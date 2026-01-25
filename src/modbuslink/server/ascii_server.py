"""
ModbusLink 异步ASCII服务器实现

ModbusLink Async ASCII Server Implementation
"""

import asyncio
import struct
import binascii
from typing import Optional

from .serial_server import AsyncSerialModbusServer
from .data_store import ModbusDataStore
from ..utils.lrc import LRCModbus


class AsyncAsciiModbusServer(AsyncSerialModbusServer):
    """
    异步ASCII Modbus服务器

    实现基于串口的异步Modbus ASCII服务器。
    使用LRC校验和ASCII编码。

    Async ASCII Modbus Server

    Implements serial port-based async Modbus ASCII server.
    Uses LRC checksum and ASCII encoding.
    """

    def __init__(
            self,
            port: str,
            baudrate: int = 9600,
            bytesize: int = 7,
            parity: str = 'E',
            stopbits: int = 1,
            data_store: Optional[ModbusDataStore] = None,
            slave_id: int = 1
    ):
        """
        初始化异步ASCII Modbus服务器 | Initialize Async ASCII Modbus Server

        Args:
            port: 串口名称 | Serial port name
            baudrate: 波特率 | Baud rate
            bytesize: 数据位 | Data bits
            parity: 校验位 ('N', 'E', 'O') | Parity ('N', 'E', 'O')
            stopbits: 停止位 | Stop bits
            data_store: 数据存储实例 | Data store instance
            slave_id: 从站地址 | Slave address
        """
        super().__init__(
            port=port,
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            data_store=data_store,
            slave_id=slave_id,
            log_name="server.ascii",
            protocol_name="ASCII"
        )

        self._logger.info(
            cn=f"ASCII服务器初始化: {port}@{baudrate}",
            en=f"ASCII server initialized: {port}@{baudrate}"
        )

    async def _server_loop(self) -> None:
        """
        服务器主循环

        Server Main Loop
        """
        self._logger.info(
            cn="ASCII服务器主循环启动",
            en="ASCII server main loop started"
        )

        try:
            while self._running and self._reader:
                try:
                    # Modbus ASCII 使用 CRLF (\r\n) 作为结束符
                    # Modbus ASCII uses CRLF (\r\n) as terminator
                    line = await self._reader.readuntil(b'\r\n')

                    # 移除首尾空白字符 (CRLF)
                    line = line.strip()

                    if not line:
                        # 如果读取到空字节，可能是端口关闭或暂时无数据
                        await asyncio.sleep(0.01)
                        continue

                    # ASCII帧必须以 ':' 开头
                    # ASCII frame must start with ':'
                    if not line.startswith(b':'):
                        # 尝试寻找中间的 ':' (处理垃圾数据)
                        idx = line.find(b':')
                        if idx != -1:
                            line = line[idx:]
                        else:
                            continue  # 无效帧，丢弃

                    # 处理这一行数据
                    await self._process_frame(line)

                except asyncio.IncompleteReadError:
                    # 流被关闭或部分读取
                    if self._running:
                        await asyncio.sleep(0.1)
                    continue
                except asyncio.LimitOverrunError:
                    # 缓冲区溢出（非常长地行），可能是噪声
                    # 读取所有数据清空缓冲区
                    try:
                        await self._reader.read(1024)
                    except Exception:
                        pass
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    self._logger.error(
                        cn=f"服务器循环异常: {e}",
                        en=f"Server loop exception: {e}"
                    )
                    await asyncio.sleep(0.1)  # 短暂延迟后继续 | Brief delay before continuing

        except asyncio.CancelledError:
            self._logger.info(
                cn="ASCII服务器主循环被取消",
                en="ASCII server main loop cancelled"
            )
        except Exception as e:
            self._logger.error(
                cn=f"ASCII服务器主循环异常: {e}",
                en=f"ASCII server main loop exception: {e}"
            )
        finally:
            self._logger.info(
                cn="ASCII服务器主循环结束d",
                en="ASCII server main loop ended"
            )

    async def _process_frame(self, ascii_frame: bytes) -> None:
        """
        处理接收到的ASCII帧

        Process Received RTU Frame

        Args:
            ascii_frame: 接收到的ASCII帧 | Received RTU frame
        """
        try:
            # 移除起始符 ':' | Remove start delimiter ':'
            hex_payload = ascii_frame[1:]

            # 长度检查：长度必须是偶数（每字节两字符）
            if len(hex_payload) % 2 != 0:
                self._logger.warning(
                    cn="ASCII帧长度无效(非偶数)",
                    en="Invalid ASCII frame length (odd)"
                )
                return

            # 将Hex字符串转换为二进制数据 | Convert Hex string to binary data
            try:
                binary_frame = binascii.unhexlify(hex_payload)
            except binascii.Error:
                self._logger.warning(
                    cn="ASCII帧包含非十六进制字符",
                    en="ASCII frame contains non-hex characters"
                )
                return

            if len(binary_frame) < 2:  # 至少包含地址和LRC
                self._logger.debug(
                    cn=f"ASCII帧长度不足: {len(binary_frame)}",
                    en=f"ASCII frame length insufficient: {len(binary_frame)}"
                )
                return

            # 提取地址、PDU和LRC | Extract address, PDU and LRC
            slave_id = binary_frame[0]
            pdu = binary_frame[1:-1]
            received_lrc = binary_frame[-1:]

            # 验证LRC | Validate LRC
            calculated_lrc = LRCModbus.calculate(binary_frame[:-1])

            if received_lrc != calculated_lrc:
                self._logger.warning(
                    cn=f"LRC校验失败: 接收 0x{received_lrc.hex().upper()}, 计算 0x{calculated_lrc.hex().upper()}",
                    en=f"LRC verification failed: Received 0x{received_lrc.hex().upper()}, Calculated 0x{calculated_lrc.hex().upper()}"
                )
                return

            self._logger.debug(
                cn=f"接收到ASCII帧: 从站 {slave_id}, PDU长度: {len(pdu)}",
                en=f"Received ASCII frame: Slave {slave_id}, PDU Length: {len(pdu)}"
            )

            # 处理请求 | Process request
            response_pdu = self.process_request(slave_id, pdu)

            if response_pdu:  # 只有非广播请求才响应 | Only respond to non-broadcast requests
                # 构建响应帧 | Build response frame
                response_frame = struct.pack("B", slave_id) + response_pdu

                # 添加LRC | Add LRC
                response_frame += LRCModbus.calculate(response_frame)

                # 编码为ASCII Hex | Encoded as ASCII Hex
                response_ascii = b':' + binascii.hexlify(response_frame).upper() + b'\r\n'

                if self._writer:
                    self._writer.write(response_ascii)
                    await self._writer.drain()

                    self._logger.debug(
                        cn=f"发送ASCII响应: 从站 {slave_id}, 帧长度 {len(response_ascii)}",
                        en=f"Sent ASCII response: Slave {slave_id}, Frame Length {len(response_ascii)}"
                    )

        except Exception as e:
            self._logger.error(
                cn=f"处理ASCII帧时出错: {e}",
                en=f"Error processing ASCII frame: {e}"
            )
