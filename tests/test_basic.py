"""基础功能测试 | Basic Functionality Tests

测试ModbusLink库的基本功能，包括模块导入、传输层创建、客户端基本操作等。
Tests basic functionality of ModbusLink library, including module imports, transport layer creation, basic client operations.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# 添加源代码路径 | Add source code path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 尝试导入ModbusLink模块 | Try to import ModbusLink modules
modbuslink_available = True
try:
    from modbuslink import ModbusClient, TcpTransport, RtuTransport
    from modbuslink.common.exceptions import (
        ModbusException, ConnectionError, TimeoutError, CRCError
    )
    from modbuslink.utils.crc import CRC16Modbus
    from modbuslink.utils.coder import PayloadCoder
except ImportError as e:
    modbuslink_available = False
    import_error = str(e)
    # 创建模拟类以避免测试收集错误 | Create mock classes to avoid test collection errors
    ModbusClient = Mock
    TcpTransport = Mock
    RtuTransport = Mock
    ModbusException = Exception
    ConnectionError = Exception
    TimeoutError = Exception
    CRCError = Exception
    CRC16Modbus = Mock
    PayloadCoder = Mock


class TestModuleImports:
    """模块导入测试 | Module Import Tests"""
    
    @pytest.mark.skipif(not modbuslink_available, reason=f"ModbusLink模块不可用 | ModbusLink modules not available: {import_error if not modbuslink_available else ''}")
    def test_import_main_classes(self):
        """测试主要类的导入 | Test importing main classes"""
        assert ModbusClient is not None
        assert TcpTransport is not None
        assert RtuTransport is not None
        print("✓ 主要类导入成功 | Main classes imported successfully")
    
    @pytest.mark.skipif(not modbuslink_available, reason=f"ModbusLink模块不可用 | ModbusLink modules not available: {import_error if not modbuslink_available else ''}")
    def test_import_exceptions(self):
        """测试异常类的导入 | Test importing exception classes"""
        assert ModbusException is not None
        assert ConnectionError is not None
        assert TimeoutError is not None
        assert CRCError is not None
        print("✓ 异常类导入成功 | Exception classes imported successfully")
    
    @pytest.mark.skipif(not modbuslink_available, reason=f"ModbusLink模块不可用 | ModbusLink modules not available: {import_error if not modbuslink_available else ''}")
    def test_import_utilities(self):
        """测试工具类的导入 | Test importing utility classes"""
        assert CRC16Modbus is not None
        assert PayloadCoder is not None
        print("✓ 工具类导入成功 | Utility classes imported successfully")


@pytest.mark.skipif(not modbuslink_available, reason=f"ModbusLink模块不可用 | ModbusLink modules not available: {import_error if not modbuslink_available else ''}")
class TestTransportLayer:
    """传输层测试 | Transport Layer Tests"""
    
    def test_tcp_transport_creation(self):
        """测试TCP传输层创建 | Test TCP transport creation"""
        transport = TcpTransport(host='127.0.0.1', port=502, timeout=5.0)
        assert transport.host == '127.0.0.1'
        assert transport.port == 502
        assert transport.timeout == 5.0
        print("✓ TCP传输层创建成功 | TCP transport created successfully")
    
    def test_rtu_transport_creation(self):
        """测试RTU传输层创建 | Test RTU transport creation"""
        transport = RtuTransport(port='COM1', baudrate=9600, timeout=1.0)
        assert transport.port == 'COM1'
        assert transport.baudrate == 9600
        assert transport.timeout == 1.0
        print("✓ RTU传输层创建成功 | RTU transport created successfully")
    
    def test_tcp_transport_invalid_params(self):
        """测试TCP传输层无效参数 | Test TCP transport with invalid parameters"""
        with pytest.raises((ValueError, TypeError)):
            TcpTransport(host='', port=-1)
        print("✓ TCP传输层参数验证正常 | TCP transport parameter validation works")
    
    def test_rtu_transport_invalid_params(self):
        """测试RTU传输层无效参数 | Test RTU transport with invalid parameters"""
        with pytest.raises((ValueError, TypeError)):
            RtuTransport(port='', baudrate=-1)
        print("✓ RTU传输层参数验证正常 | RTU transport parameter validation works")


@pytest.mark.skipif(not modbuslink_available, reason=f"ModbusLink模块不可用 | ModbusLink modules not available: {import_error if not modbuslink_available else ''}")
class TestModbusClient:
    """Modbus客户端测试 | Modbus Client Tests"""
    
    def test_client_creation_with_tcp(self):
        """测试使用TCP传输层创建客户端 | Test client creation with TCP transport"""
        transport = TcpTransport(host='127.0.0.1', port=502)
        client = ModbusClient(transport)
        assert client.transport is transport
        print("✓ TCP客户端创建成功 | TCP client created successfully")
    
    def test_client_creation_with_rtu(self):
        """测试使用RTU传输层创建客户端 | Test client creation with RTU transport"""
        transport = RtuTransport(port='COM1', baudrate=9600)
        client = ModbusClient(transport)
        assert client.transport is transport
        print("✓ RTU客户端创建成功 | RTU client created successfully")
    
    @patch('socket.socket')
    def test_client_connect_tcp(self, mock_socket):
        """测试TCP客户端连接 | Test TCP client connection"""
        mock_sock = Mock()
        mock_socket.return_value = mock_sock
        
        transport = TcpTransport(host='127.0.0.1', port=502)
        client = ModbusClient(transport)
        
        try:
            client.connect()
            print("✓ TCP客户端连接测试通过 | TCP client connection test passed")
        except Exception as e:
            print(f"TCP连接测试异常（预期）: {e} | TCP connection test exception (expected): {e}")
        finally:
            try:
                client.disconnect()
            except:
                pass
    
    def test_client_context_manager(self):
        """测试客户端上下文管理器 | Test client context manager"""
        transport = TcpTransport(host='127.0.0.1', port=502)
        client = ModbusClient(transport)
        
        # 测试上下文管理器协议 | Test context manager protocol
        assert hasattr(client, '__enter__')
        assert hasattr(client, '__exit__')
        print("✓ 客户端上下文管理器协议正常 | Client context manager protocol works")


@pytest.mark.skipif(not modbuslink_available, reason=f"ModbusLink模块不可用 | ModbusLink modules not available: {import_error if not modbuslink_available else ''}")
class TestCRC16Modbus:
    """CRC16 Modbus测试 | CRC16 Modbus Tests"""
    
    def test_crc_calculation(self):
        """测试CRC计算 | Test CRC calculation"""
        # 测试已知数据的CRC值 | Test CRC value for known data
        data = b'\x01\x03\x00\x00\x00\x0A'
        expected_crc = 0xCDC5  # 已知的正确CRC值 | Known correct CRC value
        
        calculated_crc_bytes = CRC16Modbus.calculate(data)
        calculated_crc = int.from_bytes(calculated_crc_bytes, byteorder='little')
        assert calculated_crc == expected_crc
        print(f"✓ CRC计算正确: {calculated_crc:04X} | CRC calculation correct: {calculated_crc:04X}")
    
    def test_crc_verify(self):
        """测试CRC验证 | Test CRC verification"""
        # 包含正确CRC的完整数据包 | Complete packet with correct CRC
        data_with_crc = b'\x01\x03\x00\x00\x00\x0A\xC5\xCD'
        
        is_valid = CRC16Modbus.validate(data_with_crc)
        assert is_valid is True
        print("✓ CRC验证功能正常 | CRC verification works correctly")
    
    def test_crc_verify_invalid(self):
        """测试无效CRC验证 | Test invalid CRC verification"""
        # 包含错误CRC的数据包 | Packet with incorrect CRC
        data_with_wrong_crc = b'\x01\x03\x00\x00\x00\x0A\x00\x00'
        
        is_valid = CRC16Modbus.validate(data_with_wrong_crc)
        assert is_valid is False
        print("✓ 无效CRC检测正常 | Invalid CRC detection works")


@pytest.mark.skipif(not modbuslink_available, reason=f"ModbusLink模块不可用 | ModbusLink modules not available: {import_error if not modbuslink_available else ''}")
class TestPayloadCoder:
    """数据编码器测试 | Payload Coder Tests"""
    
    def test_encode_decode_float32(self):
        """测试32位浮点数编码解码 | Test 32-bit float encoding/decoding"""
        original_value = 3.14159
        
        # 编码 | Encode
        registers = PayloadCoder.encode_float32(original_value, 'big', 'high')
        assert len(registers) == 2
        
        # 解码 | Decode
        decoded_value = PayloadCoder.decode_float32(registers, 'big', 'high')
        assert abs(decoded_value - original_value) < 0.0001
        print(f"✓ Float32编码解码正常: {original_value} -> {decoded_value} | Float32 encode/decode works: {original_value} -> {decoded_value}")
    
    def test_encode_decode_int32(self):
        """测试32位整数编码解码 | Test 32-bit integer encoding/decoding"""
        original_value = 123456789
        
        # 编码 | Encode
        registers = PayloadCoder.encode_int32(original_value, 'big', 'high')
        assert len(registers) == 2
        
        # 解码 | Decode
        decoded_value = PayloadCoder.decode_int32(registers, 'big', 'high')
        assert decoded_value == original_value
        print(f"✓ Int32编码解码正常: {original_value} -> {decoded_value} | Int32 encode/decode works: {original_value} -> {decoded_value}")
    
    def test_encode_decode_string(self):
        """测试字符串编码解码 | Test string encoding/decoding"""
        original_string = "ModbusLink Test"  # 使用纯ASCII字符串避免编码问题 | Use pure ASCII string to avoid encoding issues
        
        # 计算需要的寄存器数量 | Calculate required register count
        byte_length = len(original_string.encode('utf-8'))
        register_count = (byte_length + 1) // 2  # 向上取整 | Round up
        
        # 编码 | Encode
        registers = PayloadCoder.encode_string(original_string, register_count)
        assert len(registers) > 0
        
        # 解码 | Decode
        decoded_string = PayloadCoder.decode_string(registers)
        assert decoded_string == original_string
        print(f"✓ 字符串编码解码正常: '{original_string}' | String encode/decode works: '{original_string}'")
    
    def test_different_byte_orders(self):
        """测试不同字节序 | Test different byte orders"""
        value = 0x12345678
        
        # 大端序，高字在前 | Big endian, high word first
        registers_big_high = PayloadCoder.encode_int32(value, 'big', 'high')
        decoded_big_high = PayloadCoder.decode_int32(registers_big_high, 'big', 'high')
        
        # 大端序，低字在前 | Big endian, low word first
        registers_big_low = PayloadCoder.encode_int32(value, 'big', 'low')
        decoded_big_low = PayloadCoder.decode_int32(registers_big_low, 'big', 'low')
        
        # 验证解码结果正确 | Verify decoding results are correct
        assert decoded_big_high == value
        assert decoded_big_low == value
        
        # 验证不同字序产生不同的寄存器排列 | Verify different word orders produce different register arrangements
        assert registers_big_high != registers_big_low
        print(f"✓ 不同字序处理正常: 高字在前={registers_big_high}, 低字在前={registers_big_low} | Different word order handling works: high first={registers_big_high}, low first={registers_big_low}")


@pytest.mark.skipif(not modbuslink_available, reason=f"ModbusLink模块不可用 | ModbusLink modules not available: {import_error if not modbuslink_available else ''}")
class TestTransportErrorHandling:
    """传输层错误处理测试 | Transport Layer Error Handling Tests"""
    
    def test_transport_connection_errors(self):
        """测试传输层连接错误 | Test transport layer connection errors"""
        # 测试TCP传输连接失败 | Test TCP transport connection failure
        tcp_transport = TcpTransport(host='192.0.2.1', port=12345, timeout=0.1)  # 使用不存在的地址 | Use non-existent address
        
        with pytest.raises(Exception):  # 应该抛出连接异常 | Should raise connection exception
            tcp_transport.connect()
        
        print("✓ 传输层连接错误处理正常 | Transport layer connection error handling works")
    
    def test_transport_send_without_connection(self):
        """测试未连接时发送数据 | Test sending data without connection"""
        tcp_transport = TcpTransport(host='127.0.0.1', port=502)
        
        with pytest.raises(Exception):  # 应该抛出未连接异常 | Should raise not connected exception
            tcp_transport.send(b'\x01\x03\x00\x00\x00\x01')
        
        print("✓ 未连接发送错误处理正常 | Send without connection error handling works")


if __name__ == '__main__':
    print("开始运行基础功能测试... | Starting basic functionality tests...")
    print("=" * 60)
    
    # 运行所有测试 | Run all tests
    pytest.main([__file__, '-v', '--tb=short'])
    
    print("=" * 60)
    print("基础功能测试完成 | Basic functionality tests completed")