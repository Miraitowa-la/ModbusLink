#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级功能测试脚本 | Advanced Features Test Script

本脚本用于测试 ModbusLink 库的高级功能，包括：
This script tests the advanced features of ModbusLink library, including:
- 数据编解码功能 | Data encoding/decoding functionality
- 日志系统 | Logging system
- 高级API方法 | Advanced API methods
"""

import sys
import os
import logging

# 添加src目录到Python路径 | Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from modbuslink.utils import PayloadCoder, ModbusLogger


def test_payload_coder():
    """
    测试数据编解码功能 | Test data encoding/decoding functionality
    """
    print("=== 测试数据编解码功能 | Testing Data Encoding/Decoding ===")
    
    # 测试32位浮点数 | Test 32-bit float
    print("\n--- 32位浮点数测试 | 32-bit Float Test ---")
    test_float = 3.14159
    
    # 大端字节序，高字在前 | Big endian, high word first
    encoded = PayloadCoder.encode_float32(test_float, 'big', 'high')
    decoded = PayloadCoder.decode_float32(encoded, 'big', 'high')
    print(f"原始值 | Original: {test_float}")
    print(f"编码结果 | Encoded: {encoded}")
    print(f"解码结果 | Decoded: {decoded}")
    print(f"精度匹配 | Precision match: {abs(test_float - decoded) < 1e-6}")
    
    # 小端字节序，低字在前 | Little endian, low word first
    encoded2 = PayloadCoder.encode_float32(test_float, 'little', 'low')
    decoded2 = PayloadCoder.decode_float32(encoded2, 'little', 'low')
    print(f"\n小端编码 | Little endian encoded: {encoded2}")
    print(f"小端解码 | Little endian decoded: {decoded2}")
    print(f"精度匹配 | Precision match: {abs(test_float - decoded2) < 1e-6}")
    
    # 测试32位整数 | Test 32-bit integer
    print("\n--- 32位整数测试 | 32-bit Integer Test ---")
    test_int = 123456789
    
    encoded_int = PayloadCoder.encode_int32(test_int, 'big', 'high')
    decoded_int = PayloadCoder.decode_int32(encoded_int, 'big', 'high')
    print(f"原始值 | Original: {test_int}")
    print(f"编码结果 | Encoded: {encoded_int}")
    print(f"解码结果 | Decoded: {decoded_int}")
    print(f"值匹配 | Value match: {test_int == decoded_int}")
    
    # 测试字符串 | Test string
    print("\n--- 字符串测试 | String Test ---")
    test_string = "ModbusLink测试"
    string_bytes = test_string.encode('utf-8')
    register_count = (len(string_bytes) + 1) // 2  # 每个寄存器2字节 | 2 bytes per register
    
    encoded_str = PayloadCoder.encode_string(test_string, register_count)
    decoded_str = PayloadCoder.decode_string(encoded_str)
    print(f"原始字符串 | Original: '{test_string}'")
    print(f"字节长度 | Byte length: {len(string_bytes)}")
    print(f"寄存器数量 | Register count: {register_count}")
    print(f"编码结果 | Encoded: {encoded_str}")
    print(f"解码结果 | Decoded: '{decoded_str}'")
    print(f"字符串匹配 | String match: {test_string == decoded_str}")
    
    # 测试64位数据类型 | Test 64-bit data types
    print("\n--- 64位数据类型测试 | 64-bit Data Types Test ---")
    test_int64 = 9223372036854775807  # 最大64位有符号整数 | Maximum 64-bit signed integer
    
    encoded_int64 = PayloadCoder.encode_int64(test_int64)
    decoded_int64 = PayloadCoder.decode_int64(encoded_int64)
    print(f"64位整数 | 64-bit integer: {test_int64} -> {encoded_int64} -> {decoded_int64}")
    print(f"值匹配 | Value match: {test_int64 == decoded_int64}")
    
    # 测试无符号整数 | Test unsigned integers
    print("\n--- 无符号整数测试 | Unsigned Integer Test ---")
    test_uint32 = 4294967295  # 最大32位无符号整数 | Maximum 32-bit unsigned integer
    
    encoded_uint32 = PayloadCoder.encode_uint32(test_uint32)
    decoded_uint32 = PayloadCoder.decode_uint32(encoded_uint32)
    print(f"32位无符号整数 | 32-bit unsigned: {test_uint32} -> {encoded_uint32} -> {decoded_uint32}")
    print(f"值匹配 | Value match: {test_uint32 == decoded_uint32}")
    
    print("\n✓ 数据编解码测试完成 | Data encoding/decoding test completed")


def test_logging_system():
    """
    测试日志系统 | Test logging system
    """
    print("\n=== 测试日志系统 | Testing Logging System ===")
    
    # 配置日志系统 | Configure logging system
    ModbusLogger.setup_logging(
        level=logging.INFO,
        enable_debug=True
    )
    
    # 获取日志器 | Get logger
    logger = ModbusLogger.get_logger('test')
    
    print("\n测试不同级别的日志输出 | Testing different log levels:")
    logger.debug("这是调试信息 | This is debug message")
    logger.info("这是信息日志 | This is info message")
    logger.warning("这是警告信息 | This is warning message")
    logger.error("这是错误信息 | This is error message")
    
    # 测试协议调试功能 | Test protocol debug functionality
    print("\n启用协议调试 | Enabling protocol debug:")
    ModbusLogger.enable_protocol_debug()
    
    protocol_logger = ModbusLogger.get_logger('transport.test')
    protocol_logger.debug("协议调试信息 | Protocol debug message")
    
    print("\n禁用协议调试 | Disabling protocol debug:")
    ModbusLogger.disable_protocol_debug()
    protocol_logger.debug("这条调试信息应该不会显示 | This debug message should not appear")
    
    print("\n✓ 日志系统测试完成 | Logging system test completed")


def test_error_handling():
    """
    测试错误处理 | Test error handling
    """
    print("\n=== 测试错误处理 | Testing Error Handling ===")
    
    # 测试无效的编码参数 | Test invalid encoding parameters
    print("\n测试无效参数处理 | Testing invalid parameter handling:")
    
    try:
        # 无效的字节序 | Invalid endian
        PayloadCoder.encode_float32(3.14, 'invalid_endian', 'high')
    except ValueError as e:
        print(f"✓ 捕获到预期的字节序错误 | Caught expected endian error: {e}")
    
    try:
        # 无效的字序 | Invalid word order
        PayloadCoder.encode_float32(3.14, 'big', 'invalid_order')
    except ValueError as e:
        print(f"✓ 捕获到预期的字序错误 | Caught expected word order error: {e}")
    
    try:
        # 无效的寄存器数据长度 | Invalid register data length
        PayloadCoder.decode_float32([1, 2, 3])  # 应该是2个寄存器 | Should be 2 registers
    except ValueError as e:
        print(f"✓ 捕获到预期的长度错误 | Caught expected length error: {e}")
    
    print("\n✓ 错误处理测试完成 | Error handling test completed")


def main():
    """
    主测试函数 | Main test function
    """
    print("ModbusLink 高级功能测试 | ModbusLink Advanced Features Test")
    print("=" * 60)
    
    try:
        # 测试数据编解码 | Test data encoding/decoding
        test_payload_coder()
        
        # 测试日志系统 | Test logging system
        test_logging_system()
        
        # 测试错误处理 | Test error handling
        test_error_handling()
        
        print("\n" + "=" * 60)
        print("\n✓ 所有测试完成 | All tests completed successfully")
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误 | Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()