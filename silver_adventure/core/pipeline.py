"""Core pipeline framework for Silver Adventure."""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Type, Union
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import traceback
from contextlib import contextmanager

from .config import get_config
from .logger import PipelineLogger


@dataclass
class PipelineContext:
    """Context object passed between pipeline steps."""
    
    # Data payload
    data: Any = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Pipeline execution info
    pipeline_name: str = ""
    step_name: str = ""
    start_time: float = field(default_factory=time.time)
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Error handling
    errors: List[Exception] = field(default_factory=list)
    
    def add_error(self, error: Exception) -> None:
        """Add an error to the context."""
        self.errors.append(error)
    
    def has_errors(self) -> bool:
        """Check if context has errors."""
        return len(self.errors) > 0
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time since context creation."""
        return time.time() - self.start_time
    
    def update_metadata(self, **kwargs) -> None:
        """Update metadata with key-value pairs."""
        self.metadata.update(kwargs)
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)


class PipelineStep(ABC):
    """Abstract base class for pipeline steps."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.logger = PipelineLogger(f"step.{name}")
    
    @abstractmethod
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute the pipeline step."""
        pass
    
    def validate_input(self, context: PipelineContext) -> bool:
        """Validate input data. Override in subclasses."""
        return True
    
    def validate_output(self, context: PipelineContext) -> bool:
        """Validate output data. Override in subclasses."""
        return True
    
    def on_error(self, context: PipelineContext, error: Exception) -> PipelineContext:
        """Handle errors. Override in subclasses."""
        context.add_error(error)
        self.logger.error(f"Step '{self.name}' failed: {str(error)}")
        return context
    
    def __call__(self, context: PipelineContext) -> PipelineContext:
        """Execute the step with error handling and logging."""
        self.logger.step_start(self.name)
        context.step_name = self.name
        
        try:
            # Validate input
            if not self.validate_input(context):
                raise ValueError(f"Input validation failed for step '{self.name}'")
            
            # Execute step
            result_context = self.execute(context)
            
            # Validate output
            if not self.validate_output(result_context):
                raise ValueError(f"Output validation failed for step '{self.name}'")
            
            self.logger.step_end(self.name, success=True)
            return result_context
            
        except Exception as e:
            self.logger.exception(f"Step '{self.name}' failed with exception: {str(e)}")
            return self.on_error(context, e)


class DataProcessingStep(PipelineStep):
    """Generic data processing step."""
    
    def __init__(self, name: str, processor: Callable[[Any], Any], config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.processor = processor
    
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute data processing."""
        processed_data = self.processor(context.data)
        context.data = processed_data
        return context


class ConditionalStep(PipelineStep):
    """Conditional step that executes based on a condition."""
    
    def __init__(self, name: str, condition: Callable[[PipelineContext], bool], 
                 true_step: PipelineStep, false_step: Optional[PipelineStep] = None,
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.condition = condition
        self.true_step = true_step
        self.false_step = false_step
    
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute conditional logic."""
        if self.condition(context):
            return self.true_step(context)
        elif self.false_step:
            return self.false_step(context)
        return context


class ParallelStep(PipelineStep):
    """Step that executes multiple steps in parallel."""
    
    def __init__(self, name: str, steps: List[PipelineStep], 
                 merge_function: Optional[Callable[[List[PipelineContext]], PipelineContext]] = None,
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.steps = steps
        self.merge_function = merge_function or self._default_merge
    
    def _default_merge(self, contexts: List[PipelineContext]) -> PipelineContext:
        """Default merge function that combines all contexts."""
        if not contexts:
            return PipelineContext()
        
        # Use first context as base
        merged = contexts[0]
        
        # Merge data from all contexts
        all_data = [ctx.data for ctx in contexts]
        merged.data = all_data
        
        # Merge metadata
        for ctx in contexts[1:]:
            merged.metadata.update(ctx.metadata)
        
        # Merge errors
        for ctx in contexts[1:]:
            merged.errors.extend(ctx.errors)
        
        return merged
    
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute steps in parallel."""
        config = get_config()
        
        with ThreadPoolExecutor(max_workers=config.pipeline.max_workers) as executor:
            # Submit all steps
            futures = []
            for step in self.steps:
                # Create a copy of context for each step
                step_context = PipelineContext(
                    data=context.data,
                    metadata=context.metadata.copy(),
                    pipeline_name=context.pipeline_name,
                    config=context.config.copy()
                )
                futures.append(executor.submit(step, step_context))
            
            # Collect results
            results = []
            for future in futures:
                try:
                    result = future.result(timeout=config.pipeline.timeout)
                    results.append(result)
                except Exception as e:
                    error_context = PipelineContext()
                    error_context.add_error(e)
                    results.append(error_context)
        
        return self.merge_function(results)


class Pipeline:
    """Main pipeline class for orchestrating data processing steps."""
    
    def __init__(self, name: str, steps: List[PipelineStep], config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.steps = steps
        self.config = config or {}
        self.logger = PipelineLogger(f"pipeline.{name}")
        self._hooks = {
            'before_step': [],
            'after_step': [],
            'before_pipeline': [],
            'after_pipeline': [],
            'on_error': []
        }
    
    def add_hook(self, hook_type: str, hook_func: Callable) -> None:
        """Add a hook function."""
        if hook_type in self._hooks:
            self._hooks[hook_type].append(hook_func)
    
    def _execute_hooks(self, hook_type: str, context: PipelineContext, **kwargs) -> None:
        """Execute hooks of a specific type."""
        for hook in self._hooks[hook_type]:
            try:
                hook(context, **kwargs)
            except Exception as e:
                self.logger.error(f"Hook '{hook_type}' failed: {str(e)}")
    
    def execute(self, input_data: Any, config: Optional[Dict[str, Any]] = None) -> PipelineContext:
        """Execute the pipeline."""
        # Create initial context
        context = PipelineContext(
            data=input_data,
            pipeline_name=self.name,
            config={**self.config, **(config or {})}
        )
        
        self.logger.pipeline_start(self.name)
        self._execute_hooks('before_pipeline', context)
        
        try:
            # Execute each step
            for step in self.steps:
                self._execute_hooks('before_step', context, step=step)
                
                try:
                    context = step(context)
                    self._execute_hooks('after_step', context, step=step)
                except Exception as e:
                    self.logger.error(f"Pipeline '{self.name}' failed at step '{step.name}': {str(e)}")
                    self._execute_hooks('on_error', context, step=step, error=e)
                    context.add_error(e)
                    break
            
            # Check for errors
            success = not context.has_errors()
            self.logger.pipeline_end(self.name, success=success)
            self._execute_hooks('after_pipeline', context)
            
            return context
            
        except Exception as e:
            self.logger.exception(f"Pipeline '{self.name}' failed with exception: {str(e)}")
            context.add_error(e)
            self._execute_hooks('on_error', context, error=e)
            return context
    
    async def execute_async(self, input_data: Any, config: Optional[Dict[str, Any]] = None) -> PipelineContext:
        """Execute the pipeline asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.execute, input_data, config)
    
    def add_step(self, step: PipelineStep) -> None:
        """Add a step to the pipeline."""
        self.steps.append(step)
    
    def insert_step(self, index: int, step: PipelineStep) -> None:
        """Insert a step at a specific position."""
        self.steps.insert(index, step)
    
    def remove_step(self, step_name: str) -> None:
        """Remove a step by name."""
        self.steps = [step for step in self.steps if step.name != step_name]
    
    def get_step(self, step_name: str) -> Optional[PipelineStep]:
        """Get a step by name."""
        for step in self.steps:
            if step.name == step_name:
                return step
        return None
    
    def validate(self) -> List[str]:
        """Validate the pipeline configuration."""
        errors = []
        
        if not self.steps:
            errors.append("Pipeline has no steps")
        
        step_names = [step.name for step in self.steps]
        if len(step_names) != len(set(step_names)):
            errors.append("Duplicate step names found")
        
        return errors
    
    @contextmanager
    def monitoring(self):
        """Context manager for pipeline monitoring."""
        start_time = time.time()
        try:
            yield
        finally:
            end_time = time.time()
            self.logger.performance_metric("pipeline_duration", end_time - start_time)


class PipelineBuilder:
    """Builder pattern for creating pipelines."""
    
    def __init__(self, name: str):
        self.name = name
        self.steps = []
        self.config = {}
    
    def add_step(self, step: PipelineStep) -> "PipelineBuilder":
        """Add a step to the pipeline."""
        self.steps.append(step)
        return self
    
    def add_data_processing_step(self, name: str, processor: Callable[[Any], Any]) -> "PipelineBuilder":
        """Add a data processing step."""
        step = DataProcessingStep(name, processor)
        self.steps.append(step)
        return self
    
    def add_conditional_step(self, name: str, condition: Callable[[PipelineContext], bool], 
                           true_step: PipelineStep, false_step: Optional[PipelineStep] = None) -> "PipelineBuilder":
        """Add a conditional step."""
        step = ConditionalStep(name, condition, true_step, false_step)
        self.steps.append(step)
        return self
    
    def add_parallel_step(self, name: str, steps: List[PipelineStep]) -> "PipelineBuilder":
        """Add a parallel step."""
        step = ParallelStep(name, steps)
        self.steps.append(step)
        return self
    
    def with_config(self, config: Dict[str, Any]) -> "PipelineBuilder":
        """Set pipeline configuration."""
        self.config.update(config)
        return self
    
    def build(self) -> Pipeline:
        """Build the pipeline."""
        return Pipeline(self.name, self.steps, self.config)