#!/usr/bin/env python3
"""CRC16功能测试脚本 | CRC16 function test script

用于验证CRC16Modbus类的功能是否正常。 | Used to verify that the CRC16Modbus class functions properly.
"""

import sys
import os

# 添加src目录到Python路径 | Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from modbuslink.utils.crc import CRC16Modbus


def test_crc_calculation():
    """测试CRC计算功能 | Test CRC calculation function"""
    print("=== CRC16计算测试 | CRC16 Calculation Test ===")
    
    # 测试用例1: 读取保持寄存器请求 | Test case 1: Read holding registers request
    # 从站地址: 0x01, 功能码: 0x03, 起始地址: 0x0000, 数量: 0x0001 | Slave address: 0x01, function code: 0x03, starting address: 0x0000, quantity: 0x0001
    test_data1 = b'\x01\x03\x00\x00\x00\x01'
    expected_crc1 = b'\x84\x0a'  # 已知的正确CRC值 | Known correct CRC value
    
    calculated_crc1 = CRC16Modbus.calculate(test_data1)
    print(f"测试数据1 | Test data 1: {test_data1.hex(' ').upper()}")
    print(f"计算CRC | Calculated CRC: {calculated_crc1.hex(' ').upper()}")
    print(f"期望CRC | Expected CRC: {expected_crc1.hex(' ').upper()}")
    print(f"结果 | Result: {'✓ 通过 | Passed' if calculated_crc1 == expected_crc1 else '❌ 失败 | Failed'}")
    print()
    
    # 测试用例2: 写单个寄存器请求 | Test case 2: Write single register request
    # 从站地址: 0x01, 功能码: 0x06, 地址: 0x0000, 值: 0x1234 | Slave address: 0x01, function code: 0x06, address: 0x0000, value: 0x1234
    test_data2 = b'\x01\x06\x00\x00\x12\x34'
    calculated_crc2 = CRC16Modbus.calculate(test_data2)
    print(f"测试数据2 | Test data 2: {test_data2.hex(' ').upper()}")
    print(f"计算CRC | Calculated CRC: {calculated_crc2.hex(' ').upper()}")
    print()
    
    return calculated_crc1 == expected_crc1


def test_crc_validation():
    """测试CRC验证功能 | Test CRC validation function"""
    print("=== CRC16验证测试 | CRC16 Validation Test ===")
    
    # 测试用例1: 完整的正确帧 | Test case 1: Complete correct frame
    correct_frame = b'\x01\x03\x00\x00\x00\x01\x84\x0a'
    result1 = CRC16Modbus.validate(correct_frame)
    print(f"正确帧 | Correct frame: {correct_frame.hex(' ').upper()}")
    print(f"验证结果 | Validation result: {'✓ 通过 | Passed' if result1 else '❌ 失败 | Failed'}")
    print()
    
    # 测试用例2: CRC错误的帧 | Test case 2: Frame with incorrect CRC
    incorrect_frame = b'\x01\x03\x00\x00\x00\x01\x84\x0b'  # 最后一字节错误 | Last byte is incorrect
    result2 = CRC16Modbus.validate(incorrect_frame)
    print(f"错误帧 | Incorrect frame: {incorrect_frame.hex(' ').upper()}")
    print(f"验证结果 | Validation result: {'✓ 正确识别错误 | Correctly identified error' if not result2 else '❌ 未能识别错误 | Failed to identify error'}")
    print()
    
    # 测试用例3: 帧长度不足 | Test case 3: Frame with insufficient length
    short_frame = b'\x01\x03'
    result3 = CRC16Modbus.validate(short_frame)
    print(f"短帧 | Short frame: {short_frame.hex(' ').upper()}")
    print(f"验证结果 | Validation result: {'✓ 正确识别短帧 | Correctly identified short frame' if not result3 else '❌ 未能识别短帧 | Failed to identify short frame'}")
    print()
    
    return result1 and not result2 and not result3


def test_crc_compatibility():
    """测试与旧版本的兼容性 | Test compatibility with old versions"""
    print("=== 兼容性测试 | Compatibility Test ===")
    
    test_data = b'\x01\x03\x00\x00\x00\x01'
    
    # 新方法 | New method
    new_crc_bytes = CRC16Modbus.calculate(test_data)
    new_crc_int = int.from_bytes(new_crc_bytes, byteorder='little')
    
    # 旧方法（兼容性方法） | Old method (compatibility method)
    old_crc_int = CRC16Modbus.crc16_to_int(test_data)
    
    print(f"测试数据 | Test data: {test_data.hex(' ').upper()}")
    print(f"新方法(bytes) | New method (bytes): {new_crc_bytes.hex(' ').upper()}")
    print(f"新方法(int) | New method (int): {new_crc_int}")
    print(f"旧方法(int) | Old method (int): {old_crc_int}")
    print(f"兼容性 | Compatibility: {'✓ 兼容 | Compatible' if new_crc_int == old_crc_int else '❌ 不兼容 | Incompatible'}")
    print()
    
    return new_crc_int == old_crc_int


def main():
    """主测试函数 | Main test function"""
    print("ModbusLink CRC16功能测试 | ModbusLink CRC16 Function Test")
    print("=" * 50)
    print()
    
    # 执行所有测试 | Execute all tests
    test1_passed = test_crc_calculation()
    test2_passed = test_crc_validation()
    test3_passed = test_crc_compatibility()
    
    # 总结 | Summary
    print("=== 测试总结 | Test Summary ===")
    print(f"CRC计算测试 | CRC Calculation Test: {'✓ 通过 | Passed' if test1_passed else '❌ 失败 | Failed'}")
    print(f"CRC验证测试 | CRC Validation Test: {'✓ 通过 | Passed' if test2_passed else '❌ 失败 | Failed'}")
    print(f"兼容性测试 | Compatibility Test: {'✓ 通过 | Passed' if test3_passed else '❌ 失败 | Failed'}")
    print()
    
    all_passed = test1_passed and test2_passed and test3_passed
    if all_passed:
        print("🎉 所有测试通过！CRC16功能正常。 | All tests passed! CRC16 function is working properly.")
    else:
        print("❌ 部分测试失败，请检查CRC16实现。 | Some tests failed, please check CRC16 implementation.")
    
    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)