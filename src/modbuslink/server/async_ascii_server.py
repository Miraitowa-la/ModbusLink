"""
ModbusLink 异步ASCII服务器实现
提供基于串口的异步Modbus ASCII服务器功能。

ModbusLink Async ASCII Server Implementation
Provides serial port-based async Modbus ASCII server functionality.
"""

import asyncio
import struct
from typing import Optional
import serial_asyncio
from .async_base_server import AsyncBaseModbusServer
from .data_store import ModbusDataStore
from ..common.exceptions import ConnectionError
from ..utils.logging import get_logger


class AsyncAsciiModbusServer(AsyncBaseModbusServer):
    """
    异步ASCII Modbus服务器
    实现基于串口的异步Modbus ASCII服务器。
    使用LRC（纵向冗余校验）确保数据完整性。
    
    Async ASCII Modbus Server
    Implements serial port-based async Modbus ASCII server.
    Uses LRC (Longitudinal Redundancy Check) to ensure data integrity.
    """

    def __init__(self,
                 port: str,
                 baudrate: int = 9600,
                 bytesize: int = 7,
                 parity: str = 'E',
                 stopbits: int = 1,
                 timeout: float = 1.0,
                 data_store: Optional[ModbusDataStore] = None,
                 slave_id: int = 1):
        """
        初始化异步ASCII Modbus服务器 | Initialize Async ASCII Modbus Server
        
        Args:
            port: 串口名称 | Serial port name
            baudrate: 波特率 | Baud rate
            bytesize: 数据位 | Data bits
            parity: 校验位 ('N', 'E', 'O') | Parity ('N', 'E', 'O')
            stopbits: 停止位 | Stop bits
            timeout: 超时时间（秒） | Timeout in seconds
            data_store: 数据存储实例 | Data store instance
            slave_id: 从站地址 | Slave address
        """
        super().__init__(data_store, slave_id)
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout

        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._server_task: Optional[asyncio.Task] = None
        self._logger = get_logger("server.ascii")

        self._logger.info(
            cn=f"ASCII服务器初始化: {port}@{baudrate}",
            en=f"ASCII server initialized: {port}@{baudrate}"
        )

    async def start(self) -> None:
        """
        启动异步ASCII服务器 | Start Async ASCII Server
        
        Raises:
            ConnectionError: 当无法打开串口时 | When serial port cannot be opened
        """
        if self._running:
            self._logger.warning(
                cn="服务器已在运行",
                en="Server is already running"
            )
            return

        try:
            # 打开串口连接 | Open serial connection
            self._reader, self._writer = await serial_asyncio.open_serial_connection(
                url=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits
            )

            self._running = True

            # 启动服务器任务 | Start server task
            self._server_task = asyncio.create_task(self._server_loop())

            self._logger.info(
                cn=f"ASCII服务器启动成功: {self.port}",
                en=f"ASCII server started successfully: {self.port}"
            )

        except Exception as e:
            self._logger.error(
                cn=f"启动ASCII服务器失败: {e}",
                en=f"Failed to start ASCII server: {e}"
            )
            raise ConnectionError(
                cn=f"无法打开串口: {e}",
                en=f"Cannot open serial port: {e}"
            )

    async def stop(self) -> None:
        """停止异步ASCII服务器 | Stop Async ASCII Server"""
        if not self._running:
            self._logger.warning(
                cn="服务器未运行",
                en="Server is not running"
            )
            return

        self._running = False

        # 取消服务器任务 | Cancel server task
        if self._server_task:
            self._server_task.cancel()
            try:
                await self._server_task
            except asyncio.CancelledError:
                pass
            self._server_task = None

        # 关闭串口连接 | Close serial connection
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
            self._writer = None

        self._reader = None

        self._logger.info(
            cn="ASCII服务器已停止",
            en="ASCII server stopped"
        )

    async def is_running(self) -> bool:
        """
        检查服务器运行状态 | Check Server Running Status
        
        Returns:
            如果服务器正在运行返回True，否则返回False | True if server is running, False otherwise
        """
        return self._running and self._reader is not None and self._writer is not None

    async def _server_loop(self) -> None:
        """
        服务器主循环 | Server Main Loop
        """
        self._logger.info(
            cn="ASCII服务器主循环启动",
            en="ASCII server main loop started"
        )

        buffer = bytearray()

        try:
            while self._running and self._reader:
                try:
                    # 读取数据 | Read data
                    data = await asyncio.wait_for(
                        self._reader.read(256),
                        timeout=self.timeout
                    )

                    if not data:
                        continue

                    buffer.extend(data)

                    # 查找完整的ASCII帧 | Look for complete ASCII frame
                    while True:
                        frame = self._extract_ascii_frame(buffer)
                        if frame is None:
                            break  # 没有完整帧 | No complete frame

                        await self._process_ascii_frame(frame)

                except asyncio.TimeoutError:
                    # 超时是正常的，继续循环 | Timeout is normal, continue loop
                    continue

                except Exception as e:
                    self._logger.error(f"服务器循环异常 | Server loop exception: {e}")
                    if buffer:
                        buffer.clear()
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
                cn="ASCII服务器主循环结束",
                en="ASCII server main loop ended"
            )

    def _extract_ascii_frame(self, buffer: bytearray) -> Optional[bytes]:
        """
        从缓冲区提取完整的ASCII帧 | Extract Complete ASCII Frame from Buffer
        
        Args:
            buffer: 数据缓冲区 | Data buffer
            
        Returns:
            完整的ASCII帧，如果没有则返回None | Complete ASCII frame, None if not available
        """
        try:
            # 查找起始字符 ':' | Look for start character ':'
            start_idx = buffer.find(ord(':'))
            if start_idx == -1:
                return None

            # 查找结束字符 '\r\n' | Look for end characters '\r\n'
            end_idx = buffer.find(b'\r\n', start_idx)
            if end_idx == -1:
                return None

            # 提取完整帧 | Extract complete frame
            frame = bytes(buffer[start_idx:end_idx + 2])

            # 从缓冲区移除已处理的数据 | Remove processed data from buffer
            del buffer[:end_idx + 2]

            return frame

        except Exception as e:
            self._logger.error(
                cn=f"提取ASCII帧时出错: {e}",
                en=f"Error extracting ASCII frame: {e}"
            )
            buffer.clear()
            return None

    async def _process_ascii_frame(self, frame: bytes) -> None:
        """
        处理接收到的ASCII帧 | Process Received ASCII Frame
        
        Args:
            frame: 接收到的ASCII帧 | Received ASCII frame
        """
        try:
            # ASCII帧格式: :AABBCC...LLCRCR\r\n
            # AA = 地址, BB = 功能码, CC... = 数据, LL = LRC校验
            # AA = Address, BB = Function Code, CC... = Data, LL = LRC checksum

            if len(frame) < 9:  # 最小长度: ':' + 地址(2) + 功能码(2) + LRC(2) + '\r\n'
                self._logger.debug(
                    cn=f"ASCII帧长度不足: {len(frame)}",
                    en=f"ASCII frame length insufficient: {len(frame)}"
                )
                return

            if not frame.startswith(b':') or not frame.endswith(b'\r\n'):
                self._logger.debug(
                    cn="ASCII帧格式无效",
                    en="Invalid ASCII frame format"
                )
                return

            # 移除起始和结束字符 | Remove start and end characters
            hex_data = frame[1:-2].decode('ascii')

            if len(hex_data) % 2 != 0:
                self._logger.debug(
                    cn="ASCII帧十六进制数据长度无效",
                    en="Invalid ASCII frame hex data length"
                )
                return

            # 将十六进制字符串转换为字节 | Convert hex string to bytes
            try:
                data_bytes = bytes.fromhex(hex_data)
            except ValueError as e:
                self._logger.debug(
                    cn=f"ASCII帧十六进制数据无效: {e}",
                    en=f"Invalid ASCII frame hex data: {e}"
                )
                return

            if len(data_bytes) < 3:  # 地址 + 功能码 + LRC | Address + Function Code + LRC
                self._logger.debug(
                    cn="ASCII帧数据长度不足",
                    en="ASCII frame data length insufficient"
                )
                return

            # 提取地址、PDU和LRC | Extract address, PDU and LRC
            slave_id = data_bytes[0]
            pdu = data_bytes[1:-1]
            received_lrc = data_bytes[-1]

            # 验证LRC | Verify LRC
            calculated_lrc = self._calculate_lrc(data_bytes[:-1])
            if received_lrc != calculated_lrc:
                self._logger.warning(
                    cn=f"LRC校验失败: 接收 0x{received_lrc:02X}, 计算 0x{calculated_lrc:02X}",
                    en=f"LRC verification failed: Received 0x{received_lrc:02X}, Calculated 0x{calculated_lrc:02X}"
                )
                return

            self._logger.debug(
                cn=f"接收到ASCII帧: 从站 {slave_id}, PDU长度 {len(pdu)}",
                en=f"Received ASCII frame: Slave {slave_id}, PDU Length {len(pdu)}"
            )

            # 处理请求 | Process request
            response_pdu = self.process_request(slave_id, pdu)

            if response_pdu:  # 只有非广播请求才响应 | Only respond to non-broadcast requests
                # 构建响应帧 | Build response frame
                response_data = struct.pack("B", slave_id) + response_pdu
                response_lrc = self._calculate_lrc(response_data)
                response_data += struct.pack("B", response_lrc)

                # 转换为ASCII格式 | Convert to ASCII format
                hex_response = response_data.hex().upper()
                ascii_response = b':' + hex_response.encode('ascii') + b'\r\n'

                # 发送响应 | Send response
                if self._writer:
                    self._writer.write(ascii_response)
                    await self._writer.drain()

                    self._logger.debug(
                        cn=f"发送ASCII响应: 从站 {slave_id}, 帧长度 {len(ascii_response)}",
                        en=f"Sent ASCII response: Slave {slave_id}, Frame Length {len(ascii_response)}"
                    )

        except Exception as e:
            self._logger.error(
                cn=f"处理ASCII帧时出错: {e}",
                en=f"Error processing ASCII frame: {e}"
            )

    def _calculate_lrc(self, data: bytes) -> int:
        """
        计算LRC校验码 | Calculate LRC Checksum
        
        Args:
            data: 要计算校验码的数据 | Data to calculate checksum for
            
        Returns:
            LRC校验码 | LRC checksum
        """
        lrc = 0
        for byte in data:
            lrc += byte
        lrc = ((lrc ^ 0xFF) + 1) & 0xFF
        return lrc

    async def serve_forever(self) -> None:
        """持续运行服务器直到被停止 | Run Server Forever Until Stopped"""
        if not self._running:
            await self.start()

        if self._server_task:
            try:
                await self._server_task
            except asyncio.CancelledError:
                self._logger.info(
                    cn="服务器被取消",
                    en="Server cancelled"
                )
            except Exception as e:
                self._logger.error(
                    cn=f"服务器运行异常: {e}",
                    en=f"Server running exception: {e}"
                )
                raise
        else:
            raise ConnectionError("服务器未启动 | Server not started")
