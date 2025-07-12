"""Sample script demonstrating PyPy optimization features."""

import time
import numpy as np
from silver_adventure.utils.performance import pypy_optimizer, performance_monitor, measure_time
from silver_adventure.core.logger import get_logger

# Setup logging
logger = get_logger("sample.pypy_optimization")

def main():
    """Main function demonstrating PyPy optimization."""
    print("Silver Adventure - PyPy Optimization Sample")
    print("=" * 50)
    
    # Check PyPy information
    pypy_info = pypy_optimizer.get_pypy_info()
    print(f"PyPy Available: {pypy_info['pypy']}")
    
    if pypy_info['pypy']:
        print(f"PyPy Version: {pypy_info['version']}")
        print(f"JIT Enabled: {pypy_info['jit_enabled']}")
    
    # Demonstrate performance monitoring
    print("\n1. Performance Monitoring")
    print("-" * 30)
    
    # Test CPU-intensive operation
    with measure_time("cpu_intensive_operation"):
        result = cpu_intensive_operation(1000)
    
    print(f"CPU-intensive operation result: {result}")
    
    # Test memory usage
    with performance_monitor.monitor_operation("memory_intensive_operation"):
        result = memory_intensive_operation(10000)
    
    print(f"Memory-intensive operation result length: {len(result)}")
    
    # Demonstrate PyPy optimization
    print("\n2. PyPy Function Optimization")
    print("-" * 30)
    
    # Create optimized version of function
    optimized_function = pypy_optimizer.optimize_for_pypy(mathematical_computation)
    
    # Compare performance
    print("Testing regular function...")
    with measure_time("regular_function"):
        regular_result = mathematical_computation(1000)
    
    print("Testing PyPy-optimized function...")
    with measure_time("optimized_function"):
        optimized_result = optimized_function(1000)
    
    print(f"Results match: {regular_result == optimized_result}")
    
    # Demonstrate batch processing optimization
    print("\n3. Batch Processing Optimization")
    print("-" * 30)
    
    # Create test data
    test_data = [np.random.random(1000) for _ in range(10)]
    
    # Process with regular function
    with measure_time("regular_batch_processing"):
        regular_results = [process_array(arr) for arr in test_data]
    
    # Process with optimized function
    optimized_process = pypy_optimizer.optimize_for_pypy(process_array)
    with measure_time("optimized_batch_processing"):
        optimized_results = [optimized_process(arr) for arr in test_data]
    
    print(f"Batch processing results match: {np.allclose(regular_results, optimized_results)}")
    
    # Demonstrate pipeline optimization
    print("\n4. Pipeline Optimization")
    print("-" * 30)
    
    # Create optimized pipeline
    optimized_pipeline = create_optimized_pipeline()
    
    # Test pipeline with sample data
    sample_data = np.random.random(5000)
    
    with measure_time("optimized_pipeline"):
        pipeline_result = optimized_pipeline(sample_data)
    
    print(f"Pipeline result shape: {pipeline_result.shape}")
    print(f"Pipeline result stats: mean={pipeline_result.mean():.3f}, std={pipeline_result.std():.3f}")


def cpu_intensive_operation(n: int) -> float:
    """CPU-intensive operation for testing."""
    result = 0.0
    for i in range(n):
        for j in range(n):
            result += (i * j) ** 0.5
    return result


def memory_intensive_operation(n: int) -> list:
    """Memory-intensive operation for testing."""
    data = []
    for i in range(n):
        data.append([j * i for j in range(100)])
    return data


def mathematical_computation(n: int) -> float:
    """Mathematical computation that benefits from JIT compilation."""
    result = 0.0
    for i in range(n):
        x = i / n
        result += x * x * np.sin(x) + np.cos(x) * np.exp(-x)
    return result


def process_array(arr: np.ndarray) -> float:
    """Process array operation that benefits from optimization."""
    return np.sum(arr * arr) + np.mean(arr) * np.std(arr)


def create_optimized_pipeline():
    """Create an optimized data processing pipeline."""
    
    # Define pipeline steps
    @pypy_optimizer.optimize_for_pypy
    def step1_normalize(data):
        """Normalize data."""
        return (data - np.mean(data)) / np.std(data)
    
    @pypy_optimizer.optimize_for_pypy
    def step2_transform(data):
        """Apply mathematical transformation."""
        return np.log(1 + np.abs(data))
    
    @pypy_optimizer.optimize_for_pypy
    def step3_filter(data):
        """Filter outliers."""
        q1, q3 = np.percentile(data, [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        return data[(data >= lower_bound) & (data <= upper_bound)]
    
    @pypy_optimizer.optimize_for_pypy
    def step4_aggregate(data):
        """Aggregate data."""
        return np.array([
            np.mean(data),
            np.std(data),
            np.min(data),
            np.max(data),
            np.median(data)
        ])
    
    def pipeline(input_data):
        """Execute the full pipeline."""
        data = step1_normalize(input_data)
        data = step2_transform(data)
        data = step3_filter(data)
        result = step4_aggregate(data)
        return result
    
    return pipeline


# Additional optimization utilities
class PyPyBenchmark:
    """Benchmark utility for PyPy optimization."""
    
    def __init__(self):
        self.results = {}
    
    def benchmark_function(self, func, *args, iterations=10, warmup=3):
        """Benchmark a function with PyPy optimization."""
        # Warmup runs
        for _ in range(warmup):
            func(*args)
        
        # Benchmark runs
        times = []
        for _ in range(iterations):
            start = time.time()
            func(*args)
            end = time.time()
            times.append(end - start)
        
        return {
            'mean_time': np.mean(times),
            'std_time': np.std(times),
            'min_time': np.min(times),
            'max_time': np.max(times),
            'iterations': iterations
        }
    
    def compare_optimization(self, func, *args, iterations=10):
        """Compare regular vs optimized function performance."""
        # Benchmark regular function
        regular_stats = self.benchmark_function(func, *args, iterations=iterations)
        
        # Benchmark optimized function
        optimized_func = pypy_optimizer.optimize_for_pypy(func)
        optimized_stats = self.benchmark_function(optimized_func, *args, iterations=iterations)
        
        # Calculate improvement
        improvement = (regular_stats['mean_time'] - optimized_stats['mean_time']) / regular_stats['mean_time'] * 100
        
        return {
            'regular': regular_stats,
            'optimized': optimized_stats,
            'improvement_percent': improvement
        }


def demonstrate_benchmark():
    """Demonstrate benchmarking functionality."""
    print("\n5. PyPy Benchmark Comparison")
    print("-" * 30)
    
    benchmark = PyPyBenchmark()
    
    # Test mathematical computation
    result = benchmark.compare_optimization(mathematical_computation, 500)
    
    print(f"Mathematical Computation Benchmark:")
    print(f"  Regular function:   {result['regular']['mean_time']:.4f}s ± {result['regular']['std_time']:.4f}s")
    print(f"  Optimized function: {result['optimized']['mean_time']:.4f}s ± {result['optimized']['std_time']:.4f}s")
    print(f"  Improvement: {result['improvement_percent']:.1f}%")
    
    # Test array processing
    test_array = np.random.random(1000)
    result = benchmark.compare_optimization(process_array, test_array)
    
    print(f"\nArray Processing Benchmark:")
    print(f"  Regular function:   {result['regular']['mean_time']:.4f}s ± {result['regular']['std_time']:.4f}s")
    print(f"  Optimized function: {result['optimized']['mean_time']:.4f}s ± {result['optimized']['std_time']:.4f}s")
    print(f"  Improvement: {result['improvement_percent']:.1f}%")


if __name__ == "__main__":
    main()
    demonstrate_benchmark()