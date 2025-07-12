"""Sample script demonstrating the Silver Adventure pipeline system."""

import pandas as pd
import numpy as np
from silver_adventure.core.pipeline import PipelineBuilder
from silver_adventure.pipeline.components import DataValidationStep, DataCleaningStep, DataTransformationStep
from silver_adventure.core.config import get_config
from silver_adventure.core.logger import get_logger

# Setup logging
logger = get_logger("sample.data_processing")

def main():
    """Main function demonstrating data processing pipeline."""
    print("Silver Adventure - Data Processing Pipeline Sample")
    print("=" * 50)
    
    # Create sample data
    sample_data = create_sample_data()
    print(f"Created sample data with {len(sample_data)} rows")
    
    # Build pipeline
    pipeline = (
        PipelineBuilder("sample_data_processing")
        .add_step(DataValidationStep("validate_input", {
            "validation_rules": {
                "required_columns": ["customer_id", "age", "income"],
                "no_nulls": False,
                "column_types": {
                    "age": "int",
                    "income": "float"
                }
            }
        }))
        .add_step(DataCleaningStep("clean_data", {
            "cleaning_rules": {
                "remove_duplicates": True,
                "null_strategy": "remove",
                "remove_outliers": True,
                "standardize_text": True
            }
        }))
        .add_step(DataTransformationStep("transform_data", {
            "transformations": [
                {
                    "type": "add_column",
                    "column": "income_category",
                    "value": "unknown"
                },
                {
                    "type": "normalize",
                    "column": "income"
                }
            ]
        }))
        .build()
    )
    
    # Execute pipeline
    print("\nExecuting pipeline...")
    context = pipeline.execute(sample_data)
    
    # Display results
    if context.has_errors():
        print("Pipeline completed with errors:")
        for error in context.errors:
            print(f"  - {error}")
    else:
        print("Pipeline completed successfully!")
    
    print(f"\nProcessed data shape: {context.data.shape}")
    print(f"Metadata: {context.metadata}")
    
    # Show first few rows
    print("\nFirst 5 rows of processed data:")
    print(context.data.head())


def create_sample_data():
    """Create sample customer data."""
    np.random.seed(42)
    
    n_customers = 1000
    
    data = {
        'customer_id': [f'CUST_{i:04d}' for i in range(n_customers)],
        'age': np.random.randint(18, 80, n_customers),
        'income': np.random.lognormal(10, 0.5, n_customers),
        'tenure': np.random.randint(1, 120, n_customers),
        'monthly_charges': np.random.uniform(20, 120, n_customers),
        'contract_type': np.random.choice(['Month-to-month', 'One year', 'Two year'], n_customers),
        'payment_method': np.random.choice(['Credit card', 'Bank transfer', 'Electronic check'], n_customers),
        'internet_service': np.random.choice(['DSL', 'Fiber optic', 'No'], n_customers),
        'phone_service': np.random.choice(['Yes', 'No'], n_customers),
    }
    
    # Add some missing values
    missing_indices = np.random.choice(n_customers, size=50, replace=False)
    for idx in missing_indices:
        data['income'][idx] = np.nan
    
    # Add some duplicates
    for i in range(10):
        data['customer_id'][i] = 'CUST_0000'
    
    return pd.DataFrame(data)


if __name__ == "__main__":
    main()