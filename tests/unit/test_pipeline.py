"""Unit tests for core pipeline functionality."""

import pytest
import pandas as pd
import numpy as np
from silver_adventure.core.pipeline import (
    Pipeline, PipelineContext, PipelineStep, PipelineBuilder,
    DataProcessingStep, ConditionalStep, ParallelStep
)
from silver_adventure.core.config import Config
from tests.conftest import assert_pipeline_context_valid


class TestPipelineContext:
    """Test PipelineContext class."""
    
    def test_context_creation(self):
        """Test basic context creation."""
        context = PipelineContext(
            data={"test": "data"},
            pipeline_name="test_pipeline"
        )
        
        assert_pipeline_context_valid(context)
        assert context.data == {"test": "data"}
        assert context.pipeline_name == "test_pipeline"
        assert not context.has_errors()
    
    def test_context_metadata(self):
        """Test context metadata operations."""
        context = PipelineContext()
        
        # Test metadata updates
        context.update_metadata(key1="value1", key2="value2")
        assert context.get_metadata("key1") == "value1"
        assert context.get_metadata("key2") == "value2"
        assert context.get_metadata("nonexistent", "default") == "default"
    
    def test_context_errors(self):
        """Test context error handling."""
        context = PipelineContext()
        
        assert not context.has_errors()
        
        # Add error
        error = ValueError("Test error")
        context.add_error(error)
        
        assert context.has_errors()
        assert len(context.errors) == 1
        assert context.errors[0] == error
    
    def test_context_elapsed_time(self):
        """Test elapsed time calculation."""
        context = PipelineContext()
        
        # Should be very small since just created
        elapsed = context.get_elapsed_time()
        assert elapsed >= 0
        assert elapsed < 1.0  # Should be less than 1 second


class TestPipelineStep:
    """Test PipelineStep functionality."""
    
    def test_step_execution(self):
        """Test basic step execution."""
        
        class TestStep(PipelineStep):
            def execute(self, context):
                context.data = "processed"
                return context
        
        step = TestStep("test_step")
        context = PipelineContext(data="input")
        
        result = step(context)
        
        assert result.data == "processed"
        assert result.step_name == "test_step"
    
    def test_step_validation(self):
        """Test step input/output validation."""
        
        class ValidatingStep(PipelineStep):
            def execute(self, context):
                return context
            
            def validate_input(self, context):
                return context.data is not None
            
            def validate_output(self, context):
                return True
        
        step = ValidatingStep("validating_step")
        
        # Test with valid input
        context = PipelineContext(data="valid")
        result = step(context)
        assert not result.has_errors()
        
        # Test with invalid input
        context = PipelineContext(data=None)
        result = step(context)
        assert result.has_errors()
    
    def test_step_error_handling(self):
        """Test step error handling."""
        
        class ErrorStep(PipelineStep):
            def execute(self, context):
                raise ValueError("Test error")
        
        step = ErrorStep("error_step")
        context = PipelineContext(data="input")
        
        result = step(context)
        
        assert result.has_errors()
        assert len(result.errors) == 1
        assert "Test error" in str(result.errors[0])


class TestDataProcessingStep:
    """Test DataProcessingStep functionality."""
    
    def test_data_processing(self):
        """Test data processing step."""
        
        def processor(data):
            return data * 2
        
        step = DataProcessingStep("multiply_by_2", processor)
        context = PipelineContext(data=5)
        
        result = step(context)
        
        assert result.data == 10
        assert not result.has_errors()


class TestConditionalStep:
    """Test ConditionalStep functionality."""
    
    def test_conditional_execution_true(self):
        """Test conditional step when condition is true."""
        
        def condition(context):
            return context.data > 0
        
        true_step = DataProcessingStep("add_one", lambda x: x + 1)
        false_step = DataProcessingStep("subtract_one", lambda x: x - 1)
        
        conditional = ConditionalStep("conditional", condition, true_step, false_step)
        context = PipelineContext(data=5)
        
        result = conditional(context)
        
        assert result.data == 6  # Should execute true_step
    
    def test_conditional_execution_false(self):
        """Test conditional step when condition is false."""
        
        def condition(context):
            return context.data > 0
        
        true_step = DataProcessingStep("add_one", lambda x: x + 1)
        false_step = DataProcessingStep("subtract_one", lambda x: x - 1)
        
        conditional = ConditionalStep("conditional", condition, true_step, false_step)
        context = PipelineContext(data=-5)
        
        result = conditional(context)
        
        assert result.data == -6  # Should execute false_step


class TestParallelStep:
    """Test ParallelStep functionality."""
    
    def test_parallel_execution(self):
        """Test parallel step execution."""
        
        step1 = DataProcessingStep("step1", lambda x: x + 1)
        step2 = DataProcessingStep("step2", lambda x: x * 2)
        step3 = DataProcessingStep("step3", lambda x: x ** 2)
        
        parallel = ParallelStep("parallel", [step1, step2, step3])
        context = PipelineContext(data=5)
        
        result = parallel(context)
        
        # Should return list of results
        assert isinstance(result.data, list)
        assert len(result.data) == 3
        assert 6 in result.data   # 5 + 1
        assert 10 in result.data  # 5 * 2
        assert 25 in result.data  # 5 ** 2


class TestPipeline:
    """Test Pipeline functionality."""
    
    def test_pipeline_creation(self):
        """Test pipeline creation."""
        
        step1 = DataProcessingStep("step1", lambda x: x + 1)
        step2 = DataProcessingStep("step2", lambda x: x * 2)
        
        pipeline = Pipeline("test_pipeline", [step1, step2])
        
        assert pipeline.name == "test_pipeline"
        assert len(pipeline.steps) == 2
    
    def test_pipeline_execution(self):
        """Test pipeline execution."""
        
        step1 = DataProcessingStep("step1", lambda x: x + 1)
        step2 = DataProcessingStep("step2", lambda x: x * 2)
        
        pipeline = Pipeline("test_pipeline", [step1, step2])
        
        result = pipeline.execute(5)
        
        assert result.data == 12  # (5 + 1) * 2
        assert not result.has_errors()
        assert result.pipeline_name == "test_pipeline"
    
    def test_pipeline_with_error(self):
        """Test pipeline execution with error."""
        
        def error_processor(data):
            raise ValueError("Processing error")
        
        step1 = DataProcessingStep("step1", lambda x: x + 1)
        step2 = DataProcessingStep("step2", error_processor)
        
        pipeline = Pipeline("test_pipeline", [step1, step2])
        
        result = pipeline.execute(5)
        
        assert result.has_errors()
        assert len(result.errors) == 1
    
    def test_pipeline_validation(self):
        """Test pipeline validation."""
        
        # Empty pipeline
        pipeline = Pipeline("empty", [])
        errors = pipeline.validate()
        assert "no steps" in errors[0].lower()
        
        # Valid pipeline
        step1 = DataProcessingStep("step1", lambda x: x)
        pipeline = Pipeline("valid", [step1])
        errors = pipeline.validate()
        assert len(errors) == 0
    
    def test_pipeline_step_management(self):
        """Test pipeline step management."""
        
        step1 = DataProcessingStep("step1", lambda x: x + 1)
        step2 = DataProcessingStep("step2", lambda x: x * 2)
        step3 = DataProcessingStep("step3", lambda x: x - 1)
        
        pipeline = Pipeline("test", [step1])
        
        # Add step
        pipeline.add_step(step2)
        assert len(pipeline.steps) == 2
        
        # Insert step
        pipeline.insert_step(1, step3)
        assert len(pipeline.steps) == 3
        assert pipeline.steps[1].name == "step3"
        
        # Get step
        found_step = pipeline.get_step("step2")
        assert found_step is not None
        assert found_step.name == "step2"
        
        # Remove step
        pipeline.remove_step("step3")
        assert len(pipeline.steps) == 2
        assert pipeline.get_step("step3") is None


class TestPipelineBuilder:
    """Test PipelineBuilder functionality."""
    
    def test_builder_pattern(self):
        """Test builder pattern for pipeline creation."""
        
        pipeline = (
            PipelineBuilder("test_pipeline")
            .add_data_processing_step("step1", lambda x: x + 1)
            .add_data_processing_step("step2", lambda x: x * 2)
            .with_config({"test": "config"})
            .build()
        )
        
        assert pipeline.name == "test_pipeline"
        assert len(pipeline.steps) == 2
        assert pipeline.config["test"] == "config"
        
        # Test execution
        result = pipeline.execute(5)
        assert result.data == 12  # (5 + 1) * 2
    
    def test_builder_conditional_step(self):
        """Test builder with conditional step."""
        
        def condition(context):
            return context.data > 0
        
        true_step = DataProcessingStep("positive", lambda x: x + 10)
        false_step = DataProcessingStep("negative", lambda x: x - 10)
        
        pipeline = (
            PipelineBuilder("conditional_pipeline")
            .add_conditional_step("check_sign", condition, true_step, false_step)
            .build()
        )
        
        # Test positive case
        result = pipeline.execute(5)
        assert result.data == 15
        
        # Test negative case
        result = pipeline.execute(-5)
        assert result.data == -15
    
    def test_builder_parallel_step(self):
        """Test builder with parallel step."""
        
        step1 = DataProcessingStep("step1", lambda x: x + 1)
        step2 = DataProcessingStep("step2", lambda x: x * 2)
        
        pipeline = (
            PipelineBuilder("parallel_pipeline")
            .add_parallel_step("parallel_ops", [step1, step2])
            .build()
        )
        
        result = pipeline.execute(5)
        assert isinstance(result.data, list)
        assert len(result.data) == 2