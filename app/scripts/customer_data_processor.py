"""
Sample JSON processing script.
"""

import json
from typing import Dict, List, Any


def process_customer_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process customer data for churn prediction.
    """
    processed = data.copy()
    
    # Add derived fields
    if 'monthly_charges' in processed and 'tenure' in processed:
        processed['total_estimated_charges'] = processed['monthly_charges'] * processed['tenure']
    
    # Categorize customer
    if 'age' in processed:
        age = processed['age']
        if age < 25:
            processed['age_category'] = 'young'
        elif age < 50:
            processed['age_category'] = 'middle'
        else:
            processed['age_category'] = 'senior'
    
    # Tenure categorization
    if 'tenure' in processed:
        tenure = processed['tenure']
        if tenure < 12:
            processed['tenure_category'] = 'new'
        elif tenure < 36:
            processed['tenure_category'] = 'medium'
        else:
            processed['tenure_category'] = 'long'
    
    return processed


def validate_customer_data(data: Dict[str, Any]) -> List[str]:
    """
    Validate customer data structure.
    """
    errors = []
    
    required_fields = ['customer_id', 'age', 'tenure', 'monthly_charges']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # Type validation
    if 'age' in data and not isinstance(data['age'], (int, float)):
        errors.append("Age must be a number")
    
    if 'tenure' in data and not isinstance(data['tenure'], (int, float)):
        errors.append("Tenure must be a number")
    
    if 'monthly_charges' in data and not isinstance(data['monthly_charges'], (int, float)):
        errors.append("Monthly charges must be a number")
    
    # Range validation
    if 'age' in data and (data['age'] < 0 or data['age'] > 150):
        errors.append("Age must be between 0 and 150")
    
    if 'tenure' in data and (data['tenure'] < 0 or data['tenure'] > 120):
        errors.append("Tenure must be between 0 and 120 months")
    
    if 'monthly_charges' in data and (data['monthly_charges'] < 0 or data['monthly_charges'] > 1000):
        errors.append("Monthly charges must be between 0 and 1000")
    
    return errors


if __name__ == "__main__":
    # Example usage
    sample_data = {
        "customer_id": "CUST001",
        "age": 35,
        "tenure": 24,
        "monthly_charges": 75.50,
        "contract_type": "one-year"
    }
    
    # Process data
    processed = process_customer_data(sample_data)
    print("Processed data:", json.dumps(processed, indent=2))
    
    # Validate data
    errors = validate_customer_data(sample_data)
    if errors:
        print("Validation errors:", errors)
    else:
        print("Data is valid")