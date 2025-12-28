"""
Deepfake Detection Model Training Script
Uses EfficientNet-B4 CNN for image/video deepfake detection
"""

import os
import numpy as np
import pandas as pd
import cv2
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from torchvision import transforms, models
from PIL import Image
import albumentations as A
from albumentations.pytorch import ToTensorV2
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import logging
import json
import warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepfakeDataset(Dataset):
    def __init__(self, image_paths, labels, transform=None, face_detector=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform
        self.face_detector = face_detector

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        label = self.labels[idx]

        # Load image
        try:
            image = cv2.imread(image_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Extract face if detector is provided
            if self.face_detector is not None:
                faces = self.extract_faces(image)
                if len(faces) > 0:
                    # Use the largest face
                    face = max(faces, key=lambda x: x.shape[0] * x.shape[1])
                    image = face
            
            # Convert to PIL Image
            image = Image.fromarray(image)
            
            # Apply transforms
            if self.transform:
                image = self.transform(image)
            
            return image, torch.tensor(label, dtype=torch.long)
            
        except Exception as e:
            logger.warning(f"Error loading image {image_path}: {e}")
            # Return dummy data in case of error
            dummy_image = torch.zeros((3, 224, 224))
            return dummy_image, torch.tensor(label, dtype=torch.long)

    def extract_faces(self, image):
        """Extract faces from image using OpenCV"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            faces = self.face_detector.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            
            face_images = []
            for (x, y, w, h) in faces:
                face = image[y:y+h, x:x+w]
                if face.shape[0] > 50 and face.shape[1] > 50:  # Filter small faces
                    face_images.append(face)
            
            return face_images
            
        except Exception as e:
            logger.warning(f"Face extraction failed: {e}")
            return []

class EfficientNetDeepfake(nn.Module):
    def __init__(self, model_name='efficientnet_b4', num_classes=2, dropout=0.5):
        super(EfficientNetDeepfake, self).__init__()
        
        # Load pre-trained EfficientNet
        self.backbone = models.efficientnet_b4(pretrained=True)
        
        # Replace classifier
        in_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(in_features, 512),
            nn.ReLU(),
            nn.Dropout(dropout/2),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(dropout/4),
            nn.Linear(256, num_classes)
        )
        
        # Add attention mechanism
        self.attention = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(1792, 512, 1),  # EfficientNet-B4 has 1792 features
            nn.ReLU(),
            nn.Conv2d(512, 1792, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        # Extract features
        features = self.backbone.features(x)
        
        # Apply attention
        attention_weights = self.attention(features)
        features = features * attention_weights
        
        # Global average pooling and classification
        x = self.backbone.avgpool(features)
        x = torch.flatten(x, 1)
        x = self.backbone.classifier(x)
        
        return x

class DeepfakeModelTrainer:
    def __init__(self, model_name='efficientnet_b4', img_size=224, batch_size=32):
        self.model_name = model_name
        self.img_size = img_size
        self.batch_size = batch_size
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize face detector
        self.face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Model will be initialized in train method
        self.model = None
        
        logger.info(f"Using device: {self.device}")

    def get_transforms(self, train=True):
        """Get image transforms for training and validation"""
        
        if train:
            # Training transforms with augmentation
            return A.Compose([
                A.Resize(self.img_size, self.img_size),
                A.HorizontalFlip(p=0.5),
                A.RandomBrightnessContrast(p=0.3),
                A.HueSaturationValue(p=0.3),
                A.OneOf([
                    A.GaussNoise(p=0.5),
                    A.GaussianBlur(p=0.5),
                    A.MotionBlur(p=0.5),
                ], p=0.3),
                A.OneOf([
                    A.Sharpen(p=0.5),
                    A.Emboss(p=0.5),
                    A.RandomGamma(p=0.5),
                ], p=0.3),
                A.Cutout(max_h_size=int(self.img_size * 0.1), 
                        max_w_size=int(self.img_size * 0.1), p=0.3),
                A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
                ToTensorV2(),
            ])
        else:
            # Validation transforms
            return A.Compose([
                A.Resize(self.img_size, self.img_size),
                A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
                ToTensorV2(),
            ])

    def load_data(self, data_dir):
        """Load deepfake dataset"""
        logger.info(f"Loading data from {data_dir}")
        
        image_paths = []
        labels = []
        
        # Expected structure: data_dir/real/, data_dir/fake/
        real_dir = os.path.join(data_dir, 'real')
        fake_dir = os.path.join(data_dir, 'fake')
        
        # Load real images (label 0)
        if os.path.exists(real_dir):
            for img_file in os.listdir(real_dir):
                if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_paths.append(os.path.join(real_dir, img_file))
                    labels.append(0)
        
        # Load fake images (label 1)
        if os.path.exists(fake_dir):
            for img_file in os.listdir(fake_dir):
                if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_paths.append(os.path.join(fake_dir, img_file))
                    labels.append(1)
        
        # Convert to numpy arrays
        image_paths = np.array(image_paths)
        labels = np.array(labels)
        
        # Shuffle data
        indices = np.random.permutation(len(image_paths))
        image_paths = image_paths[indices]
        labels = labels[indices]
        
        logger.info(f"Total images: {len(image_paths)}")
        logger.info(f"Real images: {sum(labels == 0)}")
        logger.info(f"Fake images: {sum(labels == 1)}")
        
        return image_paths, labels

    def create_data_loaders(self, image_paths, labels, test_size=0.2, val_size=0.1):
        """Create train, validation, and test data loaders"""
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            image_paths, labels, test_size=test_size, random_state=42, stratify=labels
        )
        
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train, test_size=val_size, random_state=42, stratify=y_train
        )
        
        # Create transforms
        train_transform = self.get_transforms(train=True)
        val_transform = self.get_transforms(train=False)
        
        # Create datasets
        train_dataset = DeepfakeDataset(
            X_train, y_train, 
            transform=train_transform, 
            face_detector=self.face_detector
        )
        val_dataset = DeepfakeDataset(
            X_val, y_val, 
            transform=val_transform, 
            face_detector=self.face_detector
        )
        test_dataset = DeepfakeDataset(
            X_test, y_test, 
            transform=val_transform, 
            face_detector=self.face_detector
        )
        
        # Create weighted sampler for balanced training
        class_counts = np.bincount(y_train)
        class_weights = 1.0 / class_counts
        sample_weights = class_weights[y_train]
        sampler = WeightedRandomSampler(
            weights=sample_weights, 
            num_samples=len(sample_weights), 
            replacement=True
        )
        
        # Create data loaders
        train_loader = DataLoader(
            train_dataset, 
            batch_size=self.batch_size, 
            sampler=sampler,
            num_workers=4,
            pin_memory=True
        )
        val_loader = DataLoader(
            val_dataset, 
            batch_size=self.batch_size, 
            shuffle=False,
            num_workers=4,
            pin_memory=True
        )
        test_loader = DataLoader(
            test_dataset, 
            batch_size=self.batch_size, 
            shuffle=False,
            num_workers=4,
            pin_memory=True
        )
        
        logger.info(f"Train samples: {len(train_dataset)}")
        logger.info(f"Validation samples: {len(val_dataset)}")
        logger.info(f"Test samples: {len(test_dataset)}")
        
        return train_loader, val_loader, test_loader

    def train(self, train_loader, val_loader, epochs=20, learning_rate=1e-4):
        """Train the deepfake detection model"""
        
        # Initialize model
        self.model = EfficientNetDeepfake(self.model_name)
        self.model.to(self.device)
        
        # Setup optimizer and scheduler
        optimizer = optim.AdamW(
            self.model.parameters(), 
            lr=learning_rate, 
            weight_decay=1e-4
        )
        scheduler = optim.lr_scheduler.CosineAnnealingLR(
            optimizer, T_max=epochs, eta_min=1e-6
        )
        
        # Loss function with label smoothing
        criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
        
        # Training loop
        train_losses = []
        val_losses = []
        val_accuracies = []
        best_val_acc = 0.0
        
        for epoch in range(epochs):
            logger.info(f"Epoch {epoch + 1}/{epochs}")
            
            # Training
            self.model.train()
            total_train_loss = 0
            train_correct = 0
            train_total = 0
            
            for images, labels in tqdm(train_loader, desc="Training"):
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                # Clear gradients
                optimizer.zero_grad()
                
                # Forward pass
                outputs = self.model(images)
                loss = criterion(outputs, labels)
                
                # Backward pass
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()
                
                total_train_loss += loss.item()
                
                # Calculate accuracy
                _, predicted = torch.max(outputs.data, 1)
                train_total += labels.size(0)
                train_correct += (predicted == labels).sum().item()
            
            avg_train_loss = total_train_loss / len(train_loader)
            train_accuracy = train_correct / train_total
            train_losses.append(avg_train_loss)
            
            # Validation
            val_loss, val_accuracy = self.evaluate(val_loader)
            val_losses.append(val_loss)
            val_accuracies.append(val_accuracy)
            
            # Update learning rate
            scheduler.step()
            current_lr = optimizer.param_groups[0]['lr']
            
            logger.info(f"Train Loss: {avg_train_loss:.4f}, Train Acc: {train_accuracy:.4f}")
            logger.info(f"Val Loss: {val_loss:.4f}, Val Acc: {val_accuracy:.4f}")
            logger.info(f"Learning Rate: {current_lr:.6f}")
            
            # Save best model
            if val_accuracy > best_val_acc:
                best_val_acc = val_accuracy
                torch.save(self.model.state_dict(), 'best_deepfake_model.pth')
                logger.info(f"New best model saved with validation accuracy: {val_accuracy:.4f}")
            
        return {
            'train_losses': train_losses,
            'val_losses': val_losses,
            'val_accuracies': val_accuracies,
            'best_val_accuracy': best_val_acc
        }

    def evaluate(self, data_loader):
        """Evaluate model on validation/test set"""
        self.model.eval()
        
        total_loss = 0
        correct = 0
        total = 0
        
        criterion = nn.CrossEntropyLoss()
        
        with torch.no_grad():
            for images, labels in data_loader:
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                outputs = self.model(images)
                loss = criterion(outputs, labels)
                
                total_loss += loss.item()
                
                # Calculate accuracy
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        avg_loss = total_loss / len(data_loader)
        accuracy = correct / total
        
        return avg_loss, accuracy

    def test_model(self, test_loader):
        """Comprehensive evaluation on test set"""
        logger.info("Running final evaluation on test set...")
        
        # Load best model
        self.model.load_state_dict(torch.load('best_deepfake_model.pth'))
        self.model.eval()
        
        predictions = []
        true_labels = []
        probabilities = []
        
        with torch.no_grad():
            for images, labels in tqdm(test_loader, desc="Testing"):
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                outputs = self.model(images)
                probs = torch.softmax(outputs, dim=1)
                preds = torch.argmax(outputs, dim=1)
                
                predictions.extend(preds.cpu().numpy())
                true_labels.extend(labels.cpu().numpy())
                probabilities.extend(probs.cpu().numpy())
        
        # Calculate metrics
        accuracy = accuracy_score(true_labels, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            true_labels, predictions, average='binary'
        )
        
        # Calculate AUC
        probs_fake = [p[1] for p in probabilities]  # Probability of fake class
        auc = roc_auc_score(true_labels, probs_fake)
        
        results = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'auc': auc
        }
        
        logger.info(f"Test Accuracy: {accuracy:.4f}")
        logger.info(f"Test Precision: {precision:.4f}")
        logger.info(f"Test Recall: {recall:.4f}")
        logger.info(f"Test F1-Score: {f1:.4f}")
        logger.info(f"Test AUC: {auc:.4f}")
        
        return results

    def save_model(self, model_path):
        """Save trained model"""
        logger.info(f"Saving model to {model_path}")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save model
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'model_name': self.model_name,
            'img_size': self.img_size
        }, model_path)
        
        logger.info("Model saved successfully")

def main():
    """Main training script"""
    
    # Configuration
    config = {
        'data_dir': 'data/deepfake_dataset',
        'model_name': 'efficientnet_b4',
        'img_size': 224,
        'batch_size': 32,
        'epochs': 20,
        'learning_rate': 1e-4,
        'model_save_path': '../../ml-models/deepfake/efficientnet_deepfake_model.pth'
    }
    
    # Initialize trainer
    trainer = DeepfakeModelTrainer(
        model_name=config['model_name'],
        img_size=config['img_size'],
        batch_size=config['batch_size']
    )
    
    # Load data
    image_paths, labels = trainer.load_data(config['data_dir'])
    
    # Create data loaders
    train_loader, val_loader, test_loader = trainer.create_data_loaders(image_paths, labels)
    
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
    trainer.save_model(config['model_save_path'])
    
    # Save training history and results
    results = {
        'config': config,
        'training_history': history,
        'test_results': test_results
    }
    
    with open('training_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info("Training completed successfully!")

if __name__ == "__main__":
    main()
