"""
ModbusLink 异步RTU服务器实现
提供基于串口的异步Modbus RTU服务器功能。

ModbusLink Async RTU Server Implementation
Provides serial port-based async Modbus RTU server functionality.
"""

import asyncio
import struct
from typing import Optional
import serial_asyncio
from .async_base_server import AsyncBaseModbusServer
from .data_store import ModbusDataStore
from ..common.exceptions import ConnectionError
from ..utils.crc import CRC16Modbus
from ..utils.logging import get_logger


class AsyncRtuModbusServer(AsyncBaseModbusServer):
    """
    异步RTU Modbus服务器
    实现基于串口的异步Modbus RTU服务器。
    使用CRC16校验确保数据完整性。
    
    Async RTU Modbus Server
    Implements serial port-based async Modbus RTU server.
    Uses CRC16 checksum to ensure data integrity.
    """

    def __init__(self,
                 port: str,
                 baudrate: int = 9600,
                 bytesize: int = 8,
                 parity: str = 'N',
                 stopbits: int = 1,
                 timeout: float = 1.0,
                 data_store: Optional[ModbusDataStore] = None,
                 slave_id: int = 1):
        """
        初始化异步RTU Modbus服务器 | Initialize Async RTU Modbus Server
        
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
        self._logger = get_logger("server.rtu")

        # 计算字符间隔时间（3.5个字符时间） | Calculate character interval time (3.5 character times)
        self._char_time = 11.0 / baudrate  # 11位每字符（起始位+8数据位+校验位+停止位） | 11 bits per character
        self._frame_timeout = max(self._char_time * 3.5, 0.001)  # 最小1ms | Minimum 1ms

        self._logger.info(
            f"RTU服务器初始化 | RTU server initialized: {port}@{baudrate}, 帧超时 | Frame timeout: {self._frame_timeout:.3f}s")

    async def start(self) -> None:
        """
        启动异步RTU服务器 | Start Async RTU Server
        
        Raises:
            ConnectionError: 当无法打开串口时 | When serial port cannot be opened
        """
        if self._running:
            self._logger.warning("服务器已在运行 | Server is already running")
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

            self._logger.info(f"RTU服务器启动成功 | RTU server started successfully: {self.port}")

        except Exception as e:
            self._logger.error(f"启动RTU服务器失败 | Failed to start RTU server: {e}")
            raise ConnectionError(f"无法打开串口 | Cannot open serial port: {e}")

    async def stop(self) -> None:
        """停止异步RTU服务器 | Stop Async RTU Server"""
        if not self._running:
            self._logger.warning("服务器未运行 | Server is not running")
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

        self._logger.info("RTU服务器已停止 | RTU server stopped")

    async def is_running(self) -> bool:
        """
        检查服务器运行状态 | Check Server Running Status
        
        Returns:
            如果服务器正在运行返回True，否则返回False | True if server is running, False otherwise
        """
        return self._running and self._reader is not None and self._writer is not None

    async def _server_loop(self) -> None:
        """服务器主循环 | Server Main Loop"""
        self._logger.info("RTU服务器主循环启动 | RTU server main loop started")

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

                    # 等待帧间隔 | Wait for frame interval
                    await asyncio.sleep(self._frame_timeout)

                    # 检查是否还有更多数据 | Check if there's more data
                    try:
                        additional_data = await asyncio.wait_for(
                            self._reader.read(256),
                            timeout=self._frame_timeout
                        )
                        if additional_data:
                            buffer.extend(additional_data)
                            continue  # 继续读取 | Continue reading
                    except asyncio.TimeoutError:
                        pass  # 没有更多数据，处理当前帧 | No more data, process current frame

                    # 处理完整帧 | Process complete frame
                    if len(buffer) >= 4:  # 最小帧长度：地址+功能码+CRC | Minimum frame length: address + function code + CRC
                        await self._process_frame(bytes(buffer))

                    buffer.clear()

                except asyncio.TimeoutError:
                    # 超时是正常的，继续循环 | Timeout is normal, continue loop
                    if buffer:
                        buffer.clear()
                    continue

                except Exception as e:
                    self._logger.error(f"服务器循环异常 | Server loop exception: {e}")
                    if buffer:
                        buffer.clear()
                    await asyncio.sleep(0.1)  # 短暂延迟后继续 | Brief delay before continuing

        except asyncio.CancelledError:
            self._logger.info("RTU服务器主循环被取消 | RTU server main loop cancelled")
        except Exception as e:
            self._logger.error(f"RTU服务器主循环异常 | RTU server main loop exception: {e}")
        finally:
            self._logger.info("RTU服务器主循环结束 | RTU server main loop ended")

    async def _process_frame(self, frame: bytes) -> None:
        """
        处理接收到的RTU帧 | Process Received RTU Frame
        
        Args:
            frame: 接收到的RTU帧 | Received RTU frame
        """
        try:
            if len(frame) < 4:
                self._logger.debug(f"帧长度不足 | Frame length insufficient: {len(frame)}")
                return

            # 提取地址、PDU和CRC | Extract address, PDU and CRC
            slave_id = frame[0]
            pdu = frame[1:-2]
            received_crc = struct.unpack("<H", frame[-2:])[0]  # RTU使用小端序CRC | RTU uses little-endian CRC

            # 验证CRC | Verify CRC
            calculated_crc = CRC16Modbus.crc16_to_int(frame[:-2])
            if received_crc != calculated_crc:
                self._logger.warning(
                    f"CRC校验失败 | CRC verification failed: 接收 | Received 0x{received_crc:04X}, 计算 | Calculated 0x{calculated_crc:04X}")
                return

            self._logger.debug(
                f"接收到RTU帧 | Received RTU frame: 从站 | Slave {slave_id}, PDU长度 | PDU Length {len(pdu)}")

            # 处理请求 | Process request
            response_pdu = self.process_request(slave_id, pdu)

            if response_pdu:  # 只有非广播请求才响应 | Only respond to non-broadcast requests
                # 构建响应帧 | Build response frame
                response_frame = struct.pack("B", slave_id) + response_pdu
                response_crc = CRC16Modbus.crc16_to_int(response_frame)
                response_frame += struct.pack("<H", response_crc)

                # 发送响应 | Send response
                if self._writer:
                    self._writer.write(response_frame)
                    await self._writer.drain()

                    self._logger.debug(
                        f"发送RTU响应 | Sent RTU response: 从站 | Slave {slave_id}, 帧长度 | Frame Length {len(response_frame)}")

        except Exception as e:
            self._logger.error(f"处理RTU帧时出错 | Error processing RTU frame: {e}")

    async def serve_forever(self) -> None:
        """持续运行服务器直到被停止 | Run Server Forever Until Stopped"""
        if not self._running:
            await self.start()

        if self._server_task:
            try:
                await self._server_task
            except asyncio.CancelledError:
                self._logger.info("服务器被取消 | Server cancelled")
            except Exception as e:
                self._logger.error(f"服务器运行异常 | Server running exception: {e}")
                raise
        else:
            raise ConnectionError("服务器未启动 | Server not started")
