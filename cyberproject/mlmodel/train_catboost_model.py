"""
CatBoost Phishing Detection Model Training Script
This script trains a CatBoost classifier on the phishing dataset and saves it as a pickle file.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import metrics
from catboost import CatBoostClassifier
import joblib
import os

# Set paths
DATASET_PATH = r"C:\Users\suman\OneDrive\Documents\cyber\cyberproject\mlmodel\datasets\phishing.csv"
MODEL_OUTPUT_PATH = r"C:\Users\suman\OneDrive\Documents\cyber\cyberproject\mlmodel\mlmodelsperformance\catboost_phishing.pkl"

def load_and_prepare_data():
    """Load and prepare the phishing dataset"""
    print("Loading dataset...")
    data = pd.read_csv(DATASET_PATH)
    
    print(f"Dataset shape: {data.shape}")
    print(f"Columns: {list(data.columns)}")
    
    # Drop the Index column if it exists
    if 'Index' in data.columns:
        data = data.drop('Index', axis=1)
        print("Dropped 'Index' column")
    
    # Separate features and target
    y = data['class']
    X = data.drop('class', axis=1)
    
    print(f"Features shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    print(f"Target distribution:\n{y.value_counts()}")
    
    return X, y

def train_catboost_model(X_train, y_train, X_test, y_test):
    """Train CatBoost classifier"""
    print("\n" + "="*50)
    print("Training CatBoost Classifier...")
    print("="*50)
    
    # Initialize CatBoost with optimal parameters
    cat = CatBoostClassifier(
        learning_rate=0.1,
        iterations=1000,
        depth=6,
        verbose=100,  # Print progress every 100 iterations
        random_state=42,
        eval_metric='Accuracy'
    )
    
    # Train the model
    cat.fit(
        X_train, y_train,
        eval_set=(X_test, y_test),
        early_stopping_rounds=50,
        verbose=True
    )
    
    return cat

def evaluate_model(model, X_train, y_train, X_test, y_test):
    """Evaluate the trained model"""
    print("\n" + "="*50)
    print("Model Evaluation")
    print("="*50)
    
    # Make predictions
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    # Training metrics
    acc_train = metrics.accuracy_score(y_train, y_train_pred)
    f1_train = metrics.f1_score(y_train, y_train_pred, average='macro')
    recall_train = metrics.recall_score(y_train, y_train_pred, average='macro')
    precision_train = metrics.precision_score(y_train, y_train_pred, average='macro')
    
    # Test metrics
    acc_test = metrics.accuracy_score(y_test, y_test_pred)
    f1_test = metrics.f1_score(y_test, y_test_pred, average='macro')
    recall_test = metrics.recall_score(y_test, y_test_pred, average='macro')
    precision_test = metrics.precision_score(y_test, y_test_pred, average='macro')
    
    # Print results
    print("\n📊 Training Set Performance:")
    print(f"   Accuracy:  {acc_train:.4f}")
    print(f"   F1-Score:  {f1_train:.4f}")
    print(f"   Recall:    {recall_train:.4f}")
    print(f"   Precision: {precision_train:.4f}")
    
    print("\n📊 Test Set Performance:")
    print(f"   Accuracy:  {acc_test:.4f}")
    print(f"   F1-Score:  {f1_test:.4f}")
    print(f"   Recall:    {recall_test:.4f}")
    print(f"   Precision: {precision_test:.4f}")
    
    # Classification report
    print("\n📋 Classification Report (Test Set):")
    print(metrics.classification_report(y_test, y_test_pred))
    
    # Confusion matrix
    print("\n🔢 Confusion Matrix (Test Set):")
    cm = metrics.confusion_matrix(y_test, y_test_pred)
    print(cm)
    
    return {
        'accuracy': acc_test,
        'f1_score': f1_test,
        'recall': recall_test,
        'precision': precision_test
    }

def save_model(model, output_path):
    """Save the trained model using joblib"""
    print("\n" + "="*50)
    print("Saving Model...")
    print("="*50)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save model
    joblib.dump(model, output_path)
    print(f"✅ Model saved successfully to: {output_path}")
    
    # Verify file size
    file_size = os.path.getsize(output_path) / (1024 * 1024)  # Convert to MB
    print(f"📦 Model file size: {file_size:.2f} MB")

def main():
    """Main training pipeline"""
    print("="*50)
    print("CatBoost Phishing Detection Model Training")
    print("="*50)
    
    # Load data
    X, y = load_and_prepare_data()
    
    # Split data (80-20 split)
    print("\nSplitting data (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"Training set size: {X_train.shape[0]}")
    print(f"Test set size: {X_test.shape[0]}")
    
    # Train model
    model = train_catboost_model(X_train, y_train, X_test, y_test)
    
    # Evaluate model
    metrics_dict = evaluate_model(model, X_train, y_train, X_test, y_test)
    
    # Save model
    save_model(model, MODEL_OUTPUT_PATH)
    
    print("\n" + "="*50)
    print("✅ Training Complete!")
    print("="*50)
    print(f"\n📈 Final Test Accuracy: {metrics_dict['accuracy']:.4f}")
    print(f"📈 Final Test F1-Score: {metrics_dict['f1_score']:.4f}")
    print(f"\n🎯 Model is ready for integration!")

if __name__ == "__main__":
    main()
