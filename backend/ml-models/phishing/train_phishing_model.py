"""
Phishing Detection Model Training Script
Uses Neural Network for URL feature-based classification to detect phishing
Compatible with Kaggle phishing dataset with URL features
"""

import os
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report, roc_auc_score
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import logging
import json
import joblib

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PhishingDataset(Dataset):
    """Dataset class for phishing URL features"""
    def __init__(self, features, labels):
        self.features = torch.FloatTensor(features)
        self.labels = torch.FloatTensor(labels)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {
            'features': self.features[idx],
            'labels': self.labels[idx]
        }


class PhishingNeuralNetwork(nn.Module):
    """Neural Network for Phishing Detection based on URL features"""
    def __init__(self, input_size, hidden_sizes=[128, 64, 32], dropout=0.3):
        super(PhishingNeuralNetwork, self).__init__()
        
        layers = []
        prev_size = input_size
        
        for hidden_size in hidden_sizes:
            layers.extend([
                nn.Linear(prev_size, hidden_size),
                nn.BatchNorm1d(hidden_size),
                nn.ReLU(),
                nn.Dropout(dropout)
            ])
            prev_size = hidden_size
        
        # Output layer (no sigmoid here - we'll use BCEWithLogitsLoss for training)
        layers.append(nn.Linear(prev_size, 1))
        
        self.network = nn.Sequential(*layers)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x, apply_sigmoid=False):
        logits = self.network(x)
        if apply_sigmoid:
            return self.sigmoid(logits)
        return logits


class PhishingModelTrainer:
    """Trainer class for phishing detection model"""
    
    def __init__(self, hidden_sizes=[128, 64, 32], dropout=0.3, batch_size=64):
        self.hidden_sizes = hidden_sizes
        self.dropout = dropout
        self.batch_size = batch_size
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.scaler = StandardScaler()
        self.model = None
        self.feature_columns = None
        
        logger.info(f"Using device: {self.device}")

    def load_data(self, data_path):
        """Load and preprocess phishing dataset from Kaggle"""
        logger.info(f"Loading data from {data_path}")
        
        # Load CSV data
        df = pd.read_csv(data_path)
        
        logger.info(f"Dataset shape: {df.shape}")
        logger.info(f"Columns: {df.columns.tolist()}")
        
        # Handle different column name formats
        # Check for 'Phising' or 'Phishing' or 'label' or 'Label'
        label_column = None
        for col in ['Phising', 'Phishing', 'phishing', 'label', 'Label', 'class', 'Class']:
            if col in df.columns:
                label_column = col
                break
        
        if label_column is None:
            raise ValueError("Could not find label column. Expected: Phising, Phishing, label, or class")
        
        logger.info(f"Using label column: {label_column}")
        
        # Remove unnamed/index columns
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # Separate features and labels
        feature_columns = [col for col in df.columns if col != label_column]
        self.feature_columns = feature_columns
        
        X = df[feature_columns].values
        y = df[label_column].values
        
        # Handle NaN values
        X = np.nan_to_num(X, nan=0.0)
        
        # Convert labels to binary (0 or 1)
        y = (y >= 0.5).astype(int)
        
        logger.info(f"Number of features: {len(feature_columns)}")
        logger.info(f"Feature columns: {feature_columns}")
        logger.info(f"Class distribution:")
        logger.info(f"  Legitimate (0): {np.sum(y == 0)}")
        logger.info(f"  Phishing (1): {np.sum(y == 1)}")
        
        return X, y

    def create_data_loaders(self, X, y, test_size=0.2, val_size=0.1):
        """Create train, validation, and test data loaders with class balancing"""
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train, test_size=val_size, random_state=42, stratify=y_train
        )
        
        # Calculate class weights for imbalanced dataset
        class_counts = np.bincount(y_train.astype(int))
        total_samples = len(y_train)
        self.class_weights = torch.FloatTensor([
            total_samples / (2 * class_counts[0]),  # Weight for class 0 (legitimate)
            total_samples / (2 * class_counts[1])   # Weight for class 1 (phishing)
        ])
        logger.info(f"Class weights: Legitimate={self.class_weights[0]:.4f}, Phishing={self.class_weights[1]:.4f}")
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Create datasets
        train_dataset = PhishingDataset(X_train_scaled, y_train)
        val_dataset = PhishingDataset(X_val_scaled, y_val)
        test_dataset = PhishingDataset(X_test_scaled, y_test)
        
        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.batch_size, shuffle=False)
        test_loader = DataLoader(test_dataset, batch_size=self.batch_size, shuffle=False)
        
        logger.info(f"Train samples: {len(train_dataset)}")
        logger.info(f"Validation samples: {len(val_dataset)}")
        logger.info(f"Test samples: {len(test_dataset)}")
        
        return train_loader, val_loader, test_loader, X.shape[1]

    def train(self, train_loader, val_loader, input_size, epochs=50, learning_rate=0.001):
        """Train the phishing detection model with class-weighted loss"""
        
        # Initialize model
        self.model = PhishingNeuralNetwork(
            input_size=input_size,
            hidden_sizes=self.hidden_sizes,
            dropout=self.dropout
        )
        self.model.to(self.device)
        
        # Setup optimizer and scheduler
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate, weight_decay=1e-5)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', patience=5, factor=0.5)
        
        # Use weighted BCE loss to handle class imbalance
        pos_weight = self.class_weights[1] / self.class_weights[0]
        criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([pos_weight]).to(self.device))
        
        # Training tracking
        train_losses = []
        val_losses = []
        val_accuracies = []
        val_f1_scores = []
        best_val_f1 = 0
        best_model_state = None
        patience_counter = 0
        early_stopping_patience = 15
        
        logger.info(f"\n{'='*60}")
        logger.info("Starting Training...")
        logger.info(f"{'='*60}")
        
        for epoch in range(epochs):
            # Training phase
            self.model.train()
            total_train_loss = 0
            
            for batch in train_loader:
                features = batch['features'].to(self.device)
                labels = batch['labels'].to(self.device).unsqueeze(1)
                
                # Clear gradients
                optimizer.zero_grad()
                
                # Forward pass (logits, no sigmoid)
                outputs = self.model(features, apply_sigmoid=False)
                loss = criterion(outputs, labels)
                
                # Backward pass
                loss.backward()
                optimizer.step()
                
                total_train_loss += loss.item()
            
            avg_train_loss = total_train_loss / len(train_loader)
            train_losses.append(avg_train_loss)
            
            # Validation phase
            val_loss, val_accuracy, val_f1 = self.evaluate(val_loader, criterion)
            val_losses.append(val_loss)
            val_accuracies.append(val_accuracy)
            val_f1_scores.append(val_f1)
            
            # Learning rate scheduling based on F1 score
            scheduler.step(val_f1)
            
            # Early stopping check based on F1 score (better for imbalanced data)
            if val_f1 > best_val_f1:
                best_val_f1 = val_f1
                best_model_state = self.model.state_dict().copy()
                patience_counter = 0
            else:
                patience_counter += 1
            
            # Log progress
            if (epoch + 1) % 5 == 0 or epoch == 0:
                logger.info(f"Epoch [{epoch+1}/{epochs}] - Train Loss: {avg_train_loss:.4f} - Val Loss: {val_loss:.4f} - Val Acc: {val_accuracy:.4f} - Val F1: {val_f1:.4f}")
            
            # Early stopping
            if patience_counter >= early_stopping_patience:
                logger.info(f"Early stopping triggered at epoch {epoch+1}")
                break
        
        # Load best model
        if best_model_state is not None:
            self.model.load_state_dict(best_model_state)
            logger.info(f"Loaded best model with validation F1: {best_val_f1:.4f}")
        
        return {
            'train_losses': train_losses,
            'val_losses': val_losses,
            'val_accuracies': val_accuracies,
            'val_f1_scores': val_f1_scores,
            'best_val_f1': best_val_f1
        }

    def evaluate(self, data_loader, criterion=None):
        """Evaluate model on validation/test set"""
        self.model.eval()
        
        total_loss = 0
        predictions = []
        true_labels = []
        
        if criterion is None:
            criterion = nn.BCEWithLogitsLoss()
        
        with torch.no_grad():
            for batch in data_loader:
                features = batch['features'].to(self.device)
                labels = batch['labels'].to(self.device).unsqueeze(1)
                
                outputs = self.model(features, apply_sigmoid=False)
                loss = criterion(outputs, labels)
                
                total_loss += loss.item()
                
                # Get predictions (apply sigmoid then threshold at 0.5)
                probs = torch.sigmoid(outputs)
                preds = (probs >= 0.5).float()
                predictions.extend(preds.cpu().numpy().flatten())
                true_labels.extend(labels.cpu().numpy().flatten())
        
        avg_loss = total_loss / len(data_loader)
        accuracy = accuracy_score(true_labels, predictions)
        _, _, f1, _ = precision_recall_fscore_support(true_labels, predictions, average='binary', zero_division=0)
        
        return avg_loss, accuracy, f1

    def test_model(self, test_loader):
        """Comprehensive evaluation on test set"""
        logger.info(f"\n{'='*60}")
        logger.info("Running Final Evaluation on Test Set...")
        logger.info(f"{'='*60}")
        
        self.model.eval()
        predictions = []
        true_labels = []
        probabilities = []
        
        with torch.no_grad():
            for batch in test_loader:
                features = batch['features'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(features, apply_sigmoid=True)
                preds = (outputs >= 0.5).float()
                
                predictions.extend(preds.cpu().numpy().flatten())
                true_labels.extend(labels.cpu().numpy().flatten())
                probabilities.extend(outputs.cpu().numpy().flatten())
        
        # Convert to numpy arrays
        predictions = np.array(predictions)
        true_labels = np.array(true_labels)
        probabilities = np.array(probabilities)
        
        # Calculate metrics
        accuracy = accuracy_score(true_labels, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            true_labels, predictions, average='binary'
        )
        roc_auc = roc_auc_score(true_labels, probabilities)
        
        # Confusion matrix
        cm = confusion_matrix(true_labels, predictions)
        
        # Classification report
        report = classification_report(true_labels, predictions, target_names=['Legitimate', 'Phishing'])
        
        results = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'roc_auc': float(roc_auc),
            'confusion_matrix': cm.tolist()
        }
        
        logger.info(f"\n{report}")
        logger.info(f"\nTest Metrics:")
        logger.info(f"  Accuracy:  {accuracy:.4f}")
        logger.info(f"  Precision: {precision:.4f}")
        logger.info(f"  Recall:    {recall:.4f}")
        logger.info(f"  F1-Score:  {f1:.4f}")
        logger.info(f"  ROC-AUC:   {roc_auc:.4f}")
        logger.info(f"\nConfusion Matrix:")
        logger.info(f"  TN: {cm[0][0]}  FP: {cm[0][1]}")
        logger.info(f"  FN: {cm[1][0]}  TP: {cm[1][1]}")
        
        # Plot confusion matrix
        self.plot_confusion_matrix(cm)
        
        return results

    def plot_confusion_matrix(self, cm):
        """Plot and save confusion matrix"""
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=['Legitimate', 'Phishing'],
                    yticklabels=['Legitimate', 'Phishing'])
        plt.title('Confusion Matrix - Phishing Detection')
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        plt.tight_layout()
        plt.savefig('confusion_matrix.png', dpi=150)
        plt.close()
        logger.info("Confusion matrix saved to confusion_matrix.png")

    def plot_training_history(self, history):
        """Plot training history"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Loss plot
        axes[0].plot(history['train_losses'], label='Train Loss', color='blue')
        axes[0].plot(history['val_losses'], label='Validation Loss', color='orange')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Loss')
        axes[0].set_title('Training and Validation Loss')
        axes[0].legend()
        axes[0].grid(True)
        
        # Accuracy plot
        axes[1].plot(history['val_accuracies'], label='Validation Accuracy', color='green')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Accuracy')
        axes[1].set_title('Validation Accuracy')
        axes[1].legend()
        axes[1].grid(True)
        
        plt.tight_layout()
        plt.savefig('training_history.png', dpi=150)
        plt.close()
        logger.info("Training history plot saved to training_history.png")

    def save_model(self, model_path):
        """Save trained model, scaler, and configuration"""
        logger.info(f"Saving model to {model_path}")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path) if os.path.dirname(model_path) else '.', exist_ok=True)
        
        # Save model state dict and configuration
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'input_size': self.model.network[0].in_features,
            'hidden_sizes': self.hidden_sizes,
            'dropout': self.dropout,
            'feature_columns': self.feature_columns
        }, model_path)
        
        # Save scaler
        scaler_path = model_path.replace('.pth', '_scaler.pkl')
        joblib.dump(self.scaler, scaler_path)
        
        logger.info(f"Model saved to {model_path}")
        logger.info(f"Scaler saved to {scaler_path}")

    def load_model(self, model_path):
        """Load trained model"""
        logger.info(f"Loading model from {model_path}")
        
        checkpoint = torch.load(model_path, map_location=self.device)
        
        self.model = PhishingNeuralNetwork(
            input_size=checkpoint['input_size'],
            hidden_sizes=checkpoint['hidden_sizes'],
            dropout=checkpoint['dropout']
        )
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.to(self.device)
        self.model.eval()
        
        self.feature_columns = checkpoint['feature_columns']
        self.hidden_sizes = checkpoint['hidden_sizes']
        self.dropout = checkpoint['dropout']
        
        # Load scaler
        scaler_path = model_path.replace('.pth', '_scaler.pkl')
        if os.path.exists(scaler_path):
            self.scaler = joblib.load(scaler_path)
        
        logger.info("Model loaded successfully")

    def predict(self, features):
        """Make predictions on new URL features"""
        self.model.eval()
        
        if isinstance(features, pd.DataFrame):
            features = features.values
        elif isinstance(features, list):
            features = np.array(features)
        
        # Ensure 2D array
        if features.ndim == 1:
            features = features.reshape(1, -1)
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Convert to tensor
        features_tensor = torch.FloatTensor(features_scaled).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(features_tensor, apply_sigmoid=True)
            probabilities = outputs.cpu().numpy().flatten()
            predictions = (probabilities >= 0.5).astype(int)
        
        return predictions, probabilities


def main():
    """Main training script"""
    
    print("\n" + "="*60)
    print("   ScamCap Phishing Detection Model Training")
    print("="*60 + "\n")
    
    # Configuration
    config = {
        'data_path': 'Phising_Detection_Dataset.csv',
        'hidden_sizes': [128, 64, 32],
        'dropout': 0.3,
        'batch_size': 64,
        'epochs': 100,
        'learning_rate': 0.001,
        'model_save_path': 'phishing_model.pth'
    }
    
    logger.info("Configuration:")
    for key, value in config.items():
        logger.info(f"  {key}: {value}")
    
    # Initialize trainer
    trainer = PhishingModelTrainer(
        hidden_sizes=config['hidden_sizes'],
        dropout=config['dropout'],
        batch_size=config['batch_size']
    )
    
    # Load data
    X, y = trainer.load_data(config['data_path'])
    
    # Create data loaders
    train_loader, val_loader, test_loader, input_size = trainer.create_data_loaders(X, y)
    
    # Train model
    history = trainer.train(
        train_loader, 
        val_loader,
        input_size=input_size,
        epochs=config['epochs'],
        learning_rate=config['learning_rate']
    )
    
    # Plot training history
    trainer.plot_training_history(history)
    
    # Test model
    test_results = trainer.test_model(test_loader)
    
    # Save model
    trainer.save_model(config['model_save_path'])
    
    # Save training results
    results = {
        'config': config,
        'training_history': {
            'train_losses': history['train_losses'],
            'val_losses': history['val_losses'],
            'val_accuracies': history['val_accuracies'],
            'val_f1_scores': history['val_f1_scores'],
            'best_val_f1': history['best_val_f1']
        },
        'test_results': test_results
    }
    
    with open('training_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "="*60)
    print("   Training Completed Successfully!")
    print("="*60)
    print(f"\n  Model saved to: {config['model_save_path']}")
    print(f"  Results saved to: training_results.json")
    print(f"  Final Test Accuracy: {test_results['accuracy']:.4f}")
    print(f"  Final Test F1-Score: {test_results['f1_score']:.4f}")
    print("\n")


if __name__ == "__main__":
    main()
