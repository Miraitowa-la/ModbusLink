#!/usr/bin/env python3
"""测试运行脚本 | Test Runner Script

这个脚本提供了一个方便的方式来运行ModbusLink项目的所有测试。
This script provides a convenient way to run all tests for the ModbusLink project.

使用方法 | Usage:
    python run_tests.py [选项] | python run_tests.py [options]

选项 | Options:
    --basic         只运行基础测试 | Run only basic tests
    --crc           只运行CRC测试 | Run only CRC tests
    --advanced      只运行高级功能测试 | Run only advanced features tests
    --async         只运行异步测试 | Run only async tests
    --integration   只运行集成测试 | Run only integration tests
    --coverage      运行覆盖率测试 | Run coverage tests
    --performance   运行性能测试 | Run performance tests
    --verbose       详细输出 | Verbose output
    --quiet         安静模式 | Quiet mode
    --help          显示帮助 | Show help
"""

import sys
import subprocess
import argparse
from pathlib import Path

# 添加源代码路径 | Add source code path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def run_command(cmd, description):
    """运行命令并显示结果 | Run command and show results"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")

    try:
        subprocess.run(cmd, shell=True, check=True, capture_output=False)
        print(f"\n✅ {description} - 成功 | Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} - 失败 | Failed")
        print(f"错误代码 | Error code: {e.returncode}")
        return False
    except Exception as e:
        print(f"\n💥 {description} - 异常 | Exception: {e}")
        return False


def check_dependencies():
    """检查测试依赖 | Check test dependencies"""
    print("🔍 检查测试依赖... | Checking test dependencies...")

    required_packages = ["pytest", "pytest-cov", "pytest-mock", "pytest-asyncio"]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package} - 未安装 | Not installed")

    if missing_packages:
        print(f"\n⚠️  缺少依赖包 | Missing dependencies: {', '.join(missing_packages)}")
        print(
            "请运行 | Please run: pip install pytest pytest-cov pytest-mock pytest-asyncio"
        )
        return False

    print("\n✅ 所有测试依赖已安装 | All test dependencies installed")
    return True


def run_basic_tests(verbose=False):
    """运行基础测试 | Run basic tests"""
    cmd = f"pytest test_basic.py {'-v' if verbose else ''}"
    return run_command(cmd, "基础功能测试 | Basic Functionality Tests")


def run_crc_tests(verbose=False):
    """运行CRC测试 | Run CRC tests"""
    cmd = f"pytest test_crc.py {'-v' if verbose else ''}"
    return run_command(cmd, "CRC16 Modbus功能测试 | CRC16 Modbus Functionality Tests")


def run_advanced_tests(verbose=False):
    """运行高级功能测试 | Run advanced features tests"""
    cmd = f"pytest test_advanced_features.py {'-v' if verbose else ''}"
    return run_command(cmd, "高级功能测试 | Advanced Features Tests")


def run_async_tests(verbose=False):
    """运行异步测试 | Run async tests"""
    cmd = f"pytest test_async_integration.py {'-v' if verbose else ''}"
    return run_command(cmd, "异步集成测试 | Async Integration Tests")


def run_integration_tests(verbose=False):
    """运行集成测试 | Run integration tests"""
    cmd = f"pytest test_integration.py {'-v' if verbose else ''}"
    return run_command(cmd, "端到端集成测试 | End-to-End Integration Tests")


def run_all_tests(verbose=False, quiet=False):
    """运行所有测试 | Run all tests"""
    verbose_flag = "-v" if verbose else ""
    quiet_flag = "-q" if quiet else ""
    cmd = f"pytest . {verbose_flag} {quiet_flag}"
    return run_command(cmd, "所有测试 | All Tests")


def run_coverage_tests(verbose=False):
    """运行覆盖率测试 | Run coverage tests"""
    cmd = f"pytest . --cov=../src/modbuslink --cov-report=term-missing --cov-report=html {'-v' if verbose else ''}"
    return run_command(cmd, "测试覆盖率分析 | Test Coverage Analysis")


def run_performance_tests(verbose=False):
    """运行性能测试 | Run performance tests"""
    performance_tests = [
        "test_crc.py::TestCRC16ModbusPerformance",
        "test_async_integration.py::TestAsyncPerformance",
        "test_integration.py::TestPerformanceIntegration",
    ]

    success = True
    for test in performance_tests:
        cmd = f"pytest {test} {'-v' if verbose else ''}"
        if not run_command(cmd, f"性能测试 | Performance Test: {test.split('::')[-1]}"):
            success = False

    return success


def show_test_summary():
    """显示测试总结 | Show test summary"""
    print(f"\n{'='*60}")
    print("📊 测试总结 | Test Summary")
    print(f"{'='*60}")

    # 检查是否有覆盖率报告 | Check if coverage report exists
    coverage_file = project_root / "htmlcov" / "index.html"
    if coverage_file.exists():
        print(f"📈 覆盖率报告已生成 | Coverage report generated: {coverage_file}")

    # 检查是否有日志文件 | Check if log files exist
    log_dir = Path(__file__).parent / "logs"
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        if log_files:
            print(f"📝 测试日志文件 | Test log files: {len(log_files)} 个文件 | files")

    print("\n🎉 测试运行完成！| Test run completed!")


def main():
    """主函数 | Main function"""
    parser = argparse.ArgumentParser(
        description="ModbusLink 测试运行器 | ModbusLink Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例 | Examples:
  python run_tests.py                    # 运行所有测试 | Run all tests
  python run_tests.py --basic --verbose  # 运行基础测试（详细输出）| Run basic tests (verbose)
  python run_tests.py --coverage         # 运行覆盖率测试 | Run coverage tests
  python run_tests.py --performance      # 运行性能测试 | Run performance tests
        """,
    )

    # 测试类型选项 | Test type options
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument(
        "--basic", action="store_true", help="只运行基础测试 | Run only basic tests"
    )
    test_group.add_argument(
        "--crc", action="store_true", help="只运行CRC测试 | Run only CRC tests"
    )
    test_group.add_argument(
        "--advanced",
        action="store_true",
        help="只运行高级功能测试 | Run only advanced features tests",
    )
    test_group.add_argument(
        "--async-tests",
        action="store_true",
        help="只运行异步测试 | Run only async tests",
    )
    test_group.add_argument(
        "--integration",
        action="store_true",
        help="只运行集成测试 | Run only integration tests",
    )
    test_group.add_argument(
        "--coverage", action="store_true", help="运行覆盖率测试 | Run coverage tests"
    )
    test_group.add_argument(
        "--performance",
        action="store_true",
        help="运行性能测试 | Run performance tests",
    )

    # 输出选项 | Output options
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "--verbose", "-v", action="store_true", help="详细输出 | Verbose output"
    )
    output_group.add_argument(
        "--quiet", "-q", action="store_true", help="安静模式 | Quiet mode"
    )

    args = parser.parse_args()

    print("🚀 ModbusLink 测试运行器 | ModbusLink Test Runner")
    print(f"📁 项目目录 | Project directory: {project_root}")

    # 检查依赖 | Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # 确保日志目录存在 | Ensure log directory exists
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    success = True

    try:
        # 根据参数运行相应测试 | Run appropriate tests based on arguments
        if args.basic:
            success = run_basic_tests(args.verbose)
        elif args.crc:
            success = run_crc_tests(args.verbose)
        elif args.advanced:
            success = run_advanced_tests(args.verbose)
        elif args.async_tests:
            success = run_async_tests(args.verbose)
        elif args.integration:
            success = run_integration_tests(args.verbose)
        elif args.coverage:
            success = run_coverage_tests(args.verbose)
        elif args.performance:
            success = run_performance_tests(args.verbose)
        else:
            # 默认运行所有测试 | Default: run all tests
            success = run_all_tests(args.verbose, args.quiet)

        show_test_summary()

    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断 | Tests interrupted by user")
        success = False
    except Exception as e:
        print(f"\n\n💥 测试运行异常 | Test run exception: {e}")
        success = False

    # 退出码 | Exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
