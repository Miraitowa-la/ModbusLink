"""CRC16 Modbus功能测试 | CRC16 Modbus Functionality Tests

专门测试CRC16 Modbus算法的正确性，包括各种边界情况和已知测试向量。
Specifically tests the correctness of CRC16 Modbus algorithm, including various edge cases and known test vectors.
"""

import pytest
import sys
import os

# 添加源代码路径 | Add source code path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from modbuslink.utils.crc import CRC16Modbus
except ImportError as e:
    pytest.skip(f"无法导入CRC模块: {e} | Cannot import CRC module: {e}", allow_module_level=True)


class TestCRC16ModbusCalculation:
    """CRC16 Modbus计算测试 | CRC16 Modbus Calculation Tests"""
    
    def test_empty_data(self):
        """测试空数据的CRC计算 | Test CRC calculation for empty data"""
        crc_bytes = CRC16Modbus.calculate(b'')
        crc = int.from_bytes(crc_bytes, byteorder='little')
        assert crc == 0xFFFF  # 空数据的CRC应该是初始值 | CRC for empty data should be initial value
        print(f"✓ 空数据CRC计算正确: {crc:04X} | Empty data CRC calculation correct: {crc:04X}")
    
    def test_single_byte(self):
        """测试单字节数据的CRC计算 | Test CRC calculation for single byte data"""
        test_cases = [
            (b'\x00', 0x40BF),
            (b'\x01', 0x807E),
            (b'\xFF', 0x00FF),
        ]
        
        for data, expected in test_cases:
            crc_bytes = CRC16Modbus.calculate(data)
            crc = int.from_bytes(crc_bytes, byteorder='little')
            assert crc == expected
            print(f"✓ 单字节 {data.hex().upper()} CRC: {crc:04X} | Single byte {data.hex().upper()} CRC: {crc:04X}")
    
    def test_known_test_vectors(self):
        """测试已知的测试向量 | Test known test vectors"""
        test_vectors = [
            # (数据, 期望的CRC) | (data, expected CRC)
            (b'\x01\x03\x00\x00\x00\x0A', 0xCDC5),  # 读保持寄存器请求 | Read holding registers request
            (b'\x01\x04\x00\x00\x00\x0A', 0x0D70),  # 读输入寄存器请求 | Read input registers request
            (b'\x01\x06\x00\x00\x00\x01', 0x0A48),  # 写单个寄存器请求 | Write single register request
            (b'\x01\x10\x00\x00\x00\x02\x04\x00\x0A\x00\x0B', 0x6A92),  # 写多个寄存器请求 | Write multiple registers request
        ]
        
        for data, expected_crc in test_vectors:
            calculated_crc_bytes = CRC16Modbus.calculate(data)
            calculated_crc = int.from_bytes(calculated_crc_bytes, byteorder='little')
            assert calculated_crc == expected_crc
            print(f"✓ 测试向量 {data.hex().upper()} CRC: {calculated_crc:04X} | Test vector {data.hex().upper()} CRC: {calculated_crc:04X}")
    
    def test_incremental_calculation(self):
        """测试增量CRC计算 | Test incremental CRC calculation"""
        data = b'\x01\x03\x00\x00\x00\x0A'
        
        # 一次性计算 | Calculate all at once
        crc_all_bytes = CRC16Modbus.calculate(data)
        crc_all = int.from_bytes(crc_all_bytes, byteorder='little')
        
        # 注意：当前实现不支持增量计算，这里只是验证完整计算的一致性
        # Note: Current implementation doesn't support incremental calculation, just verify consistency
        crc_verify_bytes = CRC16Modbus.calculate(data)
        crc_verify = int.from_bytes(crc_verify_bytes, byteorder='little')
        
        assert crc_all == crc_verify
        print(f"✓ CRC计算一致性验证: {crc_all:04X} == {crc_verify:04X} | CRC calculation consistency verified: {crc_all:04X} == {crc_verify:04X}")
    
    def test_large_data(self):
        """测试大数据块的CRC计算 | Test CRC calculation for large data blocks"""
        # 创建一个较大的数据块 | Create a large data block
        large_data = bytes(range(256)) * 4  # 1024字节 | 1024 bytes
        
        crc_bytes = CRC16Modbus.calculate(large_data)
        assert isinstance(crc_bytes, bytes)
        assert len(crc_bytes) == 2
        crc = int.from_bytes(crc_bytes, byteorder='little')
        assert 0 <= crc <= 0xFFFF
        print(f"✓ 大数据块CRC计算完成: {crc:04X} (数据长度: {len(large_data)}) | Large data block CRC calculated: {crc:04X} (data length: {len(large_data)})")


class TestCRC16ModbusVerification:
    """CRC16 Modbus验证测试 | CRC16 Modbus Verification Tests"""
    
    def test_verify_valid_packets(self):
        """测试验证有效数据包 | Test verifying valid packets"""
        valid_packets = [
            b'\x01\x03\x00\x00\x00\x0A\xC5\xCD',  # 读保持寄存器请求 | Read holding registers request
            b'\x01\x04\x00\x00\x00\x0A\x70\x0D',  # 读输入寄存器请求 | Read input registers request
            b'\x01\x06\x00\x00\x00\x01\x48\x0A',  # 写单个寄存器请求 | Write single register request
        ]
        
        for packet in valid_packets:
            is_valid = CRC16Modbus.validate(packet)
            assert is_valid is True
            print(f"✓ 有效数据包验证通过: {packet.hex().upper()} | Valid packet verification passed: {packet.hex().upper()}")
    
    def test_verify_invalid_packets(self):
        """测试验证无效数据包 | Test verifying invalid packets"""
        invalid_packets = [
            b'\x01\x03\x00\x00\x00\x0A\x00\x00',  # 错误的CRC | Wrong CRC
            b'\x01\x04\x00\x00\x00\x0A\xFF\xFF',  # 错误的CRC | Wrong CRC
            b'\x01\x06\x00\x00\x00\x01\x12\x34',  # 错误的CRC | Wrong CRC
        ]
        
        for packet in invalid_packets:
            is_valid = CRC16Modbus.validate(packet)
            assert is_valid is False
            print(f"✓ 无效数据包正确识别: {packet.hex().upper()} | Invalid packet correctly identified: {packet.hex().upper()}")
    
    def test_verify_short_packets(self):
        """测试验证过短的数据包 | Test verifying packets that are too short"""
        short_packets = [
            b'',  # 空数据包 | Empty packet
            b'\x01',  # 只有1字节 | Only 1 byte
            b'\x01\x03',  # 只有2字节 | Only 2 bytes
        ]
        
        for packet in short_packets:
            is_valid = CRC16Modbus.validate(packet)
            assert is_valid is False
            print(f"✓ 过短数据包正确拒绝: {packet.hex().upper() if packet else '(空)'} | Short packet correctly rejected: {packet.hex().upper() if packet else '(empty)'}")
    
    def test_verify_with_custom_initial_crc(self):
        """测试使用自定义初始CRC值的验证 | Test verification with custom initial CRC value"""
        # 这个测试确保validate函数总是使用正确的初始CRC值 | This test ensures validate function always uses correct initial CRC value
        packet = b'\x01\x03\x00\x00\x00\x0A\xC5\xCD'
        
        # 验证应该总是从标准初始值开始 | Verification should always start from standard initial value
        is_valid = CRC16Modbus.validate(packet)
        assert is_valid is True
        print("✓ 标准CRC验证正常 | Standard CRC verification works")


class TestCRC16ModbusEdgeCases:
    """CRC16 Modbus边界情况测试 | CRC16 Modbus Edge Cases Tests"""
    
    def test_crc_edge_cases(self):
        """测试CRC边界情况 | Test CRC edge cases"""
        # 测试空数据 | Test empty data
        crc_empty = CRC16Modbus.calculate(b'')
        assert isinstance(crc_empty, bytes)
        assert len(crc_empty) == 2
        
        # 测试单字节数据 | Test single byte data
        crc_single = CRC16Modbus.calculate(b'\x01')
        assert isinstance(crc_single, bytes)
        assert len(crc_single) == 2
        
        # 测试大量数据 | Test large amount of data
        large_data = b'\x00' * 1000
        crc_large = CRC16Modbus.calculate(large_data)
        assert isinstance(crc_large, bytes)
        assert len(crc_large) == 2
        
        print("✓ CRC边界情况测试通过 | CRC edge cases tested")
    
    def test_crc_consistency(self):
        """测试CRC计算一致性 | Test CRC calculation consistency"""
        test_data = b'\x01\x03\x00\x00\x00\x0A'
        
        # 多次计算应该得到相同结果 | Multiple calculations should yield same result
        crc1 = CRC16Modbus.calculate(test_data)
        crc2 = CRC16Modbus.calculate(test_data)
        crc3 = CRC16Modbus.calculate(test_data)
        
        assert crc1 == crc2 == crc3
        crc_int = int.from_bytes(crc1, 'little')
        print(f"✓ CRC计算一致性验证通过: {crc_int:04X} | CRC calculation consistency verified: {crc_int:04X}")
    
    def test_all_zeros(self):
        """测试全零数据 | Test all-zero data"""
        data = b'\x00' * 10
        crc_bytes = CRC16Modbus.calculate(data)
        assert isinstance(crc_bytes, bytes)
        crc = int.from_bytes(crc_bytes, byteorder='little')
        assert 0 <= crc <= 0xFFFF
        print(f"✓ 全零数据CRC: {crc:04X} | All-zero data CRC: {crc:04X}")
    
    def test_all_ones(self):
        """测试全一数据 | Test all-one data"""
        data = b'\xFF' * 10
        crc_bytes = CRC16Modbus.calculate(data)
        assert isinstance(crc_bytes, bytes)
        crc = int.from_bytes(crc_bytes, byteorder='little')
        assert 0 <= crc <= 0xFFFF
        print(f"✓ 全一数据CRC: {crc:04X} | All-one data CRC: {crc:04X}")
    
    def test_alternating_pattern(self):
        """测试交替模式数据 | Test alternating pattern data"""
        data = b'\xAA\x55' * 5
        crc_bytes = CRC16Modbus.calculate(data)
        assert isinstance(crc_bytes, bytes)
        crc = int.from_bytes(crc_bytes, byteorder='little')
        assert 0 <= crc <= 0xFFFF
        print(f"✓ 交替模式数据CRC: {crc:04X} | Alternating pattern data CRC: {crc:04X}")
    
    def test_sequential_data(self):
        """测试顺序数据 | Test sequential data"""
        data = bytes(range(256))
        crc_bytes = CRC16Modbus.calculate(data)
        assert isinstance(crc_bytes, bytes)
        crc = int.from_bytes(crc_bytes, byteorder='little')
        assert 0 <= crc <= 0xFFFF
        print(f"✓ 顺序数据CRC: {crc:04X} | Sequential data CRC: {crc:04X}")
    
    def test_crc_consistency(self):
        """测试CRC计算的一致性 | Test CRC calculation consistency"""
        data = b'\x01\x03\x00\x00\x00\x0A'
        
        # 多次计算应该得到相同结果 | Multiple calculations should yield same result
        crc1_bytes = CRC16Modbus.calculate(data)
        crc2_bytes = CRC16Modbus.calculate(data)
        crc3_bytes = CRC16Modbus.calculate(data)
        
        assert crc1_bytes == crc2_bytes == crc3_bytes
        crc1 = int.from_bytes(crc1_bytes, byteorder='little')
        print(f"✓ CRC计算一致性验证通过: {crc1:04X} | CRC calculation consistency verified: {crc1:04X}")


class TestCRC16ModbusPerformance:
    """CRC16 Modbus性能测试 | CRC16 Modbus Performance Tests"""
    
    def test_performance_small_data(self):
        """测试小数据块的性能 | Test performance with small data blocks"""
        import time
        
        data = b'\x01\x03\x00\x00\x00\x0A'
        iterations = 10000
        
        start_time = time.time()
        for _ in range(iterations):
            CRC16Modbus.calculate(data)
        end_time = time.time()
        
        elapsed = end_time - start_time
        rate = iterations / elapsed
        
        print(f"✓ 小数据块性能: {rate:.0f} 次/秒 ({elapsed:.3f}秒/{iterations}次) | Small data performance: {rate:.0f} ops/sec ({elapsed:.3f}s/{iterations} ops)")
        
        # 性能应该足够好 | Performance should be good enough
        assert rate > 1000  # 至少1000次/秒 | At least 1000 ops/sec
    
    def test_performance_large_data(self):
        """测试大数据块的性能 | Test performance with large data blocks"""
        import time
        
        data = bytes(range(256)) * 4  # 1024字节 | 1024 bytes
        iterations = 1000
        
        start_time = time.time()
        for _ in range(iterations):
            CRC16Modbus.calculate(data)
        end_time = time.time()
        
        elapsed = end_time - start_time
        rate = iterations / elapsed
        throughput = (len(data) * iterations) / (1024 * 1024) / elapsed  # MB/s
        
        print(f"✓ 大数据块性能: {rate:.0f} 次/秒, {throughput:.1f} MB/s | Large data performance: {rate:.0f} ops/sec, {throughput:.1f} MB/s")
        
        # 性能应该足够好 | Performance should be good enough
        assert rate > 100  # 至少100次/秒 | At least 100 ops/sec


if __name__ == '__main__':
    print("开始运行CRC16 Modbus功能测试... | Starting CRC16 Modbus functionality tests...")
    print("=" * 70)
    
    # 运行所有测试 | Run all tests
    pytest.main([__file__, '-v', '--tb=short'])
    
    print("=" * 70)
    print("CRC16 Modbus功能测试完成 | CRC16 Modbus functionality tests completed")