"""Sample script demonstrating churn prediction with Silver Adventure."""

import pandas as pd
import numpy as np
from silver_adventure.ml.churn_prediction import ChurnPredictor
from silver_adventure.core.logger import get_logger

# Setup logging
logger = get_logger("sample.churn_prediction")

def main():
    """Main function demonstrating churn prediction."""
    print("Silver Adventure - Churn Prediction Sample")
    print("=" * 50)
    
    # Create sample customer data
    customer_data = create_sample_customer_data()
    print(f"Created sample customer data: {len(customer_data)} customers")
    
    # Initialize churn predictor
    predictor = ChurnPredictor()
    
    # Make single prediction
    print("\nMaking single prediction...")
    single_customer = customer_data[0]
    print(f"Customer: {single_customer['customer_id']}")
    
    prediction = predictor.predict_single(single_customer)
    print(f"Churn Probability: {prediction['churn_probability']:.3f}")
    print(f"Churn Prediction: {prediction['churn_prediction']}")
    
    # Make batch predictions
    print("\nMaking batch predictions...")
    batch_predictions = predictor.predict_batch(customer_data[:10])
    
    print("Batch Prediction Results:")
    print("Customer ID    | Churn Prob | Prediction")
    print("-" * 45)
    for i, pred in enumerate(batch_predictions):
        customer_id = customer_data[i]['customer_id']
        prob = pred['churn_probability']
        prediction = pred['churn_prediction']
        print(f"{customer_id:12} | {prob:8.3f} | {str(prediction):10}")
    
    # Analyze feature importance
    print("\nFeature Importance:")
    feature_importance = prediction.get('feature_importance', {})
    for feature, importance in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True):
        print(f"  {feature:20}: {importance:.3f}")
    
    # Create training data and train model
    print("\nTraining model with sample data...")
    training_data, training_labels = create_training_data()
    
    # Train the model
    predictor.train(training_data, training_labels)
    
    # Evaluate model
    print("\nEvaluating model...")
    evaluation_results = predictor.evaluate(training_data, training_labels)
    
    print("Model Performance:")
    for metric, value in evaluation_results.items():
        if isinstance(value, float):
            print(f"  {metric:20}: {value:.3f}")
        else:
            print(f"  {metric:20}: {value}")


def create_sample_customer_data():
    """Create sample customer data for prediction."""
    np.random.seed(42)
    
    customers = []
    
    for i in range(100):
        customer = {
            'customer_id': f'CUST_{i:04d}',
            'tenure': np.random.randint(1, 72),
            'monthly_charges': np.random.uniform(20, 120),
            'total_charges': 0,  # Will be calculated
            'contract_type': np.random.choice(['Month-to-month', 'One year', 'Two year']),
            'payment_method': np.random.choice(['Credit card', 'Bank transfer', 'Electronic check']),
            'internet_service': np.random.choice(['DSL', 'Fiber optic', 'No']),
            'phone_service': np.random.choice(['Yes', 'No']),
        }
        
        # Calculate total charges
        customer['total_charges'] = customer['tenure'] * customer['monthly_charges'] + np.random.normal(0, 100)
        customer['total_charges'] = max(0, customer['total_charges'])
        
        customers.append(customer)
    
    return customers


def create_training_data():
    """Create training data for the churn prediction model."""
    np.random.seed(42)
    
    n_samples = 1000
    
    # Create features
    tenure = np.random.randint(1, 72, n_samples)
    monthly_charges = np.random.uniform(20, 120, n_samples)
    total_charges = tenure * monthly_charges + np.random.normal(0, 100, n_samples)
    total_charges = np.maximum(0, total_charges)
    
    contract_type = np.random.choice(['Month-to-month', 'One year', 'Two year'], n_samples)
    payment_method = np.random.choice(['Credit card', 'Bank transfer', 'Electronic check'], n_samples)
    internet_service = np.random.choice(['DSL', 'Fiber optic', 'No'], n_samples)
    phone_service = np.random.choice(['Yes', 'No'], n_samples)
    
    # Create DataFrame
    data = pd.DataFrame({
        'tenure': tenure,
        'monthly_charges': monthly_charges,
        'total_charges': total_charges,
        'contract_type': contract_type,
        'payment_method': payment_method,
        'internet_service': internet_service,
        'phone_service': phone_service,
    })
    
    # Create labels (simulate churn based on features)
    # Higher churn probability for:
    # - Short tenure
    # - High monthly charges
    # - Month-to-month contracts
    # - Electronic check payment
    churn_prob = (
        0.1 +  # Base probability
        0.3 * (tenure < 12) +  # Short tenure
        0.2 * (monthly_charges > 80) +  # High charges
        0.3 * (contract_type == 'Month-to-month') +  # Month-to-month
        0.2 * (payment_method == 'Electronic check') +  # Electronic check
        np.random.normal(0, 0.1, n_samples)  # Random noise
    )
    
    churn_prob = np.clip(churn_prob, 0, 1)
    churn_labels = (np.random.random(n_samples) < churn_prob).astype(int)
    
    return data, churn_labels


if __name__ == "__main__":
    main()