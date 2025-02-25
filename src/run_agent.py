#!/usr/bin/env python3

import asyncio
import signal
import sys
import gc
import psutil
import time
from pathlib import Path
from typing import Optional, List, Dict
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from pyinjective.composer import Composer
from pyinjective.wallet import Address, PrivateKey

from src.config import Config, ConfigLoader
from src.agents.example_injective_agent import ExampleInjectiveAgent

class ResourceMonitor:
    """
    Monitors and manages system resources for the agent runner.
    
    This class provides functionality to:
    - Track memory usage and trigger garbage collection when needed
    - Monitor execution times and detect performance degradation
    - Maintain historical performance data with memory-efficient storage
    
    Attributes:
        process: System process being monitored
        warning_threshold: Memory threshold in bytes that triggers warnings
        start_time: Time when monitoring started
        execution_times: Historical execution times for performance tracking
    """
    
    def __init__(self, warning_threshold_mb: int = 1000):
        self.process = psutil.Process()
        self.warning_threshold = warning_threshold_mb * 1024 * 1024  # Convert to bytes
        self.start_time = time.time()
        self.execution_times: Dict[str, List[float]] = {}

    def check_memory_usage(self) -> tuple[float, bool]:
        """Check current memory usage and return if it's above threshold"""
        memory_info = self.process.memory_info()
        return memory_info.rss, memory_info.rss > self.warning_threshold

    def record_execution_time(self, agent_name: str, execution_time: float) -> None:
        """Record execution time for performance monitoring"""
        if agent_name not in self.execution_times:
            self.execution_times[agent_name] = []
        
        times = self.execution_times[agent_name]
        times.append(execution_time)
        
        # Keep only last 100 measurements
        if len(times) > 100:
            times.pop(0)

    def get_average_execution_time(self, agent_name: str) -> Optional[float]:
        """Get average execution time for an agent"""
        times = self.execution_times.get(agent_name, [])
        return sum(times) / len(times) if times else None

    def should_trigger_gc(self) -> bool:
        """Determine if garbage collection should be triggered"""
        memory_usage, is_high = self.check_memory_usage()
        return is_high

class AgentRunner:
    """
    Manages the execution of trading agents with comprehensive resource management.
    
    Key Features:
    1. Resource Management:
       - Memory monitoring and automatic garbage collection
       - Performance tracking and anomaly detection
       - Resource cleanup on shutdown
    
    2. Error Handling:
       - Exponential backoff for failed operations
       - Circuit breaker pattern for persistent errors
       - Graceful shutdown handling
    
    3. Logging:
       - Rotating log files with size limits
       - Structured logging format
       - Both console and file output
    
    4. Task Management:
       - Concurrent agent execution
       - Safe task cancellation
       - Resource cleanup
    
    Usage:
        runner = AgentRunner()
        await runner.initialize_agents(private_key)
        await runner.run()
    
    Configuration:
        - Memory threshold: 1000MB (configurable)
        - Log rotation: 10MB per file, 5 backup files
        - Circuit breaker: 5 consecutive errors
        - Backoff: 5s to 5min exponential
    """
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """
        Initialize the agent runner with resource management capabilities.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = ConfigLoader.load(config_path)
        ConfigLoader.validate_api_keys(self.config)
        self.running = False
        self.agents = []
        self.setup_logging()
        self.resource_monitor = ResourceMonitor()
        self.task_stats = {}

    def setup_logging(self) -> None:
        """Configure logging for the runner with rotation"""
        log_dir = Path(self.config.logging.file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Clear existing handlers
        root = logging.getLogger()
        if root.handlers:
            for handler in root.handlers:
                root.removeHandler(handler)
        
        # Setup rotating file handler
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            self.config.logging.file_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Setup formatters
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Configure root logger
        logging.basicConfig(
            level=self.config.logging.level,
            handlers=[file_handler, console_handler]
        )
        self.logger = logging.getLogger("AgentRunner")

    @asynccontextmanager
    async def managed_composer(self, private_key: str):
        """Context manager for Injective composer"""
        priv_key = PrivateKey.from_hex(private_key)
        address = Address(priv_key)
        composer = Composer(network=self.config.injective.network)
        try:
            yield composer, address
        finally:
            # Cleanup composer resources if needed
            if hasattr(composer, 'close') and callable(composer.close):
                await composer.close()

    async def initialize_agents(self, private_key: str) -> None:
        """Initialize agents for each configured market"""
        try:
            async with self.managed_composer(private_key) as (composer, address):
                for market_config in self.config.injective.markets:
                    agent = ExampleInjectiveAgent(self.config, market_config)
                    await agent.initialize(composer, address)
                    self.agents.append(agent)
                    self.logger.info(f"Initialized agent for market {market_config.id}")

        except Exception as e:
            self.logger.error(f"Error initializing agents: {e}")
            raise

    def handle_shutdown(self, signum, frame) -> None:
        """Handle shutdown signals gracefully"""
        self.logger.info("Received shutdown signal, stopping agents...")
        self.running = False

    async def run_agent_loop(self, agent: ExampleInjectiveAgent) -> None:
        """
        Run a single agent's execution loop with resource monitoring.
        
        Features:
        1. Memory Management:
           - Monitors memory usage before each execution
           - Triggers GC when memory exceeds threshold
           - Tracks resource usage statistics
        
        2. Performance Monitoring:
           - Records execution times
           - Detects abnormal execution durations
           - Maintains performance history
        
        3. Error Handling:
           - Implements exponential backoff
           - Circuit breaker for persistent errors
           - Graceful error recovery
        
        4. Resource Optimization:
           - Efficient sleep scheduling
           - Resource cleanup on errors
           - Performance statistics tracking
        
        Args:
            agent: The trading agent to run
        """
        update_interval = self.config.monitoring.update_interval
        consecutive_errors = 0
        agent_name = agent.get_name()
        
        while self.running:
            try:
                # Monitor memory before execution
                memory_usage, is_high = self.resource_monitor.check_memory_usage()
                if is_high:
                    self.logger.warning(
                        f"High memory usage detected: {memory_usage / (1024*1024):.2f} MB"
                    )
                    if self.resource_monitor.should_trigger_gc():
                        self.logger.info("Triggering garbage collection")
                        gc.collect()

                # Execute agent with timing
                start_time = time.time()
                await agent.execute()
                execution_time = time.time() - start_time
                
                # Record execution time
                self.resource_monitor.record_execution_time(agent_name, execution_time)
                
                # Monitor performance
                avg_time = self.resource_monitor.get_average_execution_time(agent_name)
                if avg_time and execution_time > avg_time * 2:
                    self.logger.warning(
                        f"Agent {agent_name} execution time ({execution_time:.2f}s) "
                        f"significantly higher than average ({avg_time:.2f}s)"
                    )

                # Reset error counter on successful execution
                consecutive_errors = 0
                
                # Reset daily metrics if needed
                if datetime.now().day != datetime.now().day:
                    agent.reset_daily_metrics()
                
                # Calculate and apply sleep time
                elapsed = time.time() - start_time
                sleep_time = max(0, update_interval - elapsed)
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"Error in agent {agent_name}: {e}")
                consecutive_errors += 1
                
                # Implement exponential backoff
                backoff_time = min(5 * (2 ** consecutive_errors), 300)  # Max 5 minutes
                self.logger.info(f"Backing off for {backoff_time} seconds")
                await asyncio.sleep(backoff_time)
                
                # Circuit breaker: stop agent if too many consecutive errors
                if consecutive_errors >= 5:
                    self.logger.error(f"Too many consecutive errors for {agent_name}, stopping")
                    break

    async def run(self) -> None:
        """
        Run all agents concurrently with resource management.
        
        Features:
        1. Task Management:
           - Creates named tasks for better monitoring
           - Handles concurrent execution
           - Ensures proper cleanup
        
        2. Resource Cleanup:
           - Cancels pending tasks
           - Waits for task completion
           - Triggers garbage collection
        
        3. Error Handling:
           - Catches and logs errors
           - Ensures proper shutdown
           - Maintains system stability
        """
        self.running = True
        tasks = []
        
        try:
            # Create tasks for all agents
            for agent in self.agents:
                task = asyncio.create_task(
                    self.run_agent_loop(agent),
                    name=f"agent_task_{agent.get_name()}"
                )
                tasks.append(task)
            
            # Wait for all tasks to complete
            await asyncio.gather(*tasks)
            
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
        finally:
            self.running = False
            
            # Clean up tasks
            for task in tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to cancel
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            # Final cleanup
            gc.collect()

async def main():
    if len(sys.argv) != 2:
        print("Usage: python run_agent.py <private_key>")
        sys.exit(1)

    private_key = sys.argv[1]
    runner = AgentRunner()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, runner.handle_shutdown)
    signal.signal(signal.SIGTERM, runner.handle_shutdown)
    
    try:
        # Initialize and run agents
        await runner.initialize_agents(private_key)
        await runner.run()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        # Ensure all resources are cleaned up
        logging.shutdown()

if __name__ == "__main__":
    asyncio.run(main()) 