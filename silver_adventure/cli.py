"""Command-line interface for Silver Adventure."""

import argparse
import sys
import json
from typing import Dict, Any, Optional
from pathlib import Path

from .core.config import get_config, reload_config
from .core.logger import setup_logging, get_logger
from .api.server import run_server
from .pipeline.registry import get_pipeline_registry
from .ml.models import get_model_registry
from .utils.monitoring import get_health_checker, get_metrics_collector


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Silver Adventure - PyPy-optimized pipeline system",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Server command
    server_parser = subparsers.add_parser('server', help='Start the API server')
    server_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    server_parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    server_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    server_parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    server_parser.add_argument('--config', help='Configuration file path')
    
    # Pipeline command
    pipeline_parser = subparsers.add_parser('pipeline', help='Pipeline operations')
    pipeline_subparsers = pipeline_parser.add_subparsers(dest='pipeline_action')
    
    # Pipeline list
    pipeline_subparsers.add_parser('list', help='List available pipelines')
    
    # Pipeline run
    run_parser = pipeline_subparsers.add_parser('run', help='Run a pipeline')
    run_parser.add_argument('name', help='Pipeline name')
    run_parser.add_argument('--input', help='Input data (JSON string or file path)')
    run_parser.add_argument('--config', help='Pipeline configuration (JSON string or file path)')
    run_parser.add_argument('--output', help='Output file path')
    
    # Pipeline info
    info_parser = pipeline_subparsers.add_parser('info', help='Get pipeline information')
    info_parser.add_argument('name', help='Pipeline name')
    
    # Model command
    model_parser = subparsers.add_parser('model', help='Model operations')
    model_subparsers = model_parser.add_subparsers(dest='model_action')
    
    # Model list
    model_subparsers.add_parser('list', help='List available models')
    
    # Model predict
    predict_parser = model_subparsers.add_parser('predict', help='Make predictions')
    predict_parser.add_argument('model', help='Model name')
    predict_parser.add_argument('--input', help='Input data (JSON string or file path)')
    predict_parser.add_argument('--output', help='Output file path')
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Health check operations')
    health_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Metrics command
    metrics_parser = subparsers.add_parser('metrics', help='Metrics operations')
    metrics_parser.add_argument('--format', choices=['json', 'prometheus'], default='json', help='Output format')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration operations')
    config_subparsers = config_parser.add_subparsers(dest='config_action')
    
    # Config show
    config_subparsers.add_parser('show', help='Show current configuration')
    
    # Config validate
    validate_parser = config_subparsers.add_parser('validate', help='Validate configuration')
    validate_parser.add_argument('file', help='Configuration file path')
    
    # Version command
    subparsers.add_parser('version', help='Show version information')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    logger = get_logger("cli")
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'server':
            handle_server_command(args)
        elif args.command == 'pipeline':
            handle_pipeline_command(args)
        elif args.command == 'model':
            handle_model_command(args)
        elif args.command == 'health':
            handle_health_command(args)
        elif args.command == 'metrics':
            handle_metrics_command(args)
        elif args.command == 'config':
            handle_config_command(args)
        elif args.command == 'version':
            handle_version_command(args)
        else:
            parser.print_help()
    
    except Exception as e:
        logger.error(f"Command failed: {str(e)}")
        sys.exit(1)


def handle_server_command(args):
    """Handle server command."""
    from .api.server import create_app
    import uvicorn
    
    # Load configuration
    if args.config:
        reload_config(args.config)
    
    config = get_config()
    
    # Override config with command line arguments
    if args.host:
        config.api.host = args.host
    if args.port:
        config.api.port = args.port
    if args.debug:
        config.api.debug = args.debug
    if args.reload:
        config.api.reload = args.reload
    
    print(f"Starting Silver Adventure API server on {config.api.host}:{config.api.port}")
    
    uvicorn.run(
        "silver_adventure.api.server:create_app",
        host=config.api.host,
        port=config.api.port,
        debug=config.api.debug,
        reload=config.api.reload,
        factory=True
    )


def handle_pipeline_command(args):
    """Handle pipeline command."""
    registry = get_pipeline_registry()
    
    if args.pipeline_action == 'list':
        pipelines = registry.list_pipelines()
        print("Available pipelines:")
        for pipeline_name in pipelines:
            print(f"  - {pipeline_name}")
    
    elif args.pipeline_action == 'run':
        # Load input data
        input_data = load_json_input(args.input)
        
        # Load configuration
        config = load_json_input(args.config) if args.config else None
        
        # Get pipeline
        pipeline = registry.get_pipeline(args.name)
        if not pipeline:
            print(f"Pipeline '{args.name}' not found")
            sys.exit(1)
        
        # Run pipeline
        print(f"Running pipeline '{args.name}'...")
        context = pipeline.execute(input_data, config)
        
        # Handle output
        if args.output:
            save_json_output(context.data, args.output)
            print(f"Results saved to {args.output}")
        else:
            print("Results:")
            print(json.dumps(context.data, indent=2, default=str))
        
        # Show errors if any
        if context.has_errors():
            print("Errors:")
            for error in context.errors:
                print(f"  - {error}")
    
    elif args.pipeline_action == 'info':
        info = registry.get_pipeline_info(args.name)
        if not info:
            print(f"Pipeline '{args.name}' not found")
            sys.exit(1)
        
        print(f"Pipeline: {info['name']}")
        print(f"Steps: {info['step_count']}")
        print("Step list:")
        for step in info['steps']:
            print(f"  - {step}")
        
        if info['config']:
            print("Configuration:")
            print(json.dumps(info['config'], indent=2))


def handle_model_command(args):
    """Handle model command."""
    registry = get_model_registry()
    
    if args.model_action == 'list':
        models = registry.list_models()
        print("Available models:")
        for model in models:
            print(f"  - {model['name']} ({model['version']}) - {model['status']}")
    
    elif args.model_action == 'predict':
        # Load input data
        input_data = load_json_input(args.input)
        
        # Get model
        model = registry.get_model(args.model)
        if not model:
            print(f"Model '{args.model}' not found")
            sys.exit(1)
        
        # Make prediction
        print(f"Making prediction with model '{args.model}'...")
        if args.model == 'churn_predictor':
            from .ml.churn_prediction import ChurnPredictor
            predictor = ChurnPredictor()
            predictions = predictor.predict_single(input_data)
        else:
            predictions = model.predict(input_data)
        
        # Handle output
        if args.output:
            save_json_output(predictions, args.output)
            print(f"Predictions saved to {args.output}")
        else:
            print("Predictions:")
            print(json.dumps(predictions, indent=2, default=str))


def handle_health_command(args):
    """Handle health command."""
    health_checker = get_health_checker()
    
    # Run all health checks
    results = health_checker.run_all_checks()
    
    # Get system health
    system_health = health_checker.get_system_health()
    results.append(system_health)
    
    # Display results
    print("Health Status:")
    for result in results:
        status_icon = "✓" if result.status == "healthy" else "⚠" if result.status == "degraded" else "✗"
        print(f"  {status_icon} {result.name}: {result.status} - {result.message}")
        
        if args.verbose and result.details:
            print(f"    Details: {json.dumps(result.details, indent=4)}")
    
    # Overall status
    unhealthy_count = sum(1 for r in results if r.status == "unhealthy")
    degraded_count = sum(1 for r in results if r.status == "degraded")
    
    if unhealthy_count > 0:
        print(f"\nOverall Status: UNHEALTHY ({unhealthy_count} unhealthy checks)")
        sys.exit(1)
    elif degraded_count > 0:
        print(f"\nOverall Status: DEGRADED ({degraded_count} degraded checks)")
    else:
        print("\nOverall Status: HEALTHY")


def handle_metrics_command(args):
    """Handle metrics command."""
    metrics_collector = get_metrics_collector()
    
    if args.format == 'json':
        metrics = metrics_collector.get_all_metrics()
        print(json.dumps(metrics, indent=2, default=str))
    elif args.format == 'prometheus':
        metrics = metrics_collector.export_prometheus()
        print(metrics)


def handle_config_command(args):
    """Handle config command."""
    config = get_config()
    
    if args.config_action == 'show':
        print("Current Configuration:")
        print(json.dumps(config.to_dict(), indent=2))
    
    elif args.config_action == 'validate':
        try:
            test_config = reload_config(args.file)
            print(f"Configuration file '{args.file}' is valid")
            print(f"Environment: {test_config.environment}")
            print(f"Debug: {test_config.debug}")
        except Exception as e:
            print(f"Configuration file '{args.file}' is invalid: {str(e)}")
            sys.exit(1)


def handle_version_command(args):
    """Handle version command."""
    from . import __version__, get_version_info
    
    print(f"Silver Adventure version: {__version__}")
    
    version_info = get_version_info()
    print(f"Build: {version_info['release']}.{version_info['build']}")
    print(f"Python: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    # PyPy information
    if hasattr(sys, 'pypy_version_info'):
        print(f"PyPy: {sys.pypy_version_info}")
    else:
        print("PyPy: Not available")


def load_json_input(input_str: Optional[str]) -> Any:
    """Load JSON input from string or file."""
    if not input_str:
        return None
    
    # Try to load as file first
    try:
        path = Path(input_str)
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    
    # Try to load as JSON string
    try:
        return json.loads(input_str)
    except json.JSONDecodeError:
        # Return as string if not valid JSON
        return input_str


def save_json_output(data: Any, output_path: str) -> None:
    """Save data to JSON file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)


if __name__ == "__main__":
    main()