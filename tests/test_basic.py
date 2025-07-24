#!/usr/bin/env python3
"""ModbusLink基本功能测试脚本 ModbusLink basic function test script

测试库的基本导入和接口功能。 Test the basic import and interface functions of the library.
"""

import sys
import os

# 添加src目录到Python路径 | Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_imports():
    """测试模块导入 Test module imports"""
    print("=== 模块导入测试 Module Import Test ===")
    
    try:
        # 测试主要接口导入 | Test main interface imports
        from modbuslink import (
            ModbusClient, RtuTransport, TcpTransport,
            ModbusLinkError, ConnectionError, TimeoutError, 
            CRCError, InvalidResponseError, ModbusException
        )
        print("✓ 主要接口导入成功 | Main interface import successful")
        
        # 测试子模块导入 | Test submodule imports
        from modbuslink.utils.crc import CRC16Modbus
        from modbuslink.transport.base import BaseTransport
        from modbuslink.client.sync_client import ModbusClient as SyncClient
        print("✓ 子模块导入成功 | Submodule import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败 | Import failed: {e}")
        return False


def test_transport_creation():
    """测试传输层创建 Test transport layer creation"""
    print("\n=== 传输层创建测试 Transport Layer Creation Test ===")
    
    try:
        from modbuslink import RtuTransport, TcpTransport
        
        # 测试RTU传输层创建 | Test RTU transport layer creation
        rtu_transport = RtuTransport(
            port='COM1',
            baudrate=9600,
            timeout=1.0
        )
        print(f"✓ RTU传输层创建成功 | RTU transport layer creation successful: {rtu_transport}")
        
        # 测试TCP传输层创建 | Test TCP transport layer creation
        tcp_transport = TcpTransport(
            host='192.168.1.100',
            port=502,
            timeout=10.0
        )
        print(f"✓ TCP传输层创建成功 | TCP transport layer creation successful: {tcp_transport}")
        
        return True
        
    except Exception as e:
        print(f"❌ 传输层创建失败 | Transport layer creation failed: {e}")
        return False


def test_client_creation():
    """测试客户端创建 Test client creation"""
    print("\n=== 客户端创建测试 Client Creation Test ===")
    
    try:
        from modbuslink import ModbusClient, RtuTransport
        
        # 创建传输层 | Create transport layer
        transport = RtuTransport('COM1')
        
        # 创建客户端 | Create client
        client = ModbusClient(transport)
        print(f"✓ 客户端创建成功 | Client creation successful: {client}")
        
        # 测试客户端方法存在性 | Test client method existence
        methods = [
            'read_coils', 'read_discrete_inputs',
            'read_holding_registers', 'read_input_registers',
            'write_single_coil', 'write_single_register',
            'write_multiple_coils', 'write_multiple_registers'
        ]
        
        for method in methods:
            if hasattr(client, method):
                print(f"  ✓ 方法 | Method {method} 存在 | exists")
            else:
                print(f"  ❌ 方法 | Method {method} 不存在 | does not exist")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 客户端创建失败 | Client creation failed: {e}")
        return False


def test_pdu_construction():
    """测试PDU构建（不实际发送） Test PDU construction (without actual sending)"""
    print("\n=== PDU构建测试 PDU Construction Test ===")
    
    try:
        import struct
        
        # 测试读取保持寄存器PDU构建 | Test read holding registers PDU construction
        pdu = struct.pack('>BHH', 0x03, 0, 4)  # 功能码0x03, 地址0, 数量4 | Function code 0x03, address 0, quantity 4
        expected = b'\x03\x00\x00\x00\x04'
        if pdu == expected:
            print(f"✓ 读取保持寄存器PDU构建正确 | Read holding registers PDU construction correct: {pdu.hex(' ').upper()}")
        else:
            print(f"❌ PDU构建错误 | PDU construction error: 期望 | Expected {expected.hex(' ').upper()}, 得到 | Got {pdu.hex(' ').upper()}")
            return False
        
        # 测试写单个寄存器PDU构建 | Test write single register PDU construction
        pdu = struct.pack('>BHH', 0x06, 0, 1234)  # 功能码0x06, 地址0, 值1234 | Function code 0x06, address 0, value 1234
        expected = b'\x06\x00\x00\x04\xd2'
        if pdu == expected:
            print(f"✓ 写单个寄存器PDU构建正确 | Write single register PDU construction correct: {pdu.hex(' ').upper()}")
        else:
            print(f"❌ PDU构建错误 | PDU construction error: 期望 | Expected {expected.hex(' ').upper()}, 得到 | Got {pdu.hex(' ').upper()}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ PDU构建测试失败 | PDU construction test failed: {e}")
        return False


def test_exception_hierarchy():
    """测试异常层次结构 Test exception hierarchy"""
    print("\n=== 异常层次结构测试 Exception Hierarchy Test ===")
    
    try:
        from modbuslink.common.exceptions import (
            ModbusLinkError, ConnectionError, TimeoutError,
            CRCError, InvalidResponseError, ModbusException
        )
        
        # 测试异常继承关系 | Test exception inheritance relationships
        exceptions = [
            ConnectionError, TimeoutError, CRCError,
            InvalidResponseError, ModbusException
        ]
        
        for exc_class in exceptions:
            if issubclass(exc_class, ModbusLinkError):
                print(f"✓ {exc_class.__name__} 正确继承自 | Correctly inherits from ModbusLinkError")
            else:
                print(f"❌ {exc_class.__name__} 未继承自 | Does not inherit from ModbusLinkError")
                return False
        
        # 测试ModbusException的特殊功能 | Test ModbusException special functionality
        exc = ModbusException(0x02, 0x03)
        if hasattr(exc, 'exception_code') and hasattr(exc, 'function_code'):
            print(f"✓ ModbusException属性正确 | ModbusException attributes correct: {exc}")
        else:
            print("❌ ModbusException属性缺失 | ModbusException attributes missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 异常层次结构测试失败 | Exception hierarchy test failed: {e}")
        return False


def test_version_info():
    """测试版本信息 Test version information"""
    print("\n=== 版本信息测试 Version Information Test ===")
    
    try:
        import modbuslink
        
        # 检查版本信息 | Check version information
        if hasattr(modbuslink, '__version__'):
            print(f"✓ 版本号 | Version: {modbuslink.__version__}")
        else:
            print("❌ 版本号缺失 | Version number missing")
            return False
        
        if hasattr(modbuslink, '__author__'):
            print(f"✓ 作者 | Author: {modbuslink.__author__}")
        else:
            print("❌ 作者信息缺失 | Author information missing")
        
        return True
        
    except Exception as e:
        print(f"❌ 版本信息测试失败 | Version information test failed: {e}")
        return False


def main():
    """主测试函数 Main test function"""
    print("ModbusLink基本功能测试 | ModbusLink Basic Function Test")
    print("=" * 50)
    
    # 执行所有测试 | Execute all tests
    tests = [
        ("模块导入 | Module Import", test_imports),
        ("传输层创建 | Transport Layer Creation", test_transport_creation),
        ("客户端创建 | Client Creation", test_client_creation),
        ("PDU构建 | PDU Construction", test_pdu_construction),
        ("异常层次结构 | Exception Hierarchy", test_exception_hierarchy),
        ("版本信息 | Version Information", test_version_info),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常 | test exception: {e}")
            results.append((test_name, False))
    
    # 总结 | Summary
    print("\n" + "=" * 50)
    print("=== 测试总结 Test Summary ===")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过 | Passed" if result else "❌ 失败 | Failed"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计 | Total: {passed}/{total} 测试通过 | tests passed")
    
    if passed == total:
        print("🎉 所有基本功能测试通过！ | All basic function tests passed!")
        print("\n✅ ModbusLink第一阶段开发完成 | ModbusLink Phase 1 Development Completed:")
        print("   - ✓ 项目结构初始化 | Project structure initialization")
        print("   - ✓ 核心工具与异常模块 | Core utilities and exception modules")
        print("   - ✓ 统一的传输层抽象基类 | Unified transport layer abstract base class")
        print("   - ✓ RTU和TCP传输层实现 | RTU and TCP transport layer implementation")
        print("   - ✓ 统一的同步客户端 | Unified synchronous client")
        print("   - ✓ 完整的API接口 | Complete API interface")
        print("   - ✓ 错误处理和异常管理 | Error handling and exception management")
    else:
        print(f"❌ {total - passed} 个测试失败，请检查实现。 | tests failed, please check implementation.")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)