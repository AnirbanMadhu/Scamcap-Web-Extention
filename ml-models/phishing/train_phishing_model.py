"""
Phishing Detection Model Training Script
Uses BERT for text classification to detect phishing content
"""

import os
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
    AdamW, get_linear_schedule_with_warmup
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PhishingDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]

        # Tokenize text
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class PhishingBERTClassifier(nn.Module):
    def __init__(self, model_name, num_classes=2, dropout=0.3):
        super(PhishingBERTClassifier, self).__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(self.bert.config.hidden_size, num_classes)

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
        # Use [CLS] token representation
        pooled_output = outputs.pooler_output
        output = self.dropout(pooled_output)
        logits = self.classifier(output)
        
        return logits

class PhishingModelTrainer:
    def __init__(self, model_name='bert-base-uncased', max_length=512, batch_size=16):
        self.model_name = model_name
        self.max_length = max_length
        self.batch_size = batch_size
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Model will be initialized in train method
        self.model = None
        
        logger.info(f"Using device: {self.device}")

    def load_data(self, data_path):
        """Load and preprocess phishing dataset"""
        logger.info(f"Loading data from {data_path}")
        
        # Load CSV data (expected format: text, label)
        df = pd.read_csv(data_path)
        
        # Clean and preprocess text
        df['text'] = df['text'].astype(str)
        df['text'] = df['text'].str.lower()
        df['text'] = df['text'].str.replace(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '[URL]', regex=True)
        df['text'] = df['text'].str.replace(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', regex=True)
        
        # Balance dataset if needed
        if 'label' in df.columns:
            # Ensure binary labels (0: legitimate, 1: phishing)
            df['label'] = df['label'].astype(int)
            
            # Balance classes
            min_class_count = df['label'].value_counts().min()
            df_balanced = df.groupby('label').sample(min_class_count, random_state=42)
            
            logger.info(f"Dataset shape: {df_balanced.shape}")
            logger.info(f"Class distribution:\n{df_balanced['label'].value_counts()}")
            
            return df_balanced['text'].values, df_balanced['label'].values
        else:
            raise ValueError("Dataset must contain 'label' column")

    def create_data_loaders(self, texts, labels, test_size=0.2, val_size=0.1):
        """Create train, validation, and test data loaders"""
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=test_size, random_state=42, stratify=labels
        )
        
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train, test_size=val_size, random_state=42, stratify=y_train
        )
        
        # Create datasets
        train_dataset = PhishingDataset(X_train, y_train, self.tokenizer, self.max_length)
        val_dataset = PhishingDataset(X_val, y_val, self.tokenizer, self.max_length)
        test_dataset = PhishingDataset(X_test, y_test, self.tokenizer, self.max_length)
        
        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.batch_size, shuffle=False)
        test_loader = DataLoader(test_dataset, batch_size=self.batch_size, shuffle=False)
        
        logger.info(f"Train samples: {len(train_dataset)}")
        logger.info(f"Validation samples: {len(val_dataset)}")
        logger.info(f"Test samples: {len(test_dataset)}")
        
        return train_loader, val_loader, test_loader

    def train(self, train_loader, val_loader, epochs=3, learning_rate=2e-5):
        """Train the phishing detection model"""
        
        # Initialize model
        self.model = PhishingBERTClassifier(self.model_name)
        self.model.to(self.device)
        
        # Setup optimizer and scheduler
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)
        total_steps = len(train_loader) * epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=0,
            num_training_steps=total_steps
        )
        
        # Loss function
        criterion = nn.CrossEntropyLoss()
        
        # Training loop
        train_losses = []
        val_losses = []
        val_accuracies = []
        
        for epoch in range(epochs):
            logger.info(f"Epoch {epoch + 1}/{epochs}")
            
            # Training
            self.model.train()
            total_train_loss = 0
            
            for batch in tqdm(train_loader, desc="Training"):
                # Move batch to device
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                # Clear gradients
                optimizer.zero_grad()
                
                # Forward pass
                logits = self.model(input_ids, attention_mask)
                loss = criterion(logits, labels)
                
                # Backward pass
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                
                total_train_loss += loss.item()
            
            avg_train_loss = total_train_loss / len(train_loader)
            train_losses.append(avg_train_loss)
            
            # Validation
            val_loss, val_accuracy = self.evaluate(val_loader)
            val_losses.append(val_loss)
            val_accuracies.append(val_accuracy)
            
            logger.info(f"Average training loss: {avg_train_loss:.4f}")
            logger.info(f"Validation loss: {val_loss:.4f}")
            logger.info(f"Validation accuracy: {val_accuracy:.4f}")
            
        return {
            'train_losses': train_losses,
            'val_losses': val_losses,
            'val_accuracies': val_accuracies
        }

    def evaluate(self, data_loader):
        """Evaluate model on validation/test set"""
        self.model.eval()
        
        total_loss = 0
        predictions = []
        true_labels = []
        
        criterion = nn.CrossEntropyLoss()
        
        with torch.no_grad():
            for batch in data_loader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                logits = self.model(input_ids, attention_mask)
                loss = criterion(logits, labels)
                
                total_loss += loss.item()
                
                # Get predictions
                preds = torch.argmax(logits, dim=1)
                predictions.extend(preds.cpu().numpy())
                true_labels.extend(labels.cpu().numpy())
        
        avg_loss = total_loss / len(data_loader)
        accuracy = accuracy_score(true_labels, predictions)
        
        return avg_loss, accuracy

    def test_model(self, test_loader):
        """Comprehensive evaluation on test set"""
        logger.info("Running final evaluation on test set...")
        
        self.model.eval()
        predictions = []
        true_labels = []
        probabilities = []
        
        with torch.no_grad():
            for batch in tqdm(test_loader, desc="Testing"):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                logits = self.model(input_ids, attention_mask)
                probs = torch.softmax(logits, dim=1)
                preds = torch.argmax(logits, dim=1)
                
                predictions.extend(preds.cpu().numpy())
                true_labels.extend(labels.cpu().numpy())
                probabilities.extend(probs.cpu().numpy())
        
        # Calculate metrics
        accuracy = accuracy_score(true_labels, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            true_labels, predictions, average='binary'
        )
        
        # Confusion matrix
        cm = confusion_matrix(true_labels, predictions)
        
        results = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'confusion_matrix': cm.tolist()
        }
        
        logger.info(f"Test Accuracy: {accuracy:.4f}")
        logger.info(f"Test Precision: {precision:.4f}")
        logger.info(f"Test Recall: {recall:.4f}")
        logger.info(f"Test F1-Score: {f1:.4f}")
        
        return results

    def save_model(self, model_path, tokenizer_path=None):
        """Save trained model and tokenizer"""
        logger.info(f"Saving model to {model_path}")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save model state dict
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'model_name': self.model_name,
            'max_length': self.max_length
        }, model_path)
        
        # Save tokenizer
        if tokenizer_path:
            self.tokenizer.save_pretrained(tokenizer_path)
        
        logger.info("Model saved successfully")

    def load_model(self, model_path):
        """Load trained model"""
        logger.info(f"Loading model from {model_path}")
        
        checkpoint = torch.load(model_path, map_location=self.device)
        
        self.model = PhishingBERTClassifier(checkpoint['model_name'])
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.to(self.device)
        self.model.eval()
        
        self.max_length = checkpoint['max_length']
        
        logger.info("Model loaded successfully")

    def predict(self, texts):
        """Make predictions on new texts"""
        self.model.eval()
        
        if isinstance(texts, str):
            texts = [texts]
        
        predictions = []
        probabilities = []
        
        with torch.no_grad():
            for text in texts:
                # Tokenize
                encoding = self.tokenizer(
                    text,
                    truncation=True,
                    padding='max_length',
                    max_length=self.max_length,
                    return_tensors='pt'
                )
                
                input_ids = encoding['input_ids'].to(self.device)
                attention_mask = encoding['attention_mask'].to(self.device)
                
                # Predict
                logits = self.model(input_ids, attention_mask)
                probs = torch.softmax(logits, dim=1)
                pred = torch.argmax(logits, dim=1)
                
                predictions.append(pred.item())
                probabilities.append(probs[0][1].item())  # Probability of phishing class
        
        return predictions, probabilities

def main():
    """Main training script"""
    
    # Configuration
    config = {
        'data_path': 'data/phishing_dataset.csv',
        'model_name': 'bert-base-uncased',
        'max_length': 512,
        'batch_size': 16,
        'epochs': 3,
        'learning_rate': 2e-5,
        'model_save_path': '../../ml-models/phishing/bert_phishing_model.pth',
        'tokenizer_save_path': '../../ml-models/phishing/tokenizer'
    }
    
    # Initialize trainer
    trainer = PhishingModelTrainer(
        model_name=config['model_name'],
        max_length=config['max_length'],
        batch_size=config['batch_size']
    )
    
    # Load data
    texts, labels = trainer.load_data(config['data_path'])
    
    # Create data loaders
    train_loader, val_loader, test_loader = trainer.create_data_loaders(texts, labels)
    
    # Train model
    history = trainer.train(
        train_loader, 
        val_loader, 
        epochs=config['epochs'],
        learning_rate=config['learning_rate']
    )
    
    # Test model
    test_results = trainer.test_model(test_loader)
    
    # Save model
    trainer.save_model(config['model_save_path'], config['tokenizer_save_path'])
    
    # Save training history and results
    results = {
        'config': config,
        'training_history': history,
        'test_results': test_results
    }
    
    with open('../../ml-models/phishing/training_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info("Training completed successfully!")

if __name__ == "__main__":
    main()
