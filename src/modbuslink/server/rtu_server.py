"""
ModbusLink 异步RTU服务器实现

ModbusLink Async RTU Server Implementation
"""

import asyncio
import struct
from typing import Optional

from .serial_server import AsyncSerialModbusServer
from .data_store import ModbusDataStore
from ..utils.crc import CRC16Modbus


class AsyncRtuModbusServer(AsyncSerialModbusServer):
    """
    异步RTU Modbus服务器

    实现基于串口的异步Modbus RTU服务器。
    使用CRC16校验确保数据完整性。

    Async RTU Modbus Server

    Implements serial port-based async Modbus RTU server.
    Uses CRC16 checksum to ensure data integrity.
    """

    def __init__(
            self,
            port: str,
            baudrate: int = 9600,
            bytesize: int = 8,
            parity: str = 'N',
            stopbits: int = 1,
            data_store: Optional[ModbusDataStore] = None,
            slave_id: int = 1
    ):
        """
        初始化异步RTU Modbus服务器

        Initialize Async RTU Modbus Server

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
            log_name="server.rtu",
            protocol_name="RTU"
        )

        # 计算字符间隔时间（3.5个字符时间） | Calculate character interval time (3.5 character times)
        self._char_time = 11.0 / baudrate  # 11位每字符（起始位+8数据位+校验位+停止位） | 11 bits per character
        self._frame_timeout = max(self._char_time * 3.5, 0.001)  # 最小1ms | Minimum 1ms

        self._logger.info(
            cn=f"RTU服务器初始化: {port}@{baudrate}, 帧超时: {self._frame_timeout:.3f}s",
            en=f"RTU server initialized: {port}@{baudrate}, Frame timeout: {self._frame_timeout:.3f}s"
        )

    async def _server_loop(self) -> None:
        """
        服务器主循环

        Server Main Loop
        """
        self._logger.info(
            cn="RTU服务器主循环启动",
            en="RTU server main loop started"
        )

        buffer = bytearray()

        try:
            while self._running and self._reader:
                try:
                    # 1. 等待第一块数据 (无超时或长超时，取决于业务需求)
                    # 1. Wait for the first chunk of data
                    # serial_asyncio 的 read 会尽可能多地读取缓冲区的数据，最大为指定字节数
                    data = await self._reader.read(1024)

                    if not data:
                        # 如果读取到空字节，可能是端口关闭或暂时无数据
                        await asyncio.sleep(0.01)
                        continue

                    buffer.extend(data)

                    # 2. 累积读取：只要在帧超时时间内有新数据，就一直读
                    # 2. Accumulate read: Keep reading as long as new data arrives within frame timeout
                    while True:
                        try:
                            # 尝试在静默时间内读取更多数据 (Modbus RTU 3.5字符时间)
                            # Try to read more data within the silence interval
                            more_data = await asyncio.wait_for(
                                self._reader.read(1024),
                                timeout=self._frame_timeout
                            )
                            if more_data:
                                buffer.extend(more_data)
                            else:
                                # 读到空数据，退出内层循环进行处理
                                break
                        except asyncio.TimeoutError:
                            # 超时意味着静默时间已到，认定帧结束
                            # Timeout means silence interval reached, frame end detected
                            break
                        except Exception:
                            # 其他读取错误，中断累积
                            break

                    # 3. 处理完整帧
                    # 3. Process complete frame
                    if len(buffer) > 0:
                        # 转换为 bytes 传递，防止引用被修改
                        await self._process_frame(bytes(buffer))

                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    self._logger.error(
                        cn=f"RTU循环处理异常: {e}",
                        en=f"RTU loop processing exception: {e}"
                    )
                    await asyncio.sleep(0.1)  # 出错后短暂暂停防止死循环耗尽CPU
                finally:
                    # 无论成功与否，清空缓冲区准备下一帧
                    # Clear buffer for the next frame regardless of success or failure
                    buffer.clear()

        except asyncio.CancelledError:
            self._logger.info(
                cn="RTU服务器主循环被取消",
                en="RTU server main loop cancelled"
            )
        except Exception as e:
            self._logger.error(
                cn=f"RTU服务器主循环异常: {e}",
                en=f"RTU server main loop exception: {e}"
            )
        finally:
            self._logger.info(
                cn="RTU服务器主循环结束",
                en="RTU server main loop ended"
            )

    async def _process_frame(self, frame: bytes) -> None:
        """
        处理接收到的RTU帧

        Process Received RTU Frame

        Args:
            frame: 接收到的RTU帧 | Received RTU frame
        """
        try:
            if len(frame) < 4:
                self._logger.debug(
                    cn=f"帧长度不足: {len(frame)}",
                    en=f"Frame length insufficient: {len(frame)}"
                )
                return

            # 提取地址、PDU和CRC | Extract address, PDU and CRC
            slave_id = frame[0]
            pdu = frame[1:-2]
            received_crc = frame[-2:]

            # 验证CRC | Verify CRC
            calculated_crc = CRC16Modbus.calculate(frame[:-2])
            if received_crc != calculated_crc:
                self._logger.warning(
                    cn=f"CRC校验失败: 接收 0x{received_crc.hex().upper()}, 计算 0x{calculated_crc.hex().upper()}",
                    en=f"CRC verification failed: Received 0x{received_crc.hex().upper()}, Calculated 0x{calculated_crc.hex().upper()}"
                )
                return

            self._logger.debug(
                cn=f"接收到RTU帧: 从站 {slave_id}, PDU长度 {len(pdu)}",
                en=f"Received RTU frame: Slave {slave_id}, PDU Length {len(pdu)}"
            )

            # 处理请求 | Process request
            response_pdu = self.process_request(slave_id, pdu)

            if response_pdu:  # 只有非广播请求才响应 | Only respond to non-broadcast requests
                # 构建响应帧 | Build response frame
                response_frame = struct.pack("B", slave_id) + response_pdu
                response_frame += CRC16Modbus.calculate(response_frame)

                # 发送响应 | Send response
                if self._writer:
                    self._writer.write(response_frame)
                    await self._writer.drain()

                    self._logger.debug(
                        cn=f"发送RTU响应: 从站 {slave_id}, 帧长度 {len(response_frame)}",
                        en=f"Sent RTU response: Slave {slave_id}, Frame Length {len(response_frame)}"
                    )

        except Exception as e:
            self._logger.error(
                cn=f"处理RTU帧时出错: {e}",
                en=f"Error processing RTU frame: {e}"
            )
