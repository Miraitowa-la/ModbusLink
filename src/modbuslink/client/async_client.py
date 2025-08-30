"""
ModbusLink 异步客户端实现
提供用户友好的异步Modbus客户端API。

ModbusLink Asynchronous Client Implementation
Provides user-friendly asynchronous Modbus client API.
"""

import struct
from typing import List, Optional, Callable, Any
from typing_extensions import Self
import asyncio
from ..transport.async_base import AsyncBaseTransport
from ..common.exceptions import InvalidResponseError
from ..utils.coder import PayloadCoder
from ..utils.logging import get_logger


class AsyncModbusClient:
    """
    异步Modbus客户端
    提供简洁、用户友好的异步Modbus操作接口。通过依赖注入的方式接收异步传输层实例，支持异步TCP等传输方式。
    所有方法都使用Python原生数据类型（int, list等），将底层的字节操作完全封装，并支持回调机制。

    Asynchronous Modbus Client
    Provides a concise, user-friendly asynchronous Modbus operation interface. Receives
    async transport layer instances through dependency injection, supporting async
    transport methods such as async TCP.
    All methods use Python native data types (int, list, etc.),
    completely encapsulating underlying byte operations, and support callback mechanisms.
    """

    def __init__(self, transport: AsyncBaseTransport):
        """
        初始化异步Modbus客户端 | Initialize Async Modbus Client

        Args:
            transport: 异步传输层实例（AsyncTcpTransport等） | Async transport layer instance (AsyncTcpTransport, etc.)
        """
        self.transport = transport
        self._logger = get_logger("client.async")

    async def read_coils(
            self,
            slave_id: int,
            start_address: int,
            quantity: int,
            callback: Optional[Callable[[List[bool]], None]] = None,
    ) -> List[bool]:
        """
        异步读取线圈状态（功能码0x01） | Async Read Coil Status (Function Code 0x01)

        Args:
            slave_id: 从站地址 | Slave address
            start_address: 起始地址 | Starting address
            quantity: 读取数量（1-2000） | Quantity to read (1-2000)
            callback: 可选的回调函数，在收到响应后调用 | Optional callback function, called after receiving response

        Returns:
            线圈状态列表，True表示ON，False表示OFF

            List of coil status, True for ON, False for OFF
        """
        if not (1 <= quantity <= 2000):
            raise ValueError(
                "线圈数量必须在1-2000之间 | Coil quantity must be between 1-2000"
            )

        # 构建PDU：功能码 + 起始地址 + 数量 | Build PDU: function code + starting address + quantity
        pdu = struct.pack(">BHH", 0x01, start_address, quantity)

        # 异步发送请求并接收响应 | Async send request and receive response
        response_pdu = await self.transport.send_and_receive(slave_id, pdu)

        # 解析响应：功能码 + 字节数 + 数据 | Parse response: function code + byte count + data
        if len(response_pdu) < 2:
            raise InvalidResponseError(
                "响应PDU长度不足 | Response PDU length insufficient"
            )

        function_code = response_pdu[0]
        byte_count = response_pdu[1]

        if function_code != 0x01:
            raise InvalidResponseError(
                f"功能码不匹配: 期望 0x01, 收到 0x{function_code:02X} | Function code mismatch: expected 0x01, received 0x{function_code:02X}"
            )

        if len(response_pdu) != 2 + byte_count:
            raise InvalidResponseError(
                "响应数据长度不匹配 | Response data length mismatch"
            )

        # 解析线圈数据 | Parse coil data
        coil_data = response_pdu[2:]
        coils: list[bool] = []

        for byte_idx, byte_val in enumerate(coil_data):
            for bit_idx in range(8):
                if (
                        len(coils) >= quantity
                ):  # 只返回请求的数量 | Only return requested quantity
                    break
                coils.append(bool(byte_val & (1 << bit_idx)))

        result = coils[:quantity]

        # 如果提供了回调函数，在后台任务中调用 | If callback is provided, call it in background task
        if callback:
            asyncio.create_task(self._call_callback(callback, result))

        return result

    async def read_discrete_inputs(
            self,
            slave_id: int,
            start_address: int,
            quantity: int,
            callback: Optional[Callable[[List[bool]], None]] = None,
    ) -> List[bool]:
        """
        异步读取离散输入状态（功能码0x02） | Async Read Discrete Input Status (Function Code 0x02)

        Args:
            slave_id: 从站地址 | Slave address
            start_address: 起始地址 | Starting address
            quantity: 读取数量（1-2000） | Quantity to read (1-2000)
            callback: 可选的回调函数，在收到响应后调用 | Optional callback function, called after receiving response

        Returns:
            离散输入状态列表，True表示ON，False表示OFF

            List of discrete input status, True for ON, False for OFF
        """
        if not (1 <= quantity <= 2000):
            raise ValueError(
                "离散输入数量必须在1-2000之间 | Discrete input quantity must be between 1-2000"
            )

        # 构建PDU：功能码 + 起始地址 + 数量 | Build PDU: function code + starting address + quantity
        pdu = struct.pack(">BHH", 0x02, start_address, quantity)

        # 异步发送请求并接收响应 | Async send request and receive response
        response_pdu = await self.transport.send_and_receive(slave_id, pdu)

        # 解析响应（与读取线圈相同的格式） | Parse response (same format as reading coils)
        if len(response_pdu) < 2:
            raise InvalidResponseError(
                "响应PDU长度不足 | Response PDU length insufficient"
            )

        function_code = response_pdu[0]
        byte_count = response_pdu[1]

        if function_code != 0x02:
            raise InvalidResponseError(
                f"功能码不匹配: 期望 0x02, 收到 0x{function_code:02X} | Function code mismatch: expected 0x02, received 0x{function_code:02X}"
            )

        if len(response_pdu) != 2 + byte_count:
            raise InvalidResponseError(
                "响应数据长度不匹配 | Response data length mismatch"
            )

        # 解析离散输入数据 | Parse discrete input data
        input_data = response_pdu[2:]
        inputs: list[bool] = []

        for byte_idx, byte_val in enumerate(input_data):
            for bit_idx in range(8):
                if (
                        len(inputs) >= quantity
                ):  # 只返回请求的数量 | Only return requested quantity
                    break
                inputs.append(bool(byte_val & (1 << bit_idx)))

        result = inputs[:quantity]

        # 如果提供了回调函数，在后台任务中调用 | If callback is provided, call it in background task
        if callback:
            asyncio.create_task(self._call_callback(callback, result))

        return result

    async def read_holding_registers(
            self,
            slave_id: int,
            start_address: int,
            quantity: int,
            callback: Optional[Callable[[List[int]], None]] = None,
    ) -> List[int]:
        """
        异步读取保持寄存器（功能码0x03） | Async Read Holding Registers (Function Code 0x03)

        Args:
            slave_id: 从站地址 | Slave address
            start_address: 起始地址 | Starting address
            quantity: 读取数量（1-125） | Quantity to read (1-125)
            callback: 可选的回调函数，在收到响应后调用 | Optional callback function, called after receiving response

        Returns:
            寄存器值列表，每个值为16位无符号整数（0-65535）

            List of register values, each value is a 16-bit unsigned integer (0-65535)
        """
        if not (1 <= quantity <= 125):
            raise ValueError(
                "寄存器数量必须在1-125之间 | Register quantity must be between 1-125"
            )

        # 构建PDU：功能码 + 起始地址 + 数量 | Build PDU: function code + starting address + quantity
        pdu = struct.pack(">BHH", 0x03, start_address, quantity)

        # 异步发送请求并接收响应 | Async send request and receive response
        response_pdu = await self.transport.send_and_receive(slave_id, pdu)

        # 解析响应：功能码 + 字节数 + 数据 | Parse response: function code + byte count + data
        if len(response_pdu) < 2:
            raise InvalidResponseError(
                "响应PDU长度不足 | Response PDU length insufficient"
            )

        function_code = response_pdu[0]
        byte_count = response_pdu[1]

        if function_code != 0x03:
            raise InvalidResponseError(
                f"功能码不匹配: 期望 0x03, 收到 0x{function_code:02X} | Function code mismatch: expected 0x03, received 0x{function_code:02X}"
            )

        expected_byte_count = quantity * 2
        if byte_count != expected_byte_count:
            raise InvalidResponseError(
                f"字节数不匹配: 期望 {expected_byte_count}, 收到 {byte_count} | Byte count mismatch: expected {expected_byte_count}, received {byte_count}"
            )

        if len(response_pdu) != 2 + byte_count:
            raise InvalidResponseError(
                "响应数据长度不匹配 | Response data length mismatch"
            )

        # 解析寄存器数据 | Parse register data
        register_data = response_pdu[2:]
        registers = []

        for i in range(0, len(register_data), 2):
            register_value = struct.unpack(">H", register_data[i: i + 2])[0]
            registers.append(register_value)

        # 如果提供了回调函数，在后台任务中调用 | If callback is provided, call it in background task
        if callback:
            asyncio.create_task(self._call_callback(callback, registers))

        return registers

    async def read_input_registers(
            self,
            slave_id: int,
            start_address: int,
            quantity: int,
            callback: Optional[Callable[[List[int]], None]] = None,
    ) -> List[int]:
        """
        异步读取输入寄存器（功能码0x04） | Async Read Input Registers (Function Code 0x04)

        Args:
            slave_id: 从站地址 | Slave address
            start_address: 起始地址 | Starting address
            quantity: 读取数量（1-125） | Quantity to read (1-125)
            callback: 可选的回调函数，在收到响应后调用 | Optional callback function, called after receiving response

        Returns:
            寄存器值列表，每个值为16位无符号整数（0-65535） | List of register values, each value is a 16-bit unsigned integer (0-65535)
        """
        if not (1 <= quantity <= 125):
            raise ValueError(
                "寄存器数量必须在1-125之间 | Register quantity must be between 1-125"
            )

        # 构建PDU：功能码 + 起始地址 + 数量 | Build PDU: function code + starting address + quantity
        pdu = struct.pack(">BHH", 0x04, start_address, quantity)

        # 异步发送请求并接收响应 | Async send request and receive response
        response_pdu = await self.transport.send_and_receive(slave_id, pdu)

        # 解析响应（与读取保持寄存器相同的格式） | Parse response (same format as reading holding registers)
        if len(response_pdu) < 2:
            raise InvalidResponseError(
                "响应PDU长度不足 | Response PDU length insufficient"
            )

        function_code = response_pdu[0]
        byte_count = response_pdu[1]

        if function_code != 0x04:
            raise InvalidResponseError(
                f"功能码不匹配: 期望 0x04, 收到 0x{function_code:02X} | Function code mismatch: expected 0x04, received 0x{function_code:02X}"
            )

        expected_byte_count = quantity * 2
        if byte_count != expected_byte_count:
            raise InvalidResponseError(
                f"字节数不匹配: 期望 {expected_byte_count}, 收到 {byte_count} | Byte count mismatch: expected {expected_byte_count}, received {byte_count}"
            )

        if len(response_pdu) != 2 + byte_count:
            raise InvalidResponseError(
                "响应数据长度不匹配 | Response data length mismatch"
            )

        # 解析寄存器数据 | Parse register data
        register_data = response_pdu[2:]
        registers = []

        for i in range(0, len(register_data), 2):
            register_value = struct.unpack(">H", register_data[i: i + 2])[0]
            registers.append(register_value)

        # 如果提供了回调函数，在后台任务中调用 | If callback is provided, call it in background task
        if callback:
            asyncio.create_task(self._call_callback(callback, registers))

        return registers

    async def write_single_coil(
            self,
            slave_id: int,
            address: int,
            value: bool,
            callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        异步写单个线圈（功能码0x05） | Async Write Single Coil (Function Code 0x05)

        Args:
            slave_id: 从站地址 | Slave address
            address: 线圈地址 | Coil address
            value: 线圈值，True表示ON，False表示OFF | Coil value, True for ON, False for OFF
            callback: 可选的回调函数，在操作完成后调用 | Optional callback function, called after operation completes
        """
        # 构建PDU：功能码 + 地址 + 值 | Build PDU: function code + address + value
        coil_value = 0xFF00 if value else 0x0000
        pdu = struct.pack(">BHH", 0x05, address, coil_value)

        # 异步发送请求并接收响应 | Async send request and receive response
        response_pdu = await self.transport.send_and_receive(slave_id, pdu)

        # 验证响应（应该与请求相同） | Verify response (should be same as request)
        if response_pdu != pdu:
            raise InvalidResponseError(
                "写单个线圈响应不匹配 | Write single coil response mismatch"
            )

        # 如果提供了回调函数，在后台任务中调用 | If callback is provided, call it in background task
        if callback:
            asyncio.create_task(self._call_callback(callback, None))

    async def write_single_register(
            self,
            slave_id: int,
            address: int,
            value: int,
            callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        异步写单个寄存器（功能码0x06） | Async Write Single Register (Function Code 0x06)

        Args:
            slave_id: 从站地址 | Slave address
            address: 寄存器地址 | Register address
            value: 寄存器值（0-65535） | Register value (0-65535)
            callback: 可选的回调函数，在操作完成后调用 | Optional callback function, called after operation completes
        """
        if not (0 <= value <= 65535):
            raise ValueError(
                "寄存器值必须在0-65535之间 | Register value must be between 0-65535"
            )

        # 构建PDU：功能码 + 地址 + 值 | Build PDU: function code + address + value
        pdu = struct.pack(">BHH", 0x06, address, value)

        # 异步发送请求并接收响应 | Async send request and receive response
        response_pdu = await self.transport.send_and_receive(slave_id, pdu)

        # 验证响应（应该与请求相同） | Verify response (should be same as request)
        if response_pdu != pdu:
            raise InvalidResponseError(
                "写单个寄存器响应不匹配 | Write single register response mismatch"
            )

        # 如果提供了回调函数，在后台任务中调用 | If callback is provided, call it in background task
        if callback:
            asyncio.create_task(self._call_callback(callback, None))

    async def write_multiple_coils(
            self,
            slave_id: int,
            start_address: int,
            values: List[bool],
            callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        异步写多个线圈（功能码0x0F） | Async Write Multiple Coils (Function Code 0x0F)

        Args:
            slave_id: 从站地址 | Slave address
            start_address: 起始地址 | Starting address
            values: 线圈值列表，True表示ON，False表示OFF | List of coil values, True for ON, False for OFF
            callback: 可选的回调函数，在操作完成后调用 | Optional callback function, called after operation completes
        """
        quantity = len(values)
        if not (1 <= quantity <= 1968):
            raise ValueError(
                "线圈数量必须在1-1968之间 | Coil quantity must be between 1-1968"
            )

        # 计算需要的字节数 | Calculate required byte count
        byte_count = (quantity + 7) // 8

        # 将布尔值列表转换为字节数据 | Convert boolean list to byte data
        coil_bytes = []
        for byte_idx in range(byte_count):
            byte_val = 0
            for bit_idx in range(8):
                value_idx = byte_idx * 8 + bit_idx
                if value_idx < quantity and values[value_idx]:
                    byte_val |= 1 << bit_idx
            coil_bytes.append(byte_val)

        # 构建PDU：功能码 + 起始地址 + 数量 + 字节数 + 数据 | Build PDU: function code + starting address + quantity + byte count + data
        pdu = struct.pack(">BHHB", 0x0F, start_address, quantity, byte_count)
        pdu += bytes(coil_bytes)

        # 异步发送请求并接收响应 | Async send request and receive response
        response_pdu = await self.transport.send_and_receive(slave_id, pdu)

        # 验证响应：功能码 + 起始地址 + 数量 | Verify response: function code + starting address + quantity
        expected_response = struct.pack(">BHH", 0x0F, start_address, quantity)
        if response_pdu != expected_response:
            raise InvalidResponseError(
                "写多个线圈响应不匹配 | Write multiple coils response mismatch"
            )

        # 如果提供了回调函数，在后台任务中调用 | If callback is provided, call it in background task
        if callback:
            asyncio.create_task(self._call_callback(callback, None))

    async def write_multiple_registers(
            self,
            slave_id: int,
            start_address: int,
            values: List[int],
            callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        异步写多个寄存器（功能码0x10） | Async Write Multiple Registers (Function Code 0x10)

        Args:
            slave_id: 从站地址 | Slave address
            start_address: 起始地址 | Starting address
            values: 寄存器值列表，每个值为0-65535 | List of register values, each value 0-65535
            callback: 可选的回调函数，在操作完成后调用 | Optional callback function, called after operation completes
        """
        quantity = len(values)
        if not (1 <= quantity <= 123):
            raise ValueError(
                "寄存器数量必须在1-123之间 | Register quantity must be between 1-123"
            )

        # 验证所有值都在有效范围内 | Verify all values are within valid range
        for i, value in enumerate(values):
            if not (0 <= value <= 65535):
                raise ValueError(
                    f"寄存器值[{i}]必须在0-65535之间: {value} | Register value[{i}] must be between 0-65535: {value}"
                )

        byte_count = quantity * 2

        # 构建PDU：功能码 + 起始地址 + 数量 + 字节数 + 数据 | Build PDU: function code + starting address + quantity + byte count + data
        pdu = struct.pack(">BHHB", 0x10, start_address, quantity, byte_count)

        # 添加寄存器数据 | Add register data
        for value in values:
            pdu += struct.pack(">H", value)

        # 异步发送请求并接收响应 | Async send request and receive response
        response_pdu = await self.transport.send_and_receive(slave_id, pdu)

        # 验证响应：功能码 + 起始地址 + 数量 | Verify response: function code + starting address + quantity
        expected_response = struct.pack(">BHH", 0x10, start_address, quantity)
        if response_pdu != expected_response:
            raise InvalidResponseError(
                "写多个寄存器响应不匹配 | Write multiple registers response mismatch"
            )

        # 如果提供了回调函数，在后台任务中调用 | If callback is provided, call it in background task
        if callback:
            asyncio.create_task(self._call_callback(callback, None))

    async def _call_callback(self, callback: Callable, result: Any) -> None:
        """安全地调用回调函数 | Safely call callback function"""
        try:
            if result is None:
                callback()
            else:
                callback(result)
        except Exception as e:
            self._logger.error(
                f"回调函数执行错误 | Callback function execution error: {e}"
            )

    # 高级数据类型API | Advanced Data Type APIs

    async def read_float32(
            self,
            slave_id: int,
            start_address: int,
            byte_order: str = "big",
            word_order: str = "high",
            callback: Optional[Callable[[float], None]] = None,
    ) -> float:
        """
        异步读取32位浮点数（占用2个连续寄存器） | Async Read 32-bit float (occupies 2 consecutive registers)

        Args:
            slave_id: 从站地址 | Slave address
            start_address: 起始寄存器地址 | Starting register address
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            word_order: 字序，'high'或'low' | Word order, 'high' or 'low'
            callback: 可选的回调函数，在收到响应后调用 | Optional callback function, called after receiving response

        Returns:
            32位浮点数值 | 32-bit float value
        """
        registers = await self.read_holding_registers(slave_id, start_address, 2)
        result = PayloadCoder.decode_float32(registers, byte_order, word_order)

        # 如果提供了回调函数，在后台任务中调用 | If callback is provided, call it in background task
        if callback:
            asyncio.create_task(self._call_callback(callback, result))

        return result

    async def write_float32(
            self,
            slave_id: int,
            start_address: int,
            value: float,
            byte_order: str = "big",
            word_order: str = "high",
            callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        异步写入32位浮点数（占用2个连续寄存器） | Async Write 32-bit float (occupies 2 consecutive registers)

        Args:
            slave_id: 从站地址 | Slave address
            start_address: 起始寄存器地址 | Starting register address
            value: 要写入的浮点数值 | Float value to write
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            word_order: 字序，'high'或'low' | Word order, 'high' or 'low'
            callback: 可选的回调函数，在操作完成后调用 | Optional callback function, called after operation completes
        """
        registers = PayloadCoder.encode_float32(value, byte_order, word_order)
        await self.write_multiple_registers(
            slave_id, start_address, registers, callback
        )

    async def read_int32(
            self,
            slave_id: int,
            start_address: int,
            byte_order: str = "big",
            word_order: str = "high",
            callback: Optional[Callable[[int], None]] = None,
    ) -> int:
        """
        异步读取32位有符号整数（占用2个连续寄存器） | Async Read 32-bit signed integer (occupies 2 consecutive registers)

        Args:
            slave_id: 从站地址 | Slave address
            start_address: 起始寄存器地址 | Starting register address
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            word_order: 字序，'high'或'low' | Word order, 'high' or 'low'
            callback: 可选的回调函数，在收到响应后调用 | Optional callback function, called after receiving response

        Returns:
            32位有符号整数值 | 32-bit signed integer value
        """
        registers = await self.read_holding_registers(slave_id, start_address, 2)
        result = PayloadCoder.decode_int32(registers, byte_order, word_order)

        # 如果提供了回调函数，在后台任务中调用 | If callback is provided, call it in background task
        if callback:
            asyncio.create_task(self._call_callback(callback, result))

        return result

    async def write_int32(
            self,
            slave_id: int,
            start_address: int,
            value: int,
            byte_order: str = "big",
            word_order: str = "high",
            callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        异步写入32位有符号整数（占用2个连续寄存器） | Async Write 32-bit signed integer (occupies 2 consecutive registers)

        Args:
            slave_id: 从站地址 | Slave address
            start_address: 起始寄存器地址 | Starting register address
            value: 要写入的整数值 | Integer value to write
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            word_order: 字序，'high'或'low' | Word order, 'high' or 'low'
            callback: 可选的回调函数，在操作完成后调用 | Optional callback function, called after operation completes
        """
        registers = PayloadCoder.encode_int32(value, byte_order, word_order)
        await self.write_multiple_registers(
            slave_id, start_address, registers, callback
        )

    async def __aenter__(self) -> Self:
        """异步上下文管理器入口 | Async context manager entry"""
        await self.transport.open()
        return self

    async def __aexit__(
            self,
            exc_type: Optional[type],
            exc_val: Optional[BaseException],
            exc_tb: Optional[Any],
    ) -> None:
        """异步上下文管理器出口 | Async context manager exit"""
        await self.transport.close()
