"""Monitoring and observability utilities."""

import time
import psutil
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
from threading import Thread
import json

from ..core.logger import get_logger


@dataclass
class HealthStatus:
    """Health status data structure."""
    name: str
    status: str  # healthy, degraded, unhealthy
    message: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


class HealthChecker:
    """System health checker."""
    
    def __init__(self):
        self.logger = get_logger("health.checker")
        self.checks = {}
        self.last_check_time = None
        self.check_interval = 60  # seconds
    
    def add_check(self, name: str, check_func: Callable[[], bool], message: str = "") -> None:
        """Add a health check."""
        self.checks[name] = {
            "function": check_func,
            "message": message,
            "last_result": None,
            "last_check": None
        }
    
    def remove_check(self, name: str) -> None:
        """Remove a health check."""
        if name in self.checks:
            del self.checks[name]
    
    def run_check(self, name: str) -> HealthStatus:
        """Run a specific health check."""
        if name not in self.checks:
            return HealthStatus(
                name=name,
                status="unhealthy",
                message="Check not found",
                timestamp=datetime.utcnow()
            )
        
        check_info = self.checks[name]
        
        try:
            result = check_info["function"]()
            status = "healthy" if result else "unhealthy"
            message = check_info["message"] or f"Check {name} {'passed' if result else 'failed'}"
            
            health_status = HealthStatus(
                name=name,
                status=status,
                message=message,
                timestamp=datetime.utcnow()
            )
            
            # Update check info
            check_info["last_result"] = result
            check_info["last_check"] = datetime.utcnow()
            
            return health_status
        
        except Exception as e:
            self.logger.error(f"Health check '{name}' failed with exception: {str(e)}")
            return HealthStatus(
                name=name,
                status="unhealthy",
                message=f"Check failed: {str(e)}",
                timestamp=datetime.utcnow()
            )
    
    def run_all_checks(self) -> List[HealthStatus]:
        """Run all health checks."""
        results = []
        
        for check_name in self.checks:
            result = self.run_check(check_name)
            results.append(result)
        
        self.last_check_time = datetime.utcnow()
        return results
    
    def get_system_health(self) -> HealthStatus:
        """Get overall system health."""
        # Check CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Check memory usage
        memory = psutil.virtual_memory()
        
        # Check disk usage
        disk = psutil.disk_usage('/')
        
        # Determine overall health
        issues = []
        
        if cpu_percent > 80:
            issues.append(f"High CPU usage: {cpu_percent}%")
        
        if memory.percent > 80:
            issues.append(f"High memory usage: {memory.percent}%")
        
        if disk.percent > 80:
            issues.append(f"High disk usage: {disk.percent}%")
        
        if issues:
            status = "degraded" if len(issues) == 1 else "unhealthy"
            message = "; ".join(issues)
        else:
            status = "healthy"
            message = "System resources are healthy"
        
        return HealthStatus(
            name="system",
            status=status,
            message=message,
            timestamp=datetime.utcnow(),
            details={
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent
            }
        )


class MetricsCollector:
    """Collect and store application metrics."""
    
    def __init__(self):
        self.logger = get_logger("metrics.collector")
        self.metrics = {}
        self.counters = {}
        self.gauges = {}
        self.histograms = {}
    
    def increment_counter(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric."""
        key = self._get_metric_key(name, tags)
        
        if key not in self.counters:
            self.counters[key] = 0
        
        self.counters[key] += value
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric."""
        key = self._get_metric_key(name, tags)
        self.gauges[key] = {
            "value": value,
            "timestamp": time.time()
        }
    
    def add_histogram_sample(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Add a sample to a histogram metric."""
        key = self._get_metric_key(name, tags)
        
        if key not in self.histograms:
            self.histograms[key] = []
        
        self.histograms[key].append({
            "value": value,
            "timestamp": time.time()
        })
        
        # Keep only recent samples (last 1000)
        if len(self.histograms[key]) > 1000:
            self.histograms[key] = self.histograms[key][-1000:]
    
    def get_counter(self, name: str, tags: Optional[Dict[str, str]] = None) -> float:
        """Get counter value."""
        key = self._get_metric_key(name, tags)
        return self.counters.get(key, 0)
    
    def get_gauge(self, name: str, tags: Optional[Dict[str, str]] = None) -> Optional[float]:
        """Get gauge value."""
        key = self._get_metric_key(name, tags)
        gauge_data = self.gauges.get(key)
        return gauge_data["value"] if gauge_data else None
    
    def get_histogram_stats(self, name: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get histogram statistics."""
        key = self._get_metric_key(name, tags)
        samples = self.histograms.get(key, [])
        
        if not samples:
            return {}
        
        values = [sample["value"] for sample in samples]
        values.sort()
        
        count = len(values)
        total = sum(values)
        
        return {
            "count": count,
            "sum": total,
            "min": values[0],
            "max": values[-1],
            "mean": total / count,
            "median": values[count // 2],
            "p95": values[int(count * 0.95)] if count > 0 else 0,
            "p99": values[int(count * 0.99)] if count > 0 else 0,
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics."""
        return {
            "counters": self.counters,
            "gauges": {k: v["value"] for k, v in self.gauges.items()},
            "histograms": {k: self.get_histogram_stats(k) for k in self.histograms}
        }
    
    def _get_metric_key(self, name: str, tags: Optional[Dict[str, str]] = None) -> str:
        """Generate metric key with tags."""
        if not tags:
            return name
        
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"
    
    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        # Export counters
        for key, value in self.counters.items():
            lines.append(f"# TYPE {key} counter")
            lines.append(f"{key} {value}")
        
        # Export gauges
        for key, gauge_data in self.gauges.items():
            lines.append(f"# TYPE {key} gauge")
            lines.append(f"{key} {gauge_data['value']}")
        
        # Export histograms
        for key, samples in self.histograms.items():
            if not samples:
                continue
            
            stats = self.get_histogram_stats(key)
            lines.append(f"# TYPE {key} histogram")
            lines.append(f"{key}_count {stats['count']}")
            lines.append(f"{key}_sum {stats['sum']}")
            
            # Add buckets
            buckets = [0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
            values = [sample["value"] for sample in samples]
            
            for bucket in buckets:
                count = sum(1 for v in values if v <= bucket)
                lines.append(f"{key}_bucket{{le=\"{bucket}\"}} {count}")
            
            lines.append(f"{key}_bucket{{le=\"+Inf\"}} {stats['count']}")
        
        return "\n".join(lines)


class SystemMonitor:
    """Monitor system resources."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.logger = get_logger("system.monitor")
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self, interval: float = 10.0) -> None:
        """Start system monitoring."""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        self.logger.info("System monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop system monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("System monitoring stopped")
    
    def _monitor_loop(self, interval: float) -> None:
        """Monitor loop."""
        while self.monitoring:
            try:
                # CPU metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                self.metrics_collector.set_gauge("system_cpu_percent", cpu_percent)
                
                # Memory metrics
                memory = psutil.virtual_memory()
                self.metrics_collector.set_gauge("system_memory_percent", memory.percent)
                self.metrics_collector.set_gauge("system_memory_available", memory.available)
                self.metrics_collector.set_gauge("system_memory_total", memory.total)
                
                # Disk metrics
                disk = psutil.disk_usage('/')
                self.metrics_collector.set_gauge("system_disk_percent", disk.percent)
                self.metrics_collector.set_gauge("system_disk_free", disk.free)
                self.metrics_collector.set_gauge("system_disk_total", disk.total)
                
                # Network metrics
                net_io = psutil.net_io_counters()
                self.metrics_collector.set_gauge("system_network_bytes_sent", net_io.bytes_sent)
                self.metrics_collector.set_gauge("system_network_bytes_recv", net_io.bytes_recv)
                
                # Process metrics
                process = psutil.Process()
                self.metrics_collector.set_gauge("process_memory_rss", process.memory_info().rss)
                self.metrics_collector.set_gauge("process_memory_vms", process.memory_info().vms)
                self.metrics_collector.set_gauge("process_cpu_percent", process.cpu_percent())
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(interval)


# Global instances
health_checker = HealthChecker()
metrics_collector = MetricsCollector()
system_monitor = SystemMonitor(metrics_collector)


def get_health_checker() -> HealthChecker:
    """Get the global health checker instance."""
    return health_checker


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return metrics_collector


def get_system_monitor() -> SystemMonitor:
    """Get the global system monitor instance."""
    return system_monitor