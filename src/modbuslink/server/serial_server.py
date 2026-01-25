"""
ModbusLink 异步串口服务器基类

ModbusLink Async Serial Server Base Class
"""

import asyncio
import serial_asyncio
from typing import Optional
from abc import abstractmethod

from .base_server import AsyncBaseModbusServer
from .data_store import ModbusDataStore
from ..common.logging import get_logger
from ..common.exceptions import ConnectError


class AsyncSerialModbusServer(AsyncBaseModbusServer):
    """
    异步串口Modbus服务器基类

    封装了串口的打开、关闭、任务管理等通用逻辑。
    具体的协议处理循环由子类实现。

    Async Serial Modbus Server Base Class

    Encapsulates common logic such as opening/closing serial ports and task management.
    Specific protocol processing loops are implemented by subclasses.
    """

    def __init__(
            self,
            port: str,
            baudrate: int,
            bytesize: int,
            parity: str,
            stopbits: int,
            data_store: Optional[ModbusDataStore] = None,
            slave_id: int = 1,
            log_name: str = "server.serial",
            protocol_name: str = "Serial"
    ):
        """
        初始化异步串口服务器

        Initialize Async Serial Server

        Args:
            port: 串口名称 | Serial port name
            baudrate: 波特率 | Baud rate
            bytesize: 数据位 | Data bits
            parity: 校验位 ('N', 'E', 'O') | Parity ('N', 'E', 'O')
            stopbits: 停止位 | Stop bits
            data_store: 数据存储实例 | Data store instance
            slave_id: 从站地址 | Slave address
            log_name: 日志名称 | Log name
            protocol_name: 协议名称 | Protocol name
        """
        super().__init__(data_store, slave_id)
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits

        # 用于日志显示的协议名称 (如 "RTU", "ASCII")
        self._protocol_name = protocol_name

        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._server_task: Optional[asyncio.Task] = None
        self._logger = get_logger(log_name)

    async def start(self) -> None:
        """
        启动异步串口服务器

        Start Async Serial Server

        Raises:
            ConnectError: 当无法打开串口时 | When serial port cannot be opened
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

            # 启动服务器任务（具体逻辑由子类 _server_loop 实现）
            # Start server task (Specific logic implemented by subclass _server_loop)
            self._server_task = asyncio.create_task(self._server_loop())

            self._logger.info(
                cn=f"{self._protocol_name}服务器启动成功: {self.port}",
                en=f"{self._protocol_name} server started successfully: {self.port}"
            )

        except Exception as e:
            self._logger.error(
                cn=f"启动{self._protocol_name}服务器失败: {e}",
                en=f"Failed to start {self._protocol_name} server: {e}"
            )
            raise ConnectError(
                cn=f"无法打开串口: {e}",
                en=f"Cannot open serial port: {e}"
            )

    async def stop(self) -> None:
        """
        停止异步串口服务器

        Stop Async Serial Server
        """
        if not self._running:
            self._logger.warning(
                cn="服务器未运行",
                en="Server is not running"
            )
            return

        self._running = False
        self._logger.info(
            cn=f"正在停止{self._protocol_name}服务器...",
            en=f"Stopping {self._protocol_name} server..."
        )

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
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception:
                pass
            self._writer = None

        self._reader = None

        self._logger.info(
            cn=f"{self._protocol_name}服务器已停止",
            en=f"{self._protocol_name} server stopped"
        )

    async def is_running(self) -> bool:
        """
        检查服务器运行状态

        Check Server Running Status

        Returns:
            如果服务器正在运行返回True，否则返回False

            True if server is running, False otherwise
        """
        return self._running and self._reader is not None and self._writer is not None

    async def serve_forever(self) -> None:
        """
        持续运行服务器直到被停止

        Run Server Forever Until Stopped
        """
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
            raise ConnectError(
                cn="服务器未启动",
                en="Server not started"
            )

    @abstractmethod
    async def _server_loop(self) -> None:
        """
        服务器主循环

        必须由子类实现，用于处理具体的协议分帧逻辑。

        Server Main Loop

        Must be implemented by subclasses to handle specific protocol framing logic.
        """
        pass
