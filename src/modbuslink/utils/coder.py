"""
ModbusLink 高级数据编解码器模块 | ModbusLink Advanced Data Encoder/Decoder Module

提供各种数据类型的编解码功能，支持不同的字节序和字序配置。
Provides encoding/decoding functionality for various data types with support for different byte order and word order configurations.
"""

import struct
from typing import List


class PayloadCoder:
    """
    高级数据编解码器类 | Advanced Data Encoder/Decoder Class

    提供各种数据类型与Modbus寄存器之间的转换功能。
    支持不同的字节序（大端/小端）和字序（高字在前/低字在前）配置。

    Provides conversion functionality between various data types and Modbus registers.
    Supports different byte order (big/little endian) and word order (high/low word first) configurations.
    """

    # 字节序常量 | Byte order constants
    BIG_ENDIAN = "big"  # 大端字节序 | Big endian byte order
    LITTLE_ENDIAN = "little"  # 小端字节序 | Little endian byte order

    # 字序常量 | Word order constants
    HIGH_WORD_FIRST = "high"  # 高字在前 | High word first
    LOW_WORD_FIRST = "low"  # 低字在前 | Low word first

    @staticmethod
    def decode_float32(
        registers: List[int],
        byte_order: str = BIG_ENDIAN,
        word_order: str = HIGH_WORD_FIRST,
    ) -> float:
        """
        将两个16位寄存器解码为32位浮点数 | Decode two 16-bit registers to a 32-bit float

        Args:
            registers: 包含两个16位寄存器值的列表 | List containing two 16-bit register values
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            word_order: 字序，'high'或'low' | Word order, 'high' or 'low'

        Returns:
            float: 解码后的浮点数 | Decoded float value

        Raises:
            ValueError: 当寄存器数量不为2时 | When register count is not 2
        """
        if len(registers) != 2:
            raise ValueError(
                "需要恰好2个寄存器来解码float32 | Exactly 2 registers required for float32 decoding"
            )

        # 根据字序排列寄存器 | Arrange registers according to word order
        if word_order == PayloadCoder.HIGH_WORD_FIRST:
            high_word, low_word = registers[0], registers[1]
        else:
            high_word, low_word = registers[1], registers[0]

        # 将寄存器值转换为字节 | Convert register values to bytes
        if byte_order == PayloadCoder.BIG_ENDIAN:
            high_bytes = high_word.to_bytes(2, "big")
            low_bytes = low_word.to_bytes(2, "big")
        else:
            high_bytes = high_word.to_bytes(2, "little")
            low_bytes = low_word.to_bytes(2, "little")

        # 组合字节并解码为浮点数 | Combine bytes and decode to float
        combined_bytes = high_bytes + low_bytes
        return float(
            struct.unpack(
                ">f" if byte_order == PayloadCoder.BIG_ENDIAN else "<f", combined_bytes
            )[0]
        )

    @staticmethod
    def encode_float32(
        value: float, byte_order: str = BIG_ENDIAN, word_order: str = HIGH_WORD_FIRST
    ) -> List[int]:
        """
        将32位浮点数编码为两个16位寄存器 | Encode a 32-bit float to two 16-bit registers

        Args:
            value: 要编码的浮点数 | Float value to encode
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            word_order: 字序，'high'或'low' | Word order, 'high' or 'low'

        Returns:
            List[int]: 包含两个16位寄存器值的列表 | List containing two 16-bit register values
        """
        # 将浮点数编码为字节 | Encode float to bytes
        packed_bytes = struct.pack(
            ">f" if byte_order == PayloadCoder.BIG_ENDIAN else "<f", value
        )

        # 提取高字和低字 | Extract high word and low word
        if byte_order == PayloadCoder.BIG_ENDIAN:
            high_word = int.from_bytes(packed_bytes[0:2], "big")
            low_word = int.from_bytes(packed_bytes[2:4], "big")
        else:
            high_word = int.from_bytes(packed_bytes[0:2], "little")
            low_word = int.from_bytes(packed_bytes[2:4], "little")

        # 根据字序返回寄存器列表 | Return register list according to word order
        if word_order == PayloadCoder.HIGH_WORD_FIRST:
            return [high_word, low_word]
        else:
            return [low_word, high_word]

    @staticmethod
    def decode_int32(
        registers: List[int],
        byte_order: str = BIG_ENDIAN,
        word_order: str = HIGH_WORD_FIRST,
        signed: bool = True,
    ) -> int:
        """
        将两个16位寄存器解码为32位整数 | Decode two 16-bit registers to a 32-bit integer

        Args:
            registers: 包含两个16位寄存器值的列表 | List containing two 16-bit register values
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            word_order: 字序，'high'或'low' | Word order, 'high' or 'low'
            signed: 是否为有符号整数 | Whether it's a signed integer

        Returns:
            int: 解码后的整数值 | Decoded integer value

        Raises:
            ValueError: 当寄存器数量不为2时 | When register count is not 2
        """
        if len(registers) != 2:
            raise ValueError(
                "需要恰好2个寄存器来解码int32 | Exactly 2 registers required for int32 decoding"
            )

        # 根据字序排列寄存器 | Arrange registers according to word order
        if word_order == PayloadCoder.HIGH_WORD_FIRST:
            high_word, low_word = registers[0], registers[1]
        else:
            high_word, low_word = registers[1], registers[0]

        # 将寄存器值转换为字节 | Convert register values to bytes
        if byte_order == PayloadCoder.BIG_ENDIAN:
            high_bytes = high_word.to_bytes(2, "big")
            low_bytes = low_word.to_bytes(2, "big")
        else:
            high_bytes = high_word.to_bytes(2, "little")
            low_bytes = low_word.to_bytes(2, "little")

        # 组合字节并解码为整数 | Combine bytes and decode to integer
        combined_bytes = high_bytes + low_bytes
        format_char = ">i" if byte_order == PayloadCoder.BIG_ENDIAN else "<i"
        if not signed:
            format_char = ">I" if byte_order == PayloadCoder.BIG_ENDIAN else "<I"

        return int(struct.unpack(format_char, combined_bytes)[0])

    @staticmethod
    def encode_int32(
        value: int,
        byte_order: str = BIG_ENDIAN,
        word_order: str = HIGH_WORD_FIRST,
        signed: bool = True,
    ) -> List[int]:
        """
        将32位整数编码为两个16位寄存器 | Encode a 32-bit integer to two 16-bit registers

        Args:
            value: 要编码的整数值 | Integer value to encode
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            word_order: 字序，'high'或'low' | Word order, 'high' or 'low'
            signed: 是否为有符号整数 | Whether it's a signed integer

        Returns:
            List[int]: 包含两个16位寄存器值的列表 | List containing two 16-bit register values
        """
        # 将整数编码为字节 | Encode integer to bytes
        format_char = ">i" if byte_order == PayloadCoder.BIG_ENDIAN else "<i"
        if not signed:
            format_char = ">I" if byte_order == PayloadCoder.BIG_ENDIAN else "<I"

        packed_bytes = struct.pack(format_char, value)

        # 提取高字和低字 | Extract high word and low word
        if byte_order == PayloadCoder.BIG_ENDIAN:
            high_word = int.from_bytes(packed_bytes[0:2], "big")
            low_word = int.from_bytes(packed_bytes[2:4], "big")
        else:
            high_word = int.from_bytes(packed_bytes[0:2], "little")
            low_word = int.from_bytes(packed_bytes[2:4], "little")

        # 根据字序返回寄存器列表 | Return register list according to word order
        if word_order == PayloadCoder.HIGH_WORD_FIRST:
            return [high_word, low_word]
        else:
            return [low_word, high_word]

    @staticmethod
    def decode_int64(
        registers: List[int],
        byte_order: str = BIG_ENDIAN,
        word_order: str = HIGH_WORD_FIRST,
        signed: bool = True,
    ) -> int:
        """
        将四个16位寄存器解码为64位整数 | Decode four 16-bit registers to a 64-bit integer

        Args:
            registers: 包含四个16位寄存器值的列表 | List containing four 16-bit register values
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            word_order: 字序，'high'或'low' | Word order, 'high' or 'low'
            signed: 是否为有符号整数 | Whether it's a signed integer

        Returns:
            int: 解码后的整数值

            Decoded integer value

        Raises:
            ValueError: 当寄存器数量不为4时

            When register count is not 4
        """
        if len(registers) != 4:
            raise ValueError(
                "需要恰好4个寄存器来解码int64 | Exactly 4 registers required for int64 decoding"
            )

        # 根据字序排列寄存器 | Arrange registers according to word order
        if word_order == PayloadCoder.HIGH_WORD_FIRST:
            ordered_registers = registers
        else:
            ordered_registers = registers[::-1]  # 反转列表 | Reverse list

        # 将所有寄存器值转换为字节 | Convert all register values to bytes
        all_bytes = b""
        for reg in ordered_registers:
            if byte_order == PayloadCoder.BIG_ENDIAN:
                all_bytes += reg.to_bytes(2, "big")
            else:
                all_bytes += reg.to_bytes(2, "little")

        # 解码为64位整数 | Decode to 64-bit integer
        format_char = ">q" if byte_order == PayloadCoder.BIG_ENDIAN else "<q"
        if not signed:
            format_char = ">Q" if byte_order == PayloadCoder.BIG_ENDIAN else "<Q"

        return int(struct.unpack(format_char, all_bytes)[0])

    @staticmethod
    def encode_int64(
        value: int,
        byte_order: str = BIG_ENDIAN,
        word_order: str = HIGH_WORD_FIRST,
        signed: bool = True,
    ) -> List[int]:
        """
        将64位整数编码为四个16位寄存器 | Encode a 64-bit integer to four 16-bit registers

        Args:
            value: 要编码的整数值 | Integer value to encode
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            word_order: 字序，'high'或'low' | Word order, 'high' or 'low'
            signed: 是否为有符号整数 | Whether it's a signed integer

        Returns:
            List[int]: 包含四个16位寄存器值的列表

            List containing four 16-bit register values
        """
        # 将整数编码为字节 | Encode integer to bytes
        format_char = ">q" if byte_order == PayloadCoder.BIG_ENDIAN else "<q"
        if not signed:
            format_char = ">Q" if byte_order == PayloadCoder.BIG_ENDIAN else "<Q"

        packed_bytes = struct.pack(format_char, value)

        # 提取四个字 | Extract four words
        registers = []
        for i in range(0, 8, 2):
            if byte_order == PayloadCoder.BIG_ENDIAN:
                word = int.from_bytes(packed_bytes[i : i + 2], "big")
            else:
                word = int.from_bytes(packed_bytes[i : i + 2], "little")
            registers.append(word)

        # 根据字序返回寄存器列表 | Return register list according to word order
        if word_order == PayloadCoder.HIGH_WORD_FIRST:
            return registers
        else:
            return registers[::-1]  # 反转列表 | Reverse list

    @staticmethod
    def decode_string(
        registers: List[int], byte_order: str = BIG_ENDIAN, encoding: str = "utf-8"
    ) -> str:
        """
        将寄存器解码为字符串 | Decode registers to a string

        Args:
            registers: 包含字符串数据的寄存器列表 | List of registers containing string data
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            encoding: 字符编码，默认为'utf-8' | Character encoding, default is 'utf-8'

        Returns:
            str: 解码后的字符串（去除尾部空字符）

            Decoded string (with trailing null characters removed)
        """
        # 将所有寄存器值转换为字节 | Convert all register values to bytes
        all_bytes = b""
        for reg in registers:
            if byte_order == PayloadCoder.BIG_ENDIAN:
                all_bytes += reg.to_bytes(2, "big")
            else:
                all_bytes += reg.to_bytes(2, "little")

        # 解码为字符串并去除尾部空字符 | Decode to string and remove trailing null characters
        try:
            decoded_string = all_bytes.decode(encoding)
            return decoded_string.rstrip(
                "\x00"
            )  # 去除尾部空字符 | Remove trailing null characters
        except UnicodeDecodeError as e:
            raise ValueError(f"字符串解码失败 | String decoding failed: {e}")

    @staticmethod
    def encode_string(
        value: str,
        register_count: int,
        byte_order: str = BIG_ENDIAN,
        encoding: str = "utf-8",
    ) -> List[int]:
        """
        将字符串编码为寄存器 | Encode a string to registers

        Args:
            value: 要编码的字符串 | String to encode
            register_count: 目标寄存器数量 | Target register count
            byte_order: 字节序，'big'或'little' | Byte order, 'big' or 'little'
            encoding: 字符编码，默认为'utf-8' | Character encoding, default is 'utf-8'

        Returns:
            List[int]: 包含字符串数据的寄存器列表

            List of registers containing string data

        Raises:
            ValueError: 当字符串太长无法适应指定寄存器数量时

            When string is too long for specified register count
        """
        # 编码字符串为字节 | Encode string to bytes
        try:
            encoded_bytes = value.encode(encoding)
        except UnicodeEncodeError as e:
            raise ValueError(f"字符串编码失败 | String encoding failed: {e}")

        # 检查字节长度是否超过寄存器容量 | Check if byte length exceeds register capacity
        max_bytes = register_count * 2
        if len(encoded_bytes) > max_bytes:
            raise ValueError(
                f"字符串太长，需要{len(encoded_bytes)}字节，但只有{max_bytes}字节可用 | String too long, needs {len(encoded_bytes)} bytes but only {max_bytes} bytes available"
            )

        # 填充到指定长度 | Pad to specified length
        padded_bytes = encoded_bytes.ljust(max_bytes, b"\x00")

        # 转换为寄存器列表 | Convert to register list
        registers = []
        for i in range(0, len(padded_bytes), 2):
            if byte_order == PayloadCoder.BIG_ENDIAN:
                word = int.from_bytes(padded_bytes[i : i + 2], "big")
            else:
                word = int.from_bytes(padded_bytes[i : i + 2], "little")
            registers.append(word)

        return registers

    @staticmethod
    def decode_uint32(
        registers: List[int],
        byte_order: str = BIG_ENDIAN,
        word_order: str = HIGH_WORD_FIRST,
    ) -> int:
        """
        将两个16位寄存器解码为32位无符号整数 | Decode two 16-bit registers to a 32-bit unsigned integer

        这是decode_int32的便捷方法，signed=False

        This is a convenience method for decode_int32 with signed=False
        """
        return PayloadCoder.decode_int32(
            registers, byte_order, word_order, signed=False
        )

    @staticmethod
    def encode_uint32(
        value: int, byte_order: str = BIG_ENDIAN, word_order: str = HIGH_WORD_FIRST
    ) -> List[int]:
        """将32位无符号整数编码为两个16位寄存器 | Encode a 32-bit unsigned integer to two 16-bit registers

        这是encode_int32的便捷方法，signed=False

        This is a convenience method for encode_int32 with signed=False
        """
        return PayloadCoder.encode_int32(value, byte_order, word_order, signed=False)

    @staticmethod
    def decode_uint64(
        registers: List[int],
        byte_order: str = BIG_ENDIAN,
        word_order: str = HIGH_WORD_FIRST,
    ) -> int:
        """
        将四个16位寄存器解码为64位无符号整数 | Decode four 16-bit registers to a 64-bit unsigned integer

        这是decode_int64的便捷方法，signed=False

        This is a convenience method for decode_int64 with signed=False
        """
        return PayloadCoder.decode_int64(
            registers, byte_order, word_order, signed=False
        )

    @staticmethod
    def encode_uint64(
        value: int, byte_order: str = BIG_ENDIAN, word_order: str = HIGH_WORD_FIRST
    ) -> List[int]:
        """
        将64位无符号整数编码为四个16位寄存器 | Encode a 64-bit unsigned integer to four 16-bit registers

        这是encode_int64的便捷方法，signed=False

        This is a convenience method for encode_int64 with signed=False
        """
        return PayloadCoder.encode_int64(value, byte_order, word_order, signed=False)
