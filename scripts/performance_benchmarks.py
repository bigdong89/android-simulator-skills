#!/usr/bin/env python3
"""
Performance Benchmarks for Android Simulator Skills

This script measures and reports the performance characteristics
of all core automation scripts.

Usage: python3 performance_benchmarks.py [--device DEVICE_ID] [--iterations N] [--output FILE]
"""

import argparse
import json
import sys
import time
import subprocess
import statistics
import psutil
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class BenchmarkResult:
    script_name: str
    operation: str
    execution_time: float
    memory_usage_mb: float
    success: bool
    error_message: Optional[str] = None

class PerformanceBenchmark:
    def __init__(self, device_id: Optional[str] = None):
        self.device_id = device_id
        self.device_flag = f"--device {device_id}" if device_id else ""
        self.results: List[BenchmarkResult] = []

    def measure_script_performance(self, script_name: str, operation_name: str,
                                  args: List[str] = None, iterations: int = 5) -> List[BenchmarkResult]:
        """Measure performance of a specific script operation"""
        results = []

        for i in range(iterations):
            print(f"  Running {operation_name} - iteration {i+1}/{iterations}")

            # Record initial memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB

            # Measure execution time
            start_time = time.time()

            try:
                # Build command
                cmd = ["python3", f"{script_name}", "--json"]
                if self.device_id:
                    cmd.extend(["--device", self.device_id])
                if args:
                    cmd.extend(args)

                # Execute command
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,  # 30 second timeout
                    cwd=os.path.dirname(os.path.abspath(__file__))
                )

                execution_time = time.time() - start_time

                # Record final memory usage
                final_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_usage = max(0, final_memory - initial_memory)

                success = result.returncode == 0
                error_msg = None if success else result.stderr.strip()

                results.append(BenchmarkResult(
                    script_name=script_name,
                    operation=operation_name,
                    execution_time=execution_time,
                    memory_usage_mb=memory_usage,
                    success=success,
                    error_message=error_msg
                ))

                if not success:
                    print(f"    ⚠️  Error: {error_msg}")

            except subprocess.TimeoutExpired:
                execution_time = time.time() - start_time
                results.append(BenchmarkResult(
                    script_name=script_name,
                    operation=operation_name,
                    execution_time=execution_time,
                    memory_usage_mb=0,
                    success=False,
                    error_message="Timeout after 30 seconds"
                ))
                print(f"    ❌ Timeout after 30 seconds")

            except Exception as e:
                execution_time = time.time() - start_time
                results.append(BenchmarkResult(
                    script_name=script_name,
                    operation=operation_name,
                    execution_time=execution_time,
                    memory_usage_mb=0,
                    success=False,
                    error_message=str(e)
                ))
                print(f"    ❌ Exception: {str(e)}")

        return results

    def benchmark_screen_mapper(self, iterations: int = 5):
        """Benchmark screen_mapper.py performance"""
        print("🖥️  Benchmarking screen_mapper.py...")

        # Test basic screen analysis
        results = self.measure_script_performance(
            "screen_mapper.py",
            "basic_screen_analysis",
            [],
            iterations
        )
        self.results.extend(results)

        # Test verbose screen analysis
        results = self.measure_script_performance(
            "screen_mapper.py",
            "verbose_screen_analysis",
            ["--verbose"],
            iterations
        )
        self.results.extend(results)

    def benchmark_navigator(self, iterations: int = 3):
        """Benchmark navigator.py performance"""
        print("🧭 Benchmarking navigator.py...")

        # Test element finding
        results = self.measure_script_performance(
            "navigator.py",
            "find_element",
            ["--find-text", "我的"],
            iterations
        )
        self.results.extend(results)

        # Test tap operation
        results = self.measure_script_performance(
            "navigator.py",
            "tap_element",
            ["--find-text", "我的", "--tap"],
            iterations
        )
        self.results.extend(results)

        # Test swipe operation
        results = self.measure_script_performance(
            "navigator.py",
            "swipe_operation",
            ["--swipe", "up"],
            iterations
        )
        self.results.extend(results)

    def benchmark_accessibility_audit(self, iterations: int = 3):
        """Benchmark accessibility_audit.py performance"""
        print("♿ Benchmarking accessibility_audit.py...")

        # Test basic accessibility audit
        results = self.measure_script_performance(
            "accessibility_audit.py",
            "basic_accessibility_audit",
            [],
            iterations
        )
        self.results.extend(results)

        # Test verbose accessibility audit
        results = self.measure_script_performance(
            "accessibility_audit.py",
            "verbose_accessibility_audit",
            ["--verbose"],
            iterations
        )
        self.results.extend(results)

        # Test specific check types
        for check_type in ["labels", "touch_targets", "structure"]:
            results = self.measure_script_performance(
                "accessibility_audit.py",
                f"accessibility_check_{check_type}",
                ["--check-type", check_type],
                iterations
            )
            self.results.extend(results)

    def benchmark_app_launcher(self, iterations: int = 3):
        """Benchmark app_launcher.py performance"""
        print("🚀 Benchmarking app_launcher.py...")

        # Test app listing
        results = self.measure_script_performance(
            "app_launcher.py",
            "list_apps",
            ["--list"],
            iterations
        )
        self.results.extend(results)

        # Test app state check (using system app)
        results = self.measure_script_performance(
            "app_launcher.py",
            "check_app_state",
            ["--check", "com.android.settings"],
            iterations
        )
        self.results.extend(results)

    def benchmark_advanced_workflows(self, iterations: int = 2):
        """Benchmark advanced_workflows.py performance"""
        print("🔄 Benchmarking advanced_workflows.py...")

        # Test different scenarios
        scenarios = ["accessibility"]  # Use lighter scenarios for benchmarking

        for scenario in scenarios:
            results = self.measure_script_performance(
                "../examples/advanced_workflows.py",
                f"workflow_{scenario}",
                ["--scenario", scenario, "--app", "com.android.settings"],
                iterations
            )
            self.results.extend(results)

    def calculate_statistics(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Calculate performance statistics for a set of results"""
        if not results:
            return {}

        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]

        if not successful_results:
            return {
                'total_runs': len(results),
                'successful_runs': 0,
                'failed_runs': len(failed_results),
                'success_rate': 0.0,
                'errors': [r.error_message for r in failed_results if r.error_message]
            }

        execution_times = [r.execution_time for r in successful_results]
        memory_usages = [r.memory_usage_mb for r in successful_results]

        return {
            'total_runs': len(results),
            'successful_runs': len(successful_results),
            'failed_runs': len(failed_results),
            'success_rate': len(successful_results) / len(results),
            'execution_time': {
                'mean': statistics.mean(execution_times),
                'median': statistics.median(execution_times),
                'min': min(execution_times),
                'max': max(execution_times),
                'std_dev': statistics.stdev(execution_times) if len(execution_times) > 1 else 0
            },
            'memory_usage_mb': {
                'mean': statistics.mean(memory_usages),
                'median': statistics.median(memory_usages),
                'min': min(memory_usages),
                'max': max(memory_usages)
            },
            'errors': [r.error_message for r in failed_results if r.error_message]
        }

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        print("📊 Generating performance report...")

        # Group results by operation
        operation_results = {}
        for result in self.results:
            key = f"{result.script_name}::{result.operation}"
            if key not in operation_results:
                operation_results[key] = []
            operation_results[key].append(result)

        # Calculate statistics for each operation
        report_data = {}
        for operation, results in operation_results.items():
            script_name, operation_name = operation.split("::")
            stats = self.calculate_statistics(results)

            report_data[operation] = {
                'script_name': script_name,
                'operation': operation_name,
                'statistics': stats
            }

        # Overall summary
        all_successful = [r for r in self.results if r.success]
        all_failed = [r for r in self.results if not r.success]

        overall_stats = {
            'total_operations': len(operation_results),
            'total_runs': len(self.results),
            'successful_runs': len(all_successful),
            'failed_runs': len(all_failed),
            'overall_success_rate': len(all_successful) / len(self.results) if self.results else 0,
            'average_execution_time': statistics.mean([r.execution_time for r in all_successful]) if all_successful else 0,
            'average_memory_usage': statistics.mean([r.memory_usage_mb for r in all_successful]) if all_successful else 0
        }

        # Performance grades
        performance_grades = self.assign_performance_grades(report_data)

        return {
            'timestamp': datetime.now().isoformat(),
            'device_id': self.device_id,
            'overall_statistics': overall_stats,
            'operation_results': report_data,
            'performance_grades': performance_grades,
            'recommendations': self.generate_recommendations(report_data)
        }

    def assign_performance_grades(self, report_data: Dict[str, Any]) -> Dict[str, str]:
        """Assign performance grades to operations"""
        grades = {}

        for operation, data in report_data.items():
            stats = data['statistics']

            # Grade based on execution time and success rate
            success_rate = stats.get('success_rate', 0)
            avg_time = stats.get('execution_time', {}).get('mean', float('inf'))

            if success_rate < 0.8:
                grade = 'F'  # Poor reliability
            elif avg_time > 10:
                grade = 'C'  # Slow but functional
            elif avg_time > 5:
                grade = 'B'  # Acceptable performance
            else:
                grade = 'A'  # Excellent performance

            grades[operation] = grade

        return grades

    def generate_recommendations(self, report_data: Dict[str, Any]) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []

        # Check for operations with high failure rates
        for operation, data in report_data.items():
            stats = data['statistics']
            success_rate = stats.get('success_rate', 1.0)

            if success_rate < 0.9:
                recommendations.append(
                    f"🔧 {operation}: Low success rate ({success_rate:.1%}). "
                    "Investigate error handling and timeout settings."
                )

            avg_time = stats.get('execution_time', {}).get('mean', 0)
            if avg_time > 5:
                recommendations.append(
                    f"⚡ {operation}: Slow execution ({avg_time:.2f}s average). "
                    "Consider optimizing algorithms or adding caching."
                )

            max_memory = stats.get('memory_usage_mb', {}).get('max', 0)
            if max_memory > 50:
                recommendations.append(
                    f"💾 {operation}: High memory usage ({max_memory:.1f}MB max). "
                    "Review memory management and data structures."
                )

        if not recommendations:
            recommendations.append("✅ All operations show acceptable performance characteristics.")

        return recommendations

    def save_report(self, filename: str = None):
        """Save performance benchmark report to file"""
        report = self.generate_report()

        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"performance_benchmark_report_{timestamp}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n📁 Performance report saved: {filename}")
            return filename
        except Exception as e:
            print(f"\n❌ Failed to save report: {e}")
            return None

    def print_summary(self):
        """Print performance summary to console"""
        report = self.generate_report()

        print("\n" + "=" * 60)
        print("📈 PERFORMANCE BENCHMARK SUMMARY")
        print("=" * 60)

        overall = report['overall_statistics']
        print(f"Total Operations: {overall['total_operations']}")
        print(f"Total Test Runs: {overall['total_runs']}")
        print(f"Successful Runs: {overall['successful_runs']}")
        print(f"Failed Runs: {overall['failed_runs']}")
        print(f"Overall Success Rate: {overall['overall_success_rate']:.1%}")
        print(f"Average Execution Time: {overall['average_execution_time']:.2f}s")
        print(f"Average Memory Usage: {overall['average_memory_usage']:.1f}MB")

        print("\n🎯 Performance Grades:")
        grades = report['performance_grades']
        grade_counts = {'A': 0, 'B': 0, 'C': 0, 'F': 0}
        for operation, grade in grades.items():
            grade_counts[grade] += 1
            script_name = operation.split("::")[0]
            print(f"  {grade} {script_name} - {operation.split('::')[1]}")

        print(f"\n📊 Grade Distribution:")
        for grade in ['A', 'B', 'C', 'F']:
            count = grade_counts[grade]
            symbol = {'A': '🏆', 'B': '✅', 'C': '⚠️', 'F': '❌'}[grade]
            print(f"  {symbol} Grade {grade}: {count} operations")

        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"  {rec}")

def main():
    parser = argparse.ArgumentParser(
        description="Performance benchmarks for Android Simulator Skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --device emulator-5554 --iterations 10
  %(prog)s --output benchmark_results.json --iterations 3
        """
    )

    parser.add_argument(
        '--device',
        help='Target Android device/emulator ID'
    )

    parser.add_argument(
        '--iterations',
        type=int,
        default=5,
        help='Number of iterations for each test (default: 5)'
    )

    parser.add_argument(
        '--output',
        help='Save report to specified JSON file'
    )

    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run quick benchmark (fewer iterations)'
    )

    args = parser.parse_args()

    iterations = 2 if args.quick else args.iterations

    # Initialize benchmark
    benchmark = PerformanceBenchmark(args.device)

    print("🚀 Android Simulator Skills - Performance Benchmarks")
    print("=" * 60)
    print(f"Device: {args.device or 'default'}")
    print(f"Iterations per test: {iterations}")
    print(f"Started: {datetime.now().isoformat()}")
    print()

    try:
        # Run benchmarks
        benchmark.benchmark_screen_mapper(iterations)
        benchmark.benchmark_navigator(min(iterations, 3))  # Navigator tests can be slow
        benchmark.benchmark_accessibility_audit(min(iterations, 3))
        benchmark.benchmark_app_launcher(iterations)

        if not args.quick:
            benchmark.benchmark_advanced_workflows(min(iterations, 2))

        # Generate and save report
        benchmark.print_summary()
        report_file = benchmark.save_report(args.output)

        # Exit with appropriate code
        overall_success_rate = benchmark.generate_report()['overall_statistics']['overall_success_rate']
        sys.exit(0 if overall_success_rate >= 0.8 else 1)

    except KeyboardInterrupt:
        print("\n⚠️ Benchmark interrupted by user")
        benchmark.save_report(f"interrupted_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        benchmark.save_report(f"failed_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        sys.exit(1)

if __name__ == '__main__':
    main()