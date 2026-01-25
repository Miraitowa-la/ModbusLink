"""
ModbusLink 数据存储模块

ModbusLink Data Store Module
"""

import threading
from typing import List, Any, Dict, Callable

from ..common.language import get_message
from ..common.logging import get_logger

# 定义回调函数类型 | Define the callback function type: (address, values) -> None
CallbackType = Callable[[int, List[Any]], None]


class ModbusDataStore:
    """
    Modbus数据存储类
    提供线程安全的Modbus数据存储功能，支持线圈、离散输入、保持寄存器和输入寄存器的读写操作。

    Modbus Data Store Class
    Provides thread-safe Modbus data storage functionality, supporting read/write operations for coils, discrete inputs, holding registers, and input registers.
    """

    def __init__(
            self,
            coils_size: int = 65536,
            discrete_inputs_size: int = 65536,
            holding_registers_size: int = 65536,
            input_registers_size: int = 65536
    ):
        """
        初始化数据存储

        Initialize Data Store
        
        Args:
            coils_size: 线圈数量 | Number of coils
            discrete_inputs_size: 离散输入数量 | Number of discrete inputs
            holding_registers_size: 保持寄存器数量 | Number of holding registers
            input_registers_size: 输入寄存器数量 | Number of input registers
        """
        self._logger = get_logger("server.data_store")
        self._rlock = threading.RLock()

        # 初始化数据存储区域 | Initialize data storage areas
        self._coils: List[bool] = [False] * coils_size
        self._discrete_inputs: List[bool] = [False] * discrete_inputs_size
        self._holding_registers: List[int] = [0] * holding_registers_size
        self._input_registers: List[int] = [0] * input_registers_size

        # 回调存储 { 'coils': [func1, func2], ... }
        self._callbacks: Dict[str, List[CallbackType]] = {
            'coils': [],
            'discrete_inputs': [],
            'holding_registers': [],
            'input_registers': []
        }

        self._logger.info(
            cn=f"数据存储初始化完成: {coils_size}线圈, {discrete_inputs_size}离散输入, {holding_registers_size}保持寄存器, {input_registers_size}输入寄存器",
            en=f"Data store initialized: Coils:{coils_size}, Discrete:{discrete_inputs_size}, Holding:{holding_registers_size}, Input:{holding_registers_size}",
        )

    @staticmethod
    def _validate_range(address: int, count: int, max_size: int, type_name: str) -> None:
        """
        [内部]验证地址范围是否有效

        [Internal] Validate if address range is valid

        Args:
            address: 起始地址 | Starting address
            count: 请求的数量 | Requested count
            max_size: 数据区的最大容量 | Maximum size of the data area
            type_name: 数据区名称（用于生成错误消息） | Data area name (used for generating error messages)

        Raises:
            ValueError: 如果地址为负数或超出范围 | If address is negative or out of range
        """
        # 检查起始地址 | Check starting address
        if address < 0 or address >= max_size:
            raise ValueError(get_message(
                cn=f"{type_name}地址超出范围: {address} (最大: {max_size - 1})",
                en=f"{type_name} address out of range: {address} (Max: {max_size - 1})"
            ))

        # 检查数量及结束地址 | Check count and end address
        if count <= 0 or address + count > max_size:
            raise ValueError(get_message(
                cn=f"{type_name}请求数量无效或超出范围: {count} (起始: {address}, 剩余可用: {max_size - address})",
                en=f"Invalid {type_name} count or out of range: {count} (Start: {address}, Available: {max_size - address})"
            ))

    def _trigger_callbacks(self, area_name: str, address: int, values: List[Any]) -> None:
        """
        [内部]安全地触发指定区域的回调函数

        [Internal]Safely trigger callback functions for specified area

        Args:
            area_name: 数据区名称 | Data area name -> ('coils', 'discrete_inputs', 'holding_registers', 'input_registers')
            address: 数据变更的起始地址 | Starting address of data change
            values: 写入的新值列表 | List of new values written
        """
        callbacks = self._callbacks.get(area_name)
        if not callbacks:
            return

        area_name_map = {
            "coils": get_message("线圈", "Coils"),
            "discrete_inputs": get_message("离散输入", "Discrete Inputs"),
            "holding_registers": get_message("保持寄存器", "Holding Registers"),
            "input_registers": get_message("输入寄存器", "Input Registers")
        }
        friendly_name = area_name_map.get(area_name, area_name)

        for callback in callbacks:
            try:
                callback(address, values)
            except Exception as e:
                # 记录回调执行错误，但不中断程序运行
                # Log callback execution error but do not interrupt program execution
                self._logger.error(
                    cn=f"执行 {friendly_name} 回调函数失败: {e}",
                    en=f"Failed to execute {friendly_name} callback: {e}"
                )

    def add_callback(self, area_name: str, callback: Callable[[int, List[Any]], None]) -> None:
        """
        添加数据变更监视回调函数（回调函数应尽量轻量，不要包含阻塞操作）

        Add data change monitoring callback function (callback function should be light-weight, no blocking operations)

        Args:
            area_name: 要监视的数据区名称 | Data area name to monitor -> ('coils', 'discrete_inputs', 'holding_registers', 'input_registers')
            callback: 回调函数对象 | Callback function object -> [(address: int, values: List) -> None]

        Raises:
            ValueError: 如果提供的 area_name 无效 | If the provided area_name is invalid
        """
        if area_name not in self._callbacks:
            valid_names = ", ".join(self._callbacks.keys())
            raise ValueError(get_message(
                cn=f"无效的数据区名称: {area_name}。必须是: {valid_names}",
                en=f"Invalid data area name: {area_name}. Must be: {valid_names}"
            ))

        with self._rlock:
            self._callbacks[area_name].append(callback)

        self._logger.debug(
            cn=f"已添加回调监视: {area_name}",
            en=f"Added callback monitor: {area_name}"
        )

    def read_coils(self, address: int, count: int) -> List[bool]:
        """
        读取线圈状态

        Read Coil Status

        Args:
            address: 起始地址 | Starting address
            count: 读取数量 | Number to read

        Returns:
            线圈状态列表

            List of coil status

        Raises:
            ValueError: 地址或数量无效 | Invalid address or count
        """
        with self._rlock:
            self._validate_range(address, count, len(self._coils), get_message("线圈", "Coils"))
            self._logger.debug(
                cn=f"读取线圈: 地址 {address}, 数量 {count}",
                en=f"Read coils: Address {address}, Count {count}"
            )
            return self._coils[address:address + count]

    def write_coils(self, address: int, values: List[bool]) -> None:
        """
        写入线圈状态

        Write Coil Status

        Args:
            address: 起始地址 | Starting address
            values: 线圈状态列表 | List of coil status

        Raises:
            ValueError: 地址或数据无效 | Invalid address or data
        """
        with self._rlock:
            self._validate_range(address, len(values), len(self._coils), get_message("线圈", "Coils"))
            self._coils[address: address + len(values)] = values
            self._logger.debug(
                cn=f"写入线圈: 地址 {address}, 数量 {len(values)}",
                en=f"Write coils: Address {address}, Count {len(values)}"
            )
            self._trigger_callbacks('coils', address, values)

    def read_discrete_inputs(self, address: int, count: int) -> List[bool]:
        """
        读取离散输入状态

        Read Discrete Input Status

        Args:
            address: 起始地址 | Starting address
            count: 读取数量 | Number to read

        Returns:
            离散输入状态列表

            List of discrete input status

        Raises:
            ValueError: 地址或数量无效 | Invalid address or count
        """
        with self._rlock:
            self._validate_range(address, count, len(self._discrete_inputs), "Discrete Inputs")
            self._logger.debug(
                cn=f"读取离散输入: 地址 {address}, 数量 {count}",
                en=f"Read discrete inputs: Address {address}, Count {count}"
            )
            return self._discrete_inputs[address:address + count]

    def write_discrete_inputs(self, address: int, values: List[bool]) -> None:
        """
        写入离散输入状态（通常用于模拟）

        Write Discrete Input Status (usually for simulation)

        Args:
            address: 起始地址 | Starting address
            values: 离散输入状态列表 | List of discrete input status

        Raises:
            ValueError: 地址或数据无效 | Invalid address or data
        """
        with self._rlock:
            self._validate_range(address, len(values), len(self._discrete_inputs), "Discrete Inputs")
            self._discrete_inputs[address: address + len(values)] = values
            self._logger.debug(
                cn=f"写入离散输入: 地址 {address}, 数量 {len(values)}",
                en=f"Write discrete inputs: Address {address}, Count {len(values)}"
            )
            self._trigger_callbacks('discrete_inputs', address, values)

    def read_holding_registers(self, address: int, count: int) -> List[int]:
        """
        读取保持寄存器

        Read Holding Registers

        Args:
            address: 起始地址 | Starting address
            count: 读取数量 | Number to read

        Returns:
            保持寄存器值列表

            List of holding register values

        Raises:
            ValueError: 地址或数量无效 | Invalid address or count
        """
        with self._rlock:
            self._validate_range(address, count, len(self._holding_registers), "Holding Registers")
            self._logger.debug(
                cn=f"读取保持寄存器: 地址 {address}, 数量 {count}",
                en=f"Read holding registers: Address {address}, Count {count}"
            )
            return self._holding_registers[address:address + count]

    def write_holding_registers(self, address: int, values: List[int]) -> None:
        """
        写入保持寄存器

        Write Holding Registers

        Args:
            address: 起始地址 | Starting address
            values: 保持寄存器值列表 | List of holding register values

        Raises:
            ValueError: 地址或数据无效 | Invalid address or data
        """
        # 预先检查数值范围
        if any(not (0 <= v <= 65535) for v in values):
            raise ValueError(get_message(
                cn="存在超出范围的寄存器值 (0-65535)",
                en="Register value out of range (0-65535)"
            ))

        with self._rlock:
            self._validate_range(address, len(values), len(self._holding_registers), "Holding Registers")
            self._holding_registers[address: address + len(values)] = values
            self._logger.debug(
                cn=f"写入保持寄存器: 地址 {address}, 数量 {len(values)}",
                en=f"Write holding registers: Address {address}, Count {len(values)}"
            )
            self._trigger_callbacks('holding_registers', address, values)

    def read_input_registers(self, address: int, count: int) -> List[int]:
        """
        读取输入寄存器

        Read Input Registers

        Args:
            address: 起始地址 | Starting address
            count: 读取数量 | Number to read

        Returns:
            输入寄存器值列表

            List of input register values

        Raises:
            ValueError: 地址或数量无效 | Invalid address or count
        """
        with self._rlock:
            self._validate_range(address, count, len(self._input_registers), "Input Registers")
            self._logger.debug(
                cn=f"读取输入寄存器: 地址 {address}, 数量 {count}",
                en=f"Read input registers: Address {address}, Count {count}"
            )
            return self._input_registers[address:address + count]

    def write_input_registers(self, address: int, values: List[int]) -> None:
        """
        写入输入寄存器（通常用于模拟）

        Write Input Registers (usually for simulation)

        Args:
            address: 起始地址 | Starting address
            values: 输入寄存器值列表 | List of input register values

        Raises:
            ValueError: 地址或数据无效 | Invalid address or data
        """
        if any(not (0 <= v <= 65535) for v in values):
            raise ValueError(get_message(
                cn="存在超出范围的寄存器值 (0-65535)",
                en="Register value out of range (0-65535)"
            ))

        with self._rlock:
            self._validate_range(address, len(values), len(self._input_registers), "Input Registers")
            self._input_registers[address: address + len(values)] = values
            self._logger.debug(
                cn=f"写入输入寄存器: 地址 {address}, 数量 {len(values)}",
                en=f"Write input registers: Address {address}, Count {len(values)}"
            )
            self._trigger_callbacks('input_registers', address, values)

    def get_coils_size(self) -> int:
        """
        获取线圈总数

        Get total number of coils
        """
        return len(self._coils)

    def get_discrete_inputs_size(self) -> int:
        """
        获取离散输入总数

        Get total number of discrete inputs
        """
        return len(self._discrete_inputs)

    def get_holding_registers_size(self) -> int:
        """
        获取保持寄存器总数

        Get total number of holding registers
        """
        return len(self._holding_registers)

    def get_input_registers_size(self) -> int:
        """
        获取输入寄存器总数

        Get total number of input registers
        """
        return len(self._input_registers)

    def reset(self) -> None:
        """
        重置所有数据为默认值

        Reset All Data to Default Values
        """
        with self._rlock:
            self._coils[:] = [False] * len(self._coils)
            self._discrete_inputs[:] = [False] * len(self._discrete_inputs)
            self._holding_registers[:] = [0] * len(self._holding_registers)
            self._input_registers[:] = [0] * len(self._input_registers)

            self._logger.info(
                cn="数据存储已重置",
                en="Data store reset"
            )
