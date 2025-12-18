"""
ModbusLink 数据存储模块
提供Modbus服务器的数据存储功能，包括线圈、离散输入、保持寄存器和输入寄存器的管理。

ModbusLink Data Store Module
Provides data storage functionality for Modbus server, including management of coils,
discrete inputs, holding registers, and input registers.
"""

from typing import List
import threading
from ..utils.logging import get_logger


class ModbusDataStore:
    """
    Modbus数据存储类
    提供线程安全的Modbus数据存储功能，支持线圈、离散输入、保持寄存器和输入寄存器的读写操作。
    
    Modbus Data Store Class
    Provides thread-safe Modbus data storage functionality, supporting read/write operations
    for coils, discrete inputs, holding registers, and input registers.
    """

    def __init__(self,
                 coils_size: int = 65536,
                 discrete_inputs_size: int = 65536,
                 holding_registers_size: int = 65536,
                 input_registers_size: int = 65536):
        """
        初始化数据存储 | Initialize Data Store
        
        Args:
            coils_size: 线圈数量 | Number of coils
            discrete_inputs_size: 离散输入数量 | Number of discrete inputs
            holding_registers_size: 保持寄存器数量 | Number of holding registers
            input_registers_size: 输入寄存器数量 | Number of input registers
        """
        self._logger = get_logger("server.data_store")
        self._lock = threading.RLock()

        # 初始化数据存储区域 | Initialize data storage areas
        self._coils: List[bool] = [False] * coils_size
        self._discrete_inputs: List[bool] = [False] * discrete_inputs_size
        self._holding_registers: List[int] = [0] * holding_registers_size
        self._input_registers: List[int] = [0] * input_registers_size

        self._logger.info(
            cn=f"数据存储初始化完成: "
               f"线圈: {coils_size}, "
               f"离散输入: {discrete_inputs_size}, "
               f"保持寄存器: {holding_registers_size}, "
               f"输入寄存器: {input_registers_size}",
            en=f"Data store initialized: "
               f"Coils: {coils_size}, "
               f"Discrete Inputs: {discrete_inputs_size}, "
               f"Holding Registers: {holding_registers_size}, "
               f"Input Registers: {input_registers_size}",
        )

    def read_coils(self, address: int, count: int) -> List[bool]:
        """
        读取线圈状态 | Read Coil Status
        
        Args:
            address: 起始地址 | Starting address
            count: 读取数量 | Number to read
            
        Returns:
            线圈状态列表 | List of coil status
            
        Raises:
            ValueError: 地址或数量无效 | Invalid address or count
        """
        with self._lock:
            if address < 0 or address >= len(self._coils):
                raise ValueError(f"线圈地址超出范围 | Coil address out of range: {address}")
            if count <= 0 or address + count > len(self._coils):
                raise ValueError(f"线圈数量无效 | Invalid coil count: {count}")

            result = self._coils[address:address + count]
            self._logger.debug(
                cn=f"读取线圈: 地址 {address}, 数量 {count}",
                en=f"Read coils: Address {address}, Count {count}"
            )
            return result

    def write_coils(self, address: int, values: List[bool]) -> None:
        """
        写入线圈状态 | Write Coil Status
        
        Args:
            address: 起始地址 | Starting address
            values: 线圈状态列表 | List of coil status
            
        Raises:
            ValueError: 地址或数据无效 | Invalid address or data
        """
        with self._lock:
            if address < 0 or address >= len(self._coils):
                raise ValueError(f"线圈地址超出范围 | Coil address out of range: {address}")
            if not values or address + len(values) > len(self._coils):
                raise ValueError(f"线圈数据无效 | Invalid coil data")

            for i, value in enumerate(values):
                self._coils[address + i] = value

            self._logger.debug(
                cn=f"写入线圈: 地址 {address}, 数量 {len(values)}",
                en=f"Write coils: Address {address}, Count {len(values)}"
            )

    def read_discrete_inputs(self, address: int, count: int) -> List[bool]:
        """
        读取离散输入状态 | Read Discrete Input Status
        
        Args:
            address: 起始地址 | Starting address
            count: 读取数量 | Number to read
            
        Returns:
            离散输入状态列表 | List of discrete input status
            
        Raises:
            ValueError: 地址或数量无效 | Invalid address or count
        """
        with self._lock:
            if address < 0 or address >= len(self._discrete_inputs):
                raise ValueError(f"离散输入地址超出范围 | Discrete input address out of range: {address}")
            if count <= 0 or address + count > len(self._discrete_inputs):
                raise ValueError(f"离散输入数量无效 | Invalid discrete input count: {count}")

            result = self._discrete_inputs[address:address + count]
            self._logger.debug(
                cn=f"读取离散输入: 地址 {address}, 数量 {count}",
                en=f"Read discrete inputs: Address {address}, Count {count}"
            )
            return result

    def write_discrete_inputs(self, address: int, values: List[bool]) -> None:
        """
        写入离散输入状态（通常用于模拟） | Write Discrete Input Status (usually for simulation)
        
        Args:
            address: 起始地址 | Starting address
            values: 离散输入状态列表 | List of discrete input status
            
        Raises:
            ValueError: 地址或数据无效 | Invalid address or data
        """
        with self._lock:
            if address < 0 or address >= len(self._discrete_inputs):
                raise ValueError(f"离散输入地址超出范围 | Discrete input address out of range: {address}")
            if not values or address + len(values) > len(self._discrete_inputs):
                raise ValueError(f"离散输入数据无效 | Invalid discrete input data")

            for i, value in enumerate(values):
                self._discrete_inputs[address + i] = value

            self._logger.debug(
                cn=f"写入离散输入: 地址 {address}, 数量 {len(values)}",
                en=f"Write discrete inputs: Address {address}, Count {len(values)}"
            )

    def read_holding_registers(self, address: int, count: int) -> List[int]:
        """
        读取保持寄存器 | Read Holding Registers
        
        Args:
            address: 起始地址 | Starting address
            count: 读取数量 | Number to read
            
        Returns:
            保持寄存器值列表 | List of holding register values
            
        Raises:
            ValueError: 地址或数量无效 | Invalid address or count
        """
        with self._lock:
            if address < 0 or address >= len(self._holding_registers):
                raise ValueError(f"保持寄存器地址超出范围 | Holding register address out of range: {address}")
            if count <= 0 or address + count > len(self._holding_registers):
                raise ValueError(f"保持寄存器数量无效 | Invalid holding register count: {count}")

            result = self._holding_registers[address:address + count]
            self._logger.debug(
                cn=f"读取保持寄存器: 地址 {address}, 数量 {count}",
                en=f"Read holding registers: Address {address}, Count {count}"
            )
            return result

    def write_holding_registers(self, address: int, values: List[int]) -> None:
        """
        写入保持寄存器 | Write Holding Registers
        
        Args:
            address: 起始地址 | Starting address
            values: 保持寄存器值列表 | List of holding register values
            
        Raises:
            ValueError: 地址或数据无效 | Invalid address or data
        """
        with self._lock:
            if address < 0 or address >= len(self._holding_registers):
                raise ValueError(f"保持寄存器地址超出范围 | Holding register address out of range: {address}")
            if not values or address + len(values) > len(self._holding_registers):
                raise ValueError(f"保持寄存器数据无效 | Invalid holding register data")

            for i, value in enumerate(values):
                if not (0 <= value <= 65535):
                    raise ValueError(f"寄存器值超出范围 | Register value out of range: {value}")
                self._holding_registers[address + i] = value

            self._logger.debug(
                cn=f"写入保持寄存器: 地址 {address}, 数量 {len(values)}",
                en=f"Write holding registers: Address {address}, Count {len(values)}"
            )

    def read_input_registers(self, address: int, count: int) -> List[int]:
        """
        读取输入寄存器 | Read Input Registers
        
        Args:
            address: 起始地址 | Starting address
            count: 读取数量 | Number to read
            
        Returns:
            输入寄存器值列表 | List of input register values
            
        Raises:
            ValueError: 地址或数量无效 | Invalid address or count
        """
        with self._lock:
            if address < 0 or address >= len(self._input_registers):
                raise ValueError(f"输入寄存器地址超出范围 | Input register address out of range: {address}")
            if count <= 0 or address + count > len(self._input_registers):
                raise ValueError(f"输入寄存器数量无效 | Invalid input register count: {count}")

            result = self._input_registers[address:address + count]
            self._logger.debug(
                cn=f"读取输入寄存器: 地址 {address}, 数量 {count}",
                en=f"Read input registers: Address {address}, Count {count}"
            )
            return result

    def write_input_registers(self, address: int, values: List[int]) -> None:
        """
        写入输入寄存器（通常用于模拟） | Write Input Registers (usually for simulation)
        
        Args:
            address: 起始地址 | Starting address
            values: 输入寄存器值列表 | List of input register values
            
        Raises:
            ValueError: 地址或数据无效 | Invalid address or data
        """
        with self._lock:
            if address < 0 or address >= len(self._input_registers):
                raise ValueError(f"输入寄存器地址超出范围 | Input register address out of range: {address}")
            if not values or address + len(values) > len(self._input_registers):
                raise ValueError(f"输入寄存器数据无效 | Invalid input register data")

            for i, value in enumerate(values):
                if not (0 <= value <= 65535):
                    raise ValueError(f"寄存器值超出范围 | Register value out of range: {value}")
                self._input_registers[address + i] = value

            self._logger.debug(
                cn=f"写入输入寄存器: 地址 {address}, 数量 {len(values)}",
                en=f"Write input registers: Address {address}, Count {len(values)}"
            )

    def get_coils_size(self) -> int:
        """获取线圈总数 | Get total number of coils"""
        return len(self._coils)

    def get_discrete_inputs_size(self) -> int:
        """获取离散输入总数 | Get total number of discrete inputs"""
        return len(self._discrete_inputs)

    def get_holding_registers_size(self) -> int:
        """获取保持寄存器总数 | Get total number of holding registers"""
        return len(self._holding_registers)

    def get_input_registers_size(self) -> int:
        """获取输入寄存器总数 | Get total number of input registers"""
        return len(self._input_registers)

    def reset(self) -> None:
        """
        重置所有数据为默认值
        
        Reset All Data to Default Values
        """
        with self._lock:
            for i in range(len(self._coils)):
                self._coils[i] = False
            for i in range(len(self._discrete_inputs)):
                self._discrete_inputs[i] = False
            for i in range(len(self._holding_registers)):
                self._holding_registers[i] = 0
            for i in range(len(self._input_registers)):
                self._input_registers[i] = 0

            self._logger.info(
                cn="数据存储已重置",
                en="Data store reset"
            )
