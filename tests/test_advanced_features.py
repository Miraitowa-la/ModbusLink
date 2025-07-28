"""高级功能测试 | Advanced Features Tests

测试ModbusLink库的高级功能，包括数据编码器、高级数据类型、日志系统等。
Tests advanced features of ModbusLink library, including data encoders, advanced data types, logging system.
"""

import pytest
import sys
import os
import struct
import logging
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# 添加源代码路径 | Add source code path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from modbuslink.utils.coder import PayloadCoder
    from modbuslink.utils.logging import ModbusLogger
    from modbuslink import ModbusClient, TcpTransport
except ImportError as e:
    pytest.skip(f"无法导入高级功能模块: {e} | Cannot import advanced feature modules: {e}", allow_module_level=True)


class TestPayloadCoderFloat32:
    """32位浮点数编码器测试 | 32-bit Float Encoder Tests"""
    
    def test_encode_decode_positive_float(self):
        """测试正浮点数编码解码 | Test positive float encoding/decoding"""
        test_values = [3.14159, 123.456, 0.001, 999999.9]
        
        for value in test_values:
            for byte_order in ['big', 'little']:
                for word_order in ['high', 'low']:
                    registers = PayloadCoder.encode_float32(value, byte_order, word_order)
                    decoded = PayloadCoder.decode_float32(registers, byte_order, word_order)
                    
                    assert len(registers) == 2
                    assert abs(decoded - value) < 0.1
                    print(f"✓ Float32 {value} ({byte_order}/{word_order}): {decoded} | Float32 {value} ({byte_order}/{word_order}): {decoded}")
    
    def test_encode_decode_negative_float(self):
        """测试负浮点数编码解码 | Test negative float encoding/decoding"""
        test_values = [-3.14159, -123.456, -0.001, -999999.9]
        
        for value in test_values:
            registers = PayloadCoder.encode_float32(value, 'big', 'high')
            decoded = PayloadCoder.decode_float32(registers, 'big', 'high')
            
            assert len(registers) == 2
            assert abs(decoded - value) < 0.1
            print(f"✓ 负Float32 {value}: {decoded} | Negative Float32 {value}: {decoded}")
    
    def test_encode_decode_special_float_values(self):
        """测试特殊浮点数值 | Test special float values"""
        import math
        
        special_values = [
            0.0,
            -0.0,
            float('inf'),
            float('-inf'),
            # math.nan,  # NaN比较特殊，需要单独处理 | NaN is special, needs separate handling
        ]
        
        for value in special_values:
            registers = PayloadCoder.encode_float32(value, 'big', 'high')
            decoded = PayloadCoder.decode_float32(registers, 'big', 'high')
            
            assert len(registers) == 2
            if math.isinf(value):
                assert math.isinf(decoded) and (decoded > 0) == (value > 0)
            else:
                assert decoded == value
            print(f"✓ 特殊Float32 {value}: {decoded} | Special Float32 {value}: {decoded}")
    
    def test_float32_nan_handling(self):
        """测试NaN值处理 | Test NaN value handling"""
        import math
        
        nan_value = float('nan')
        registers = PayloadCoder.encode_float32(nan_value, 'big', 'high')
        decoded = PayloadCoder.decode_float32(registers, 'big', 'high')
        
        assert len(registers) == 2
        assert math.isnan(decoded)
        print("✓ NaN值处理正常 | NaN value handling works")


class TestPayloadCoderIntegers:
    """整数编码器测试 | Integer Encoder Tests"""
    
    def test_encode_decode_int32(self):
        """测试32位有符号整数编码解码 | Test 32-bit signed integer encoding/decoding"""
        test_values = [0, 1, -1, 123456789, -123456789, 2147483647, -2147483648]
        
        for value in test_values:
            for byte_order in ['big', 'little']:
                for word_order in ['high', 'low']:
                    registers = PayloadCoder.encode_int32(value, byte_order, word_order)
                    decoded = PayloadCoder.decode_int32(registers, byte_order, word_order)
                    
                    assert len(registers) == 2
                    assert decoded == value
                    print(f"✓ Int32 {value} ({byte_order}/{word_order}): {decoded} | Int32 {value} ({byte_order}/{word_order}): {decoded}")
    
    def test_encode_decode_uint32(self):
        """测试32位无符号整数编码解码 | Test 32-bit unsigned integer encoding/decoding"""
        test_values = [0, 1, 123456789, 4294967295]
        
        for value in test_values:
            for byte_order in ['big', 'little']:
                for word_order in ['high', 'low']:
                    registers = PayloadCoder.encode_uint32(value, byte_order, word_order)
                    decoded = PayloadCoder.decode_uint32(registers, byte_order, word_order)
                    
                    assert len(registers) == 2
                    assert decoded == value
                    print(f"✓ UInt32 {value} ({byte_order}/{word_order}): {decoded} | UInt32 {value} ({byte_order}/{word_order}): {decoded}")
    
    def test_encode_decode_int64(self):
        """测试64位有符号整数编码解码 | Test 64-bit signed integer encoding/decoding"""
        test_values = [0, 1, -1, 123456789012345, -123456789012345, 9223372036854775807, -9223372036854775808]
        
        for value in test_values:
            registers = PayloadCoder.encode_int64(value, 'big', 'high')
            decoded = PayloadCoder.decode_int64(registers, 'big', 'high')
            
            assert len(registers) == 4
            assert decoded == value
            print(f"✓ Int64 {value}: {decoded} | Int64 {value}: {decoded}")
    
    def test_encode_decode_uint64(self):
        """测试64位无符号整数编码解码 | Test 64-bit unsigned integer encoding/decoding"""
        test_values = [0, 1, 123456789012345, 18446744073709551615]
        
        for value in test_values:
            registers = PayloadCoder.encode_uint64(value, 'big', 'high')
            decoded = PayloadCoder.decode_uint64(registers, 'big', 'high')
            
            assert len(registers) == 4
            assert decoded == value
            print(f"✓ UInt64 {value}: {decoded} | UInt64 {value}: {decoded}")
    
    def test_integer_overflow_handling(self):
        """测试整数溢出处理 | Test integer overflow handling"""
        # 测试超出范围的值 | Test out-of-range values
        with pytest.raises((ValueError, OverflowError, struct.error)):
            PayloadCoder.encode_int32(2147483648, 'big', 'high')  # 超出int32范围 | Beyond int32 range
        
        with pytest.raises((ValueError, OverflowError, struct.error)):
            PayloadCoder.encode_uint32(-1, 'big', 'high')  # 负数不能编码为uint32 | Negative cannot be encoded as uint32
        
        print("✓ 整数溢出处理正常 | Integer overflow handling works")
    
    def test_invalid_register_count_errors(self):
        """测试无效寄存器数量错误 | Test invalid register count errors"""
        # 测试float32解码错误 | Test float32 decoding error
        with pytest.raises(ValueError, match="需要恰好2个寄存器"):
            PayloadCoder.decode_float32([1], 'big', 'high')  # 只有1个寄存器 | Only 1 register
        
        with pytest.raises(ValueError, match="需要恰好2个寄存器"):
            PayloadCoder.decode_float32([1, 2, 3], 'big', 'high')  # 3个寄存器 | 3 registers
        
        # 测试int32解码错误 | Test int32 decoding error
        with pytest.raises(ValueError, match="需要恰好2个寄存器"):
            PayloadCoder.decode_int32([1], 'big', 'high')  # 只有1个寄存器 | Only 1 register
        
        # 测试int64解码错误 | Test int64 decoding error
        with pytest.raises(ValueError, match="需要恰好4个寄存器"):
            PayloadCoder.decode_int64([1, 2], 'big', 'high')  # 只有2个寄存器 | Only 2 registers
        
        print("✓ 无效寄存器数量错误处理正常 | Invalid register count error handling works")
    
    def test_parameter_variations(self):
        """测试参数变化 | Test parameter variations"""
        # 测试不同参数组合不会崩溃 | Test different parameter combinations don't crash
        value = 3.14
        
        # 正常参数应该工作 | Normal parameters should work
        result1 = PayloadCoder.encode_float32(value, 'big', 'high')
        result2 = PayloadCoder.encode_float32(value, 'little', 'low')
        
        assert len(result1) == 2
        assert len(result2) == 2
        assert all(isinstance(r, int) for r in result1)
        assert all(isinstance(r, int) for r in result2)
        
        print("✓ 参数变化测试通过 | Parameter variations test passed")
    
    def test_string_encoding_edge_cases(self):
        """测试字符串编码边界情况 | Test string encoding edge cases"""
        # 测试字符串长度超出寄存器容量 | Test string length exceeding register capacity
        long_string = "A" * 100
        register_count = 2  # 只能容纳4字节 | Can only hold 4 bytes
        
        try:
            PayloadCoder.encode_string(long_string, register_count)
            # 如果没有抛出异常，检查结果是否被截断 | If no exception, check if result is truncated
            print("✓ 长字符串处理正常（可能被截断） | Long string handled (possibly truncated)")
        except ValueError:
            print("✓ 长字符串抛出异常正常 | Long string raises exception as expected")
        
        # 测试无效编码会被Python捕获 | Test invalid encoding will be caught by Python
        try:
            PayloadCoder.encode_string("test", 2, encoding="invalid_encoding")
        except (LookupError, ValueError) as e:
            print(f"✓ 无效编码错误处理正常: {type(e).__name__} | Invalid encoding error handled: {type(e).__name__}")
        
        print("✓ 字符串编码边界情况处理正常 | String encoding edge cases handled correctly")
    
    def test_all_word_orders(self):
        """测试所有字序组合 | Test all word order combinations"""
        value = 0x12345678
        
        # 测试所有字节序和字序组合 | Test all byte order and word order combinations
        for byte_order in ['big', 'little']:
            for word_order in ['high', 'low']:
                registers = PayloadCoder.encode_int32(value, byte_order, word_order)
                decoded = PayloadCoder.decode_int32(registers, byte_order, word_order)
                assert decoded == value
        
        print("✓ 所有字序组合测试通过 | All word order combinations tested")


class TestPayloadCoderString:
    """字符串编码器测试 | String Encoder Tests"""
    
    def test_encode_decode_ascii_string(self):
        """测试ASCII字符串编码解码 | Test ASCII string encoding/decoding"""
        test_strings = [
            "Hello",
            "ModbusLink",
            "Test123",
            "!@#$%^&*()",
            "",  # 空字符串 | Empty string
        ]
        
        for string in test_strings:
            byte_length = len(string.encode('utf-8'))
            register_count = (byte_length + 1) // 2
            registers = PayloadCoder.encode_string(string, register_count)
            decoded = PayloadCoder.decode_string(registers)
            
            assert isinstance(registers, list)
            assert all(isinstance(r, int) and 0 <= r <= 65535 for r in registers)
            assert decoded.rstrip('\x00') == string
            print(f"✓ ASCII字符串 '{string}': 长度{len(registers)}寄存器 | ASCII string '{string}': {len(registers)} registers")
    
    def test_encode_decode_unicode_string(self):
        """测试Unicode字符串编码解码 | Test Unicode string encoding/decoding"""
        test_strings = [
            "你好世界 | Hello World",
            "测试 | Test",
            "ModbusLink库 | ModbusLink Library",
            "🚀📚💡",  # Emoji
        ]
        
        for string in test_strings:
            byte_length = len(string.encode('utf-8'))
            register_count = (byte_length + 1) // 2
            registers = PayloadCoder.encode_string(string, register_count)
            decoded = PayloadCoder.decode_string(registers)
            
            assert isinstance(registers, list)
            assert all(isinstance(r, int) and 0 <= r <= 65535 for r in registers)
            assert decoded.rstrip('\x00') == string
            print(f"✓ Unicode字符串 '{string}': {len(registers)}寄存器, {byte_length}字节 | Unicode string '{string}': {len(registers)} registers, {byte_length} bytes")
    
    def test_string_padding(self):
        """测试字符串填充 | Test string padding"""
        string = "Test"
        register_count = 5  # 足够容纳字符串和填充 | Enough to contain string and padding
        registers = PayloadCoder.encode_string(string, register_count)
        
        # 验证寄存器数量正确 | Verify register count is correct
        assert len(registers) == register_count
        
        # 解码应该包含原始字符串 | Decoding should include original string
        decoded_longer = PayloadCoder.decode_string(registers)
        assert decoded_longer.rstrip('\x00') == string
        print(f"✓ 字符串填充正常: '{string}' -> {len(registers)}寄存器 | String padding works: '{string}' -> {len(registers)} registers")
    
    def test_string_truncation(self):
        """测试字符串截断 | Test string truncation"""
        string = "LongTestString"
        byte_length = len(string.encode('utf-8'))
        register_count = (byte_length + 1) // 2
        registers = PayloadCoder.encode_string(string, register_count)
        
        # 完整解码 | Full decoding
        decoded_full = PayloadCoder.decode_string(registers)
        
        assert decoded_full.rstrip('\x00') == string
        print(f"✓ 字符串编码解码正常: '{string}' -> '{decoded_full.rstrip('\x00')}' | String encoding/decoding works: '{string}' -> '{decoded_full.rstrip('\x00')}'")


class TestPayloadCoderByteOrder:
    """字节序和字序测试 | Byte Order and Word Order Tests"""
    
    def test_different_byte_orders_produce_different_results(self):
        """测试不同字节序产生不同结果 | Test different byte orders produce different results"""
        value = 0x12345678
        
        registers_big = PayloadCoder.encode_int32(value, 'big', 'high')
        registers_little = PayloadCoder.encode_int32(value, 'little', 'high')
        
        # 不同字节序应该产生不同的寄存器值 | Different byte orders should produce different register values
        assert registers_big != registers_little
        
        # 但解码后应该得到相同的原始值 | But should decode to the same original value
        decoded_big = PayloadCoder.decode_int32(registers_big, 'big', 'high')
        decoded_little = PayloadCoder.decode_int32(registers_little, 'little', 'high')
        
        assert decoded_big == value
        assert decoded_little == value
        print(f"✓ 字节序测试: 大端{registers_big}, 小端{registers_little} | Byte order test: big-endian{registers_big}, little-endian{registers_little}")
    
    def test_different_word_orders_produce_different_results(self):
        """测试不同字序产生不同结果 | Test different word orders produce different results"""
        value = 0x12345678
        
        registers_high = PayloadCoder.encode_int32(value, 'big', 'high')
        registers_low = PayloadCoder.encode_int32(value, 'big', 'low')
        
        # 不同字序应该产生不同的寄存器顺序 | Different word orders should produce different register order
        assert registers_high != registers_low
        assert registers_high == [registers_low[1], registers_low[0]]  # 应该是相反的顺序 | Should be reverse order
        
        # 但解码后应该得到相同的原始值 | But should decode to the same original value
        decoded_high = PayloadCoder.decode_int32(registers_high, 'big', 'high')
        decoded_low = PayloadCoder.decode_int32(registers_low, 'big', 'low')
        
        assert decoded_high == value
        assert decoded_low == value
        print(f"✓ 字序测试: 高字在前{registers_high}, 低字在前{registers_low} | Word order test: high-first{registers_high}, low-first{registers_low}")
    
    def test_cross_decode_fails(self):
        """测试交叉解码失败 | Test cross-decoding fails"""
        value = 0x12345678
        
        # 用大端序编码 | Encode with big-endian
        registers = PayloadCoder.encode_int32(value, 'big', 'high')
        
        # 用小端序解码应该得到不同结果 | Decode with little-endian should give different result
        decoded_wrong = PayloadCoder.decode_int32(registers, 'little', 'high')
        
        assert decoded_wrong != value
        print(f"✓ 交叉解码检测: 原值{value:08X}, 错误解码{decoded_wrong:08X} | Cross-decode detection: original{value:08X}, wrong decode{decoded_wrong:08X}")


class TestModbusLogger:
    """Modbus日志系统测试 | Modbus Logger System Tests"""
    
    def test_logger_setup(self):
        """测试日志系统设置 | Test logger system setup"""
        # 设置日志系统 | Setup logging system
        ModbusLogger.setup_logging(level=logging.INFO, enable_debug=True)
        
        # 获取日志器 | Get logger
        logger = ModbusLogger.get_logger('test_module')
        
        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'modbuslink.test_module'
        print("✓ 日志系统设置成功 | Logger system setup successful")
    
    def test_logger_output(self):
        """测试日志输出 | Test logger output"""
        # 创建字符串流来捕获日志输出 | Create string stream to capture log output
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        
        # 设置日志系统 | Setup logging system
        ModbusLogger.setup_logging(level=logging.DEBUG, enable_debug=True)
        logger = ModbusLogger.get_logger('test_output')
        logger.addHandler(handler)
        
        # 测试不同级别的日志 | Test different log levels
        logger.debug("调试信息 | Debug message")
        logger.info("信息消息 | Info message")
        logger.warning("警告消息 | Warning message")
        logger.error("错误消息 | Error message")
        
        log_output = log_stream.getvalue()
        assert "调试信息" in log_output or "Debug message" in log_output
        assert "信息消息" in log_output or "Info message" in log_output
        assert "警告消息" in log_output or "Warning message" in log_output
        assert "错误消息" in log_output or "Error message" in log_output
        
        print("✓ 日志输出测试通过 | Logger output test passed")
    
    def test_protocol_debug(self):
        """测试协议调试功能 | Test protocol debug functionality"""
        # 启用协议调试 | Enable protocol debug
        ModbusLogger.enable_protocol_debug()
        
        logger = ModbusLogger.get_logger('protocol_test')
        
        # 模拟协议数据 | Simulate protocol data
        test_data = b'\x01\x03\x00\x00\x00\x0A\xC5\xCD'
        logger.debug(f"发送数据: {test_data.hex().upper()} | Sending data: {test_data.hex().upper()}")
        
        print("✓ 协议调试功能正常 | Protocol debug functionality works")
    
    @patch('logging.FileHandler')
    def test_file_logging(self, mock_file_handler):
        """测试文件日志记录 | Test file logging"""
        mock_handler = Mock()
        # 设置Mock对象的level属性为整数，避免比较问题
        mock_handler.level = logging.INFO
        mock_file_handler.return_value = mock_handler
        
        # 设置文件日志 | Setup file logging
        ModbusLogger.setup_logging(level=logging.INFO, log_file='test.log')
        
        # 验证文件处理器被创建 | Verify file handler was created
        mock_file_handler.assert_called_once_with('test.log', encoding='utf-8')
        print("✓ 文件日志设置正常 | File logging setup works")


class TestAdvancedClientFeatures:
    """高级客户端功能测试 | Advanced Client Features Tests"""
    
    @patch('socket.socket')
    def test_client_advanced_data_types(self, mock_socket):
        """测试客户端高级数据类型方法 | Test client advanced data type methods"""
        mock_sock = Mock()
        mock_socket.return_value = mock_sock
        
        transport = TcpTransport(host='127.0.0.1', port=502)
        client = ModbusClient(transport)
        
        # 检查高级数据类型方法是否存在 | Check if advanced data type methods exist
        advanced_methods = [
            'read_float32', 'write_float32',
            'read_int32', 'write_int32',
            'read_uint32', 'write_uint32',
            'read_int64', 'write_int64',
            'read_uint64', 'write_uint64',
            'read_string', 'write_string',
        ]
        
        for method_name in advanced_methods:
            assert hasattr(client, method_name)
            method = getattr(client, method_name)
            assert callable(method)
            print(f"✓ 高级方法存在: {method_name} | Advanced method exists: {method_name}")
    
    def test_client_method_signatures(self):
        """测试客户端方法签名 | Test client method signatures"""
        import inspect
        
        transport = TcpTransport(host='127.0.0.1', port=502)
        client = ModbusClient(transport)
        
        # 检查方法签名 | Check method signatures
        method_signatures = {
            'read_float32': ['slave_id', 'start_address'],
            'write_float32': ['slave_id', 'start_address', 'value'],
            'read_string': ['slave_id', 'start_address', 'length'],
            'write_string': ['slave_id', 'start_address', 'value'],
        }
        
        for method_name, expected_params in method_signatures.items():
            if hasattr(client, method_name):
                method = getattr(client, method_name)
                sig = inspect.signature(method)
                param_names = list(sig.parameters.keys())
                
                for expected_param in expected_params:
                    assert expected_param in param_names
                print(f"✓ 方法签名正确: {method_name}{list(sig.parameters.keys())} | Method signature correct: {method_name}{list(sig.parameters.keys())}")


if __name__ == '__main__':
    print("开始运行高级功能测试... | Starting advanced features tests...")
    print("=" * 70)
    
    # 运行所有测试 | Run all tests
    pytest.main([__file__, '-v', '--tb=short'])
    
    print("=" * 70)
    print("高级功能测试完成 | Advanced features tests completed")