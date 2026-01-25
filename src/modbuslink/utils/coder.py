"""
ModbusLink 高级数据编解码器模块

ModbusLink Advanced Data Encoder/Decoder Module
"""

import struct
from typing import List, Literal

from ..common.language import get_message

ByteOrderType = Literal["big", "little"]
WordOrderType = Literal["high", "low"]


class PayloadCoder:
    """
    高级数据编解码器类

    提供各种数据类型与Modbus寄存器之间的转换功能。
    支持不同的字节序（大端/小端）和字序（高字在前/低字在前）配置。

    Advanced Data Encoder/Decoder Class

    Provides conversion functionality between various data types and Modbus registers.
    Supports different byte order (big/little endian) and word order (high/low word first) configurations.
    """

    # 字节序常量 | Byte order constants
    BIG_ENDIAN: ByteOrderType = "big"  # 大端字节序 | Big endian byte order
    LITTLE_ENDIAN: ByteOrderType = "little"  # 小端字节序 | Little endian byte order

    # 字序常量 | Word order constants
    HIGH_WORD_FIRST: WordOrderType = "high"  # 高字在前 | High word first
    LOW_WORD_FIRST: WordOrderType = "low"  # 低字在前 | Low word first

    @staticmethod
    def _registers_to_bytes(
            registers: List[int],
            byte_order: ByteOrderType,
            word_order: WordOrderType
    ) -> bytes:
        """
        [内部]将16位寄存器整数列表转换为指定序的字节流

        [Internal] Convert the list of 16-bit register integers to a byte stream in the specified order

        - Big Endian + High Word = ABCD (Big Endian)
        - Big Endian + Low Word = CDAB (Mid-Little Endian / Byte Swap)
        - Little Endian + Low Word = DCBA (Little Endian)
        - Little Endian + High Word = BADC (Mid-Big Endian)

        Args:
            registers: 待转换的寄存器列表 | List of registers to be converted
            byte_order: 字节序(BIG_ENDIAN/LITTLE_ENDIAN) | Byte order (BIG_ENDIAN/LITTLE_ENDIAN)
            word_order: 字序(HIGH_WORD_FIRST/LOW_WORD_FIRST) | Word order (HIGH_WORD_FIRST/LOW_WORD_FIRST)

        Returns:
            转换后的拼接字节流

            The transformed and concatenated byte stream
        """
        # 复制列表以防修改原列表
        working_regs = list(registers)

        # 1. 字序处理 (Word Order Logic)
        # struct 模块对不同字节序期望的输入流顺序不同：
        # - Big Endian (>): 期望 [HighWord, LowWord]
        # - Little Endian (<): 期望 [LowWord, HighWord]
        # 因此，我们需要根据用户请求的 word_order 和 struct 期望的顺序来决定是否翻转。

        should_reverse = False
        if byte_order == PayloadCoder.BIG_ENDIAN:
            # 大端模式下，struct 期望 High First。如果用户提供的是 Low First，则需翻转。
            if word_order == PayloadCoder.LOW_WORD_FIRST:
                should_reverse = True
        else:  # LITTLE_ENDIAN
            # 小端模式下，struct 期望 Low First。如果用户提供的是 High First，则需翻转。
            if word_order == PayloadCoder.HIGH_WORD_FIRST:
                should_reverse = True

        if should_reverse:
            working_regs.reverse()

        # 2. 字节序处理并合并 (Byte Order & Merge)
        all_bytes = b""
        for reg in working_regs:
            # 确保寄存器值在 0-65535 之间
            # Ensure register is unsigned 16-bit
            safe_reg = reg & 0xFFFF
            all_bytes += safe_reg.to_bytes(2, byte_order)

        return all_bytes

    @staticmethod
    def _bytes_to_registers(
            data: bytes,
            byte_order: ByteOrderType,
            word_order: WordOrderType
    ) -> List[int]:
        """
        [内部]将字节流转回16位寄存器整数列表

        [Internal] Transfer the bytes back to a list of 16-bit register integers

        - Big Endian + High Word = ABCD (Big Endian)
        - Big Endian + Low Word = CDAB (Mid-Little Endian / Byte Swap)
        - Little Endian + Low Word = DCBA (Little Endian)
        - Little Endian + High Word = BADC (Mid-Big Endian)

        Args:
            data: 待转换的原始字节流 | The original byte stream to be converted
            byte_order: 字节序(BIG_ENDIAN/LITTLE_ENDIAN) | Byte order (BIG_ENDIAN/LITTLE_ENDIAN)
            word_order: 字序(HIGH_WORD_FIRST/LOW_WORD_FIRST) | Word order (HIGH_WORD_FIRST/LOW_WORD_FIRST)

        Returns:
            转换后的16位无符号寄存器整数列表

            The converted list of 16-bit unsigned register integers
        """
        registers = []
        # 每次取2个字节转换为一个寄存器
        # 这里转换出的寄存器顺序是 struct pack 的自然顺序：
        # - Big Endian: [HighWord, LowWord]
        # - Little Endian: [LowWord, HighWord]
        for i in range(0, len(data), 2):
            chunk = data[i: i + 2]
            reg = int.from_bytes(chunk, byte_order)
            registers.append(reg)

        # 字序处理 (Word Order Logic)
        # 根据用户期望的输出顺序进行调整
        should_reverse = False
        if byte_order == PayloadCoder.BIG_ENDIAN:
            # 自然顺序为 High First。如果用户想要 Low First，则翻转。
            if word_order == PayloadCoder.LOW_WORD_FIRST:
                should_reverse = True
        else:  # LITTLE_ENDIAN
            # 自然顺序为 Low First。如果用户想要 High First，则翻转。
            if word_order == PayloadCoder.HIGH_WORD_FIRST:
                should_reverse = True

        if should_reverse:
            return registers[::-1]

        return registers

    @staticmethod
    def decode_float32(
            registers: List[int],
            byte_order: ByteOrderType = BIG_ENDIAN,
            word_order: WordOrderType = HIGH_WORD_FIRST,
    ) -> float:
        """
        将两个16位寄存器解码为32位浮点数

        Decode two 16-bit registers to a 32-bit float

        Args:
            registers: 包含两个16位寄存器值的列表 | List containing two 16-bit register values
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            word_order: 字序，'high'或'low' | Word order, 'high' or 'low'

        Returns:
            解码后的浮点数

            Decoded float value

        Raises:
            ValueError: 当寄存器数量不为2时 | When register count is not 2
        """
        if len(registers) != 2:
            raise ValueError(get_message(
                cn="需要恰好2个寄存器来解码float32",
                en="Exactly 2 registers required for float32 decoding"
            ))

        data = PayloadCoder._registers_to_bytes(registers, byte_order, word_order)

        # struct格式: '>'代表大端, '<'代表小端 | struct format: '>' for Big Endian, '<' for Little Endian
        fmt = ">f" if byte_order == PayloadCoder.BIG_ENDIAN else "<f"
        return float(struct.unpack(fmt, data)[0])

    @staticmethod
    def encode_float32(
            value: float,
            byte_order: ByteOrderType = BIG_ENDIAN,
            word_order: WordOrderType = HIGH_WORD_FIRST
    ) -> List[int]:
        """
        将32位浮点数编码为两个16位寄存器

        Encode a 32-bit float to two 16-bit registers

        Args:
            value: 要编码的浮点数 | Float value to encode
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            word_order: 字序，'high'或'low' | Word order, 'high' or 'low'

        Returns:
            包含两个16位寄存器值的列表

            List containing two 16-bit register values
        """
        fmt = ">f" if byte_order == PayloadCoder.BIG_ENDIAN else "<f"
        packed_bytes = struct.pack(fmt, value)
        return PayloadCoder._bytes_to_registers(packed_bytes, byte_order, word_order)

    @staticmethod
    def decode_int32(
            registers: List[int],
            byte_order: ByteOrderType = BIG_ENDIAN,
            word_order: WordOrderType = HIGH_WORD_FIRST,
            signed: bool = True,
    ) -> int:
        """
        将两个16位寄存器解码为32位整数

        Decode two 16-bit registers to a 32-bit integer

        Args:
            registers: 包含两个16位寄存器值的列表 | List containing two 16-bit register values
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            word_order: 字序，'high'或'low' | Word order, 'high' or 'low'
            signed: 是否为有符号整数 | Whether it's a signed integer

        Returns:
            解码后的整数值

            Decoded integer value

        Raises:
            ValueError: 当寄存器数量不为2时 | When register count is not 2
        """
        if len(registers) != 2:
            raise ValueError(get_message(
                cn="需要恰好2个寄存器来解码int32",
                en="Exactly 2 registers required for int32 decoding"
            ))

        data = PayloadCoder._registers_to_bytes(registers, byte_order, word_order)

        # 确定struct格式字符 | Determine struct format character
        endian_char = ">" if byte_order == PayloadCoder.BIG_ENDIAN else "<"
        type_char = "i" if signed else "I"  # i=signed, I=unsigned

        return int(struct.unpack(f"{endian_char}{type_char}", data)[0])

    @staticmethod
    def encode_int32(
            value: int,
            byte_order: ByteOrderType = BIG_ENDIAN,
            word_order: WordOrderType = HIGH_WORD_FIRST,
            signed: bool = True,
    ) -> List[int]:
        """
        将32位整数编码为两个16位寄存器

        Encode a 32-bit integer to two 16-bit registers

        Args:
            value: 要编码的整数值 | Integer value to encode
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            word_order: 字序，'high'或'low' | Word order, 'high' or 'low'
            signed: 是否为有符号整数 | Whether it's a signed integer

        Returns:
            包含两个16位寄存器值的列表

            List containing two 16-bit register values
        """
        endian_char = ">" if byte_order == PayloadCoder.BIG_ENDIAN else "<"
        type_char = "i" if signed else "I"

        packed_bytes = struct.pack(f"{endian_char}{type_char}", value)
        return PayloadCoder._bytes_to_registers(packed_bytes, byte_order, word_order)

    @staticmethod
    def decode_int64(
            registers: List[int],
            byte_order: ByteOrderType = BIG_ENDIAN,
            word_order: WordOrderType = HIGH_WORD_FIRST,
            signed: bool = True,
    ) -> int:
        """
        将四个16位寄存器解码为64位整数

        Decode four 16-bit registers to a 64-bit integer

        Args:
            registers: 包含四个16位寄存器值的列表 | List containing four 16-bit register values
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            word_order: 字序，'high'或'low' | Word order, 'high' or 'low'
            signed: 是否为有符号整数 | Whether it's a signed integer

        Returns:
            解码后的整数值

            Decoded integer value

        Raises:
            ValueError: 当寄存器数量不为4时 | When register count is not 4
        """
        if len(registers) != 4:
            raise ValueError(get_message(
                cn="需要恰好4个寄存器来解码int64",
                en="Exactly 4 registers required for int64 decoding"
            ))

        data = PayloadCoder._registers_to_bytes(registers, byte_order, word_order)

        endian_char = ">" if byte_order == PayloadCoder.BIG_ENDIAN else "<"
        type_char = "q" if signed else "Q"  # q=signed long long, Q=unsigned

        return int(struct.unpack(f"{endian_char}{type_char}", data)[0])

    @staticmethod
    def encode_int64(
            value: int,
            byte_order: ByteOrderType = BIG_ENDIAN,
            word_order: WordOrderType = HIGH_WORD_FIRST,
            signed: bool = True,
    ) -> List[int]:
        """
        将64位整数编码为四个16位寄存器

        Encode a 64-bit integer to four 16-bit registers

        Args:
            value: 要编码的整数值 | Integer value to encode
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            word_order: 字序，'high'或'low' | Word order, 'high' or 'low'
            signed: 是否为有符号整数 | Whether it's a signed integer

        Returns:
            包含四个16位寄存器值的列表

            List containing four 16-bit register values
        """
        endian_char = ">" if byte_order == PayloadCoder.BIG_ENDIAN else "<"
        type_char = "q" if signed else "Q"

        packed_bytes = struct.pack(f"{endian_char}{type_char}", value)
        return PayloadCoder._bytes_to_registers(packed_bytes, byte_order, word_order)

    @staticmethod
    def decode_string(
            registers: List[int],
            byte_order: ByteOrderType = BIG_ENDIAN,
            encoding: str = "utf-8"
    ) -> str:
        """
        将寄存器解码为字符串

        Decode registers to a string

        Args:
            registers: 包含字符串数据的寄存器列表 | List of registers containing string data
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            encoding: 字符编码，默认为'utf-8' | Character encoding, default is 'utf-8'

        Returns:
            解码后的字符串（去除尾部空字符）

            Decoded string (with trailing null characters removed)
        """
        # 复用核心方法，强制 word_order 为 High First (通常字符串按顺序读取)
        # Reuse core method, force word_order to High First (strings usually read sequentially)
        all_bytes = PayloadCoder._registers_to_bytes(registers, byte_order, PayloadCoder.HIGH_WORD_FIRST)

        try:
            decoded_string = all_bytes.decode(encoding)
            # 在第一个空字符处截断，模拟C字符串行为
            # Truncate at the first null character to simulate C-string behavior
            return decoded_string.split('\x00')[0]
        except UnicodeDecodeError as e:
            raise ValueError(get_message(
                cn=f"字符串解码失败",
                en=f"String decoding failed: {e}"
            ))

    @staticmethod
    def encode_string(
            value: str,
            register_count: int,
            byte_order: ByteOrderType = BIG_ENDIAN,
            encoding: str = "utf-8",
            truncate: bool = False
    ) -> List[int]:
        """
        将字符串编码为寄存器

        Encode a string to registers

        Args:
            value: 要编码的字符串 | String to encode
            register_count: 目标寄存器数量 | Target register count
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            encoding: 字符编码，默认为'utf-8' | Character encoding, default is 'utf-8'
            truncate: 是否截断字符串 | Whether to truncate the string

        Returns:
            包含字符串数据的寄存器列表

            List of registers containing string data

        Raises:
            ValueError: 当字符串太长无法适应指定寄存器数量时 | When string is too long for specified register count
        """
        # 编码字符串为字节 | Encode string to bytes
        try:
            encoded_bytes = value.encode(encoding)
        except UnicodeEncodeError as e:
            raise ValueError(get_message(
                cn=f"字符串编码失败: {e}",
                en=f"String encoding failed: {e}"
            ))

        # 检查字节长度是否超过寄存器容量 | Check if byte length exceeds register capacity
        max_bytes = register_count * 2
        if len(encoded_bytes) > max_bytes:
            if truncate:
                encoded_bytes = encoded_bytes[:max_bytes]
            else:
                raise ValueError(get_message(
                    cn=f"字符串太长，需要{len(encoded_bytes)}字节，但只有{max_bytes}字节可用",
                    en=f"String too long, needs {len(encoded_bytes)} bytes but only {max_bytes} bytes available"
                ))

        # 填充到指定长度 | Pad to specified length
        padded_bytes = encoded_bytes.ljust(max_bytes, b"\x00")

        # 使用核心方法转换为寄存器 (字符串不需要字序反转，通常是 High First)
        # Use core method to convert to registers (Strings don't need word swap, usually High First)
        return PayloadCoder._bytes_to_registers(padded_bytes, byte_order, PayloadCoder.HIGH_WORD_FIRST)

    @staticmethod
    def decode_uint32(
            registers: List[int],
            byte_order: ByteOrderType = BIG_ENDIAN,
            word_order: WordOrderType = HIGH_WORD_FIRST,
    ) -> int:
        """
        将两个16位寄存器解码为32位无符号整数

        Decode two 16-bit registers to a 32-bit unsigned integer

        Args:
            registers: 包含两个16位寄存器值的列表 | List containing two 16-bit register values
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            word_order: 字序，'high'或'low' | Word order, 'high' or 'low'

        Returns:
            解码后的整数值

            Decoded integer value
        """
        return PayloadCoder.decode_int32(registers, byte_order, word_order, signed=False)

    @staticmethod
    def encode_uint32(
            value: int,
            byte_order: ByteOrderType = BIG_ENDIAN,
            word_order: WordOrderType = HIGH_WORD_FIRST
    ) -> List[int]:
        """
        将32位无符号整数编码为两个16位寄存器

        Encode a 32-bit unsigned integer to two 16-bit registers

        Args:
            value: 要编码的整数值 | Integer value to encode
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            word_order: 字序，'high'或'low' | Word order, 'high' or 'low'

        Returns:
            包含两个16位寄存器值的列表

            List containing two 16-bit register values
        """
        return PayloadCoder.encode_int32(value, byte_order, word_order, signed=False)

    @staticmethod
    def decode_uint64(
            registers: List[int],
            byte_order: ByteOrderType = BIG_ENDIAN,
            word_order: WordOrderType = HIGH_WORD_FIRST,
    ) -> int:
        """
        将四个16位寄存器解码为64位无符号整数

        Decode four 16-bit registers to a 64-bit unsigned integer

        Args:
            registers: 包含四个16位寄存器值的列表 | List containing four 16-bit register values
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            word_order: 字序，'high'或'low' | Word order, 'high' or 'low'

        Returns:
            解码后的整数值

            Decoded integer value

        Raises:
            ValueError: 当寄存器数量不为4时 | When register count is not 4
        """
        return PayloadCoder.decode_int64(registers, byte_order, word_order, signed=False)

    @staticmethod
    def encode_uint64(
            value: int,
            byte_order: ByteOrderType = BIG_ENDIAN,
            word_order: WordOrderType = HIGH_WORD_FIRST
    ) -> List[int]:
        """
        将64位无符号整数编码为四个16位寄存器

        Encode a 64-bit unsigned integer to four 16-bit registers

        Args:
            value: 要编码的整数值 | Integer value to encode
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            word_order: 字序，'high'或'low' | Word order, 'high' or 'low'

        Returns:
            包含四个16位寄存器值的列表

            List containing four 16-bit register values
        """
        return PayloadCoder.encode_int64(value, byte_order, word_order, signed=False)
