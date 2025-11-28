# ScamCap: AI-Powered Browser Extension for Phishing & Deepfake Protection

## Project Overview

ScamCap is a comprehensive AI-powered browser extension that protects users from phishing attacks and deepfake threats by analyzing web content in real-time. The system combines advanced machine learning models with adaptive security measures to provide robust protection against modern cyber threats.

## Features

### 🛡️ Real-Time Protection
- **Phishing Detection**: BERT-based NLP analysis of URLs, content, and domains
- **Deepfake Detection**: EfficientNet CNN analysis of images and videos
- **Adaptive MFA**: Context-aware multi-factor authentication via SMS/email
- **Threat Logging**: Comprehensive logging and analytics for security insights

### 🔧 Technical Architecture
- **Chrome Extension**: Manifest V3 with service workers and content scripts
- **Backend API**: FastAPI with async/await patterns and MongoDB
- **ML Models**: PyTorch-based BERT and EfficientNet implementations
- **Deployment**: Docker containerization with AWS deployment scripts

## Project Structure

```
ScamCap Extension/
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── config/
│   │   │   └── settings.py    # Configuration management
│   │   ├── models/
│   │   │   └── schemas.py     # Pydantic data models
│   │   ├── services/          # Business logic services
│   │   │   ├── phishing_detector.py
│   │   │   ├── deepfake_detector.py
│   │   │   ├── auth_service.py
│   │   │   ├── mfa_service.py
│   │   │   └── threat_logger.py
│   │   ├── api/               # API route handlers
│   │   │   ├── phishing.py
│   │   │   ├── deepfake.py
│   │   │   ├── auth.py
│   │   │   └── mfa.py
│   │   └── utils/
│   │       └── database.py    # Database connection
├── extension/                  # Chrome extension files
│   ├── manifest.json          # Extension configuration
│   ├── background/
│   │   └── service-worker.js  # Background processing
│   ├── content/
│   │   └── content-script.js  # Page content analysis
│   └── popup/                 # Extension popup interface
│       ├── popup.html
│       ├── popup.css
│       └── popup.js
├── ml-models/                  # Machine learning components
│   ├── phishing/
│   │   └── train_phishing_model.py
│   └── deepfake/
│       └── train_deepfake_model.py
├── deployment/                 # Deployment configurations
│   ├── nginx.conf
│   ├── mongo-init.js
│   ├── aws-deploy.sh
│   └── user-data.sh
├── tests/                      # Test suites
│   ├── test_backend.py
│   └── test_extension.js
├── Dockerfile                  # Container configuration
├── docker-compose.yml         # Multi-service orchestration
└── requirements.txt           # Python dependencies
```

## Quick Start

### 1. Environment Setup

Create a Python virtual environment on external drive (as requested):

```powershell
# Create virtual environment on D: drive
mkdir "D:\venvs"
python -m venv "D:\venvs\scamcap"

# Activate virtual environment
& "D:\venvs\scamcap\Scripts\Activate.ps1"

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

Install and start MongoDB:

```powershell
# Start MongoDB (if installed locally)
mongod

# Or use Docker
docker run -d -p 27017:27017 --name mongodb mongo:5.0
```

### 3. Configure Environment Variables

Create `.env` file:

```env
MONGODB_URL=mongodb://localhost:27017/scamcap
JWT_SECRET_KEY=your-secret-key-here
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-phone
FIREBASE_SERVICE_ACCOUNT=path/to/firebase-service-account.json
```

### 4. Start Backend Service

```powershell
# Activate virtual environment
& "D:\venvs\scamcap\Scripts\Activate.ps1"

# Start FastAPI server
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Install Chrome Extension

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" and select the `extension/` folder
4. Pin the ScamCap extension to your toolbar

## Training ML Models

### Phishing Detection Model

```powershell
# Activate virtual environment
& "D:\venvs\scamcap\Scripts\Activate.ps1"

# Train phishing detection model
python ml-models/phishing/train_phishing_model.py
```

### Deepfake Detection Model

```powershell
# Train deepfake detection model
python ml-models/deepfake/train_deepfake_model.py
```

## Docker Deployment

### Local Development

```powershell
# Build and start all services
docker-compose up --build

# Access API at http://localhost:8000
# MongoDB at localhost:27017
```

### Production Deployment

```bash
# Deploy to AWS (Linux/WSL)
chmod +x deployment/aws-deploy.sh
./deployment/aws-deploy.sh
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Analysis
- `POST /api/analyze/phishing` - Analyze URL/content for phishing
- `POST /api/analyze/deepfake` - Analyze image/video for deepfakes

### MFA
- `POST /api/mfa/challenge` - Generate MFA challenge
- `POST /api/mfa/verify` - Verify MFA response

### Monitoring
- `GET /health` - Health check
- `GET /api/threats/history` - User threat history

## Extension Usage

### Automatic Protection
- The extension automatically scans web pages for threats
- Real-time analysis of forms, links, and media content
- Visual indicators for detected threats

### Manual Scanning
- Click the extension icon to manually scan current page
- View threat statistics and recent detections
- Configure protection settings

### Threat Responses
- High-risk threats trigger MFA challenges
- Visual warnings overlay suspicious content
- Detailed threat information in popup

## Testing

### Backend Tests

```powershell
# Run Python tests
pytest tests/test_backend.py -v
```

### Extension Tests

```powershell
# Install Jest (if not installed)
npm install -g jest

# Run JavaScript tests
jest tests/test_extension.js
```

## Configuration

### Backend Settings

Edit `backend/app/config/settings.py`:

```python
# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000

# ML Model Paths
PHISHING_MODEL_PATH = "ml-models/phishing/bert_phishing_model.pth"
DEEPFAKE_MODEL_PATH = "ml-models/deepfake/efficientnet_deepfake_model.pth"

# Risk Thresholds
PHISHING_RISK_THRESHOLD = 0.7
DEEPFAKE_RISK_THRESHOLD = 0.8
MFA_TRIGGER_THRESHOLD = 0.9
```

### Extension Settings

Configure in `extension/popup/popup.js`:

```javascript
const settings = {
  apiEndpoint: 'https://api.scamcap.com',
  enableRealTimeScanning: true,
  showThreatNotifications: true,
  mfaMethod: 'sms' // or 'email'
};
```

## Security Considerations

### Data Privacy
- All analysis is performed on secure servers
- User data is encrypted in transit and at rest
- No sensitive information is stored locally

### API Security
- JWT-based authentication
- Rate limiting on all endpoints
- CORS configuration for extension origins only

### ML Model Security
- Models are validated before deployment
- Regular retraining with updated threat data
- Adversarial attack detection

## Monitoring and Analytics

### Threat Logging
- All detected threats are logged with metadata
- User-specific threat histories
- Aggregate analytics for threat trends

### Performance Monitoring
- API response time tracking
- ML model inference speed monitoring
- Extension performance metrics

## Troubleshooting

### Common Issues

**Extension not loading:**
- Check manifest.json syntax
- Verify all files are present
- Check browser console for errors

**API connection failed:**
- Verify backend server is running
- Check network connectivity
- Validate API endpoint configuration

**ML model errors:**
- Ensure PyTorch is installed correctly
- Verify model files exist and are accessible
- Check GPU/CUDA compatibility if using GPU

**Database connection issues:**
- Verify MongoDB is running
- Check connection string format
- Ensure database exists and is accessible

### Performance Optimization

**For better ML performance:**
- Use GPU acceleration when available
- Implement model quantization for faster inference
- Cache frequent predictions

**For API optimization:**
- Implement Redis caching
- Use async/await patterns consistently
- Optimize database queries with indexes

## Contributing

### Development Setup

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Install development dependencies
4. Make changes and add tests
5. Submit pull request

### Code Standards

- Follow PEP 8 for Python code
- Use ESLint for JavaScript code
- Add type hints for Python functions
- Include comprehensive tests for new features

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Contact: support@scamcap.com
- Documentation: https://docs.scamcap.com

## Roadmap

### Version 2.0 Features
- [ ] Real-time video deepfake detection
- [ ] Advanced phishing techniques detection
- [ ] Multi-language support
- [ ] Mobile browser extension support
- [ ] Advanced analytics dashboard

## 🛡️ Overview
ScamCap is an intelligent browser extension that protects users from phishing attacks and deepfake threats using real-time AI analysis and adaptive multi-factor authentication.

## 🏗️ Architecture
```
User → Browser Extension → AI API → Risk Assessment → Adaptive MFA → Secure Access
```

## 📁 Project Structure
```
ScamCap/
├── backend/                    # Python API service
│   ├── app/
│   │   ├── api/               # REST API endpoints
│   │   ├── config/            # Configuration management
│   │   ├── models/            # Database models
│   │   ├── services/          # Business logic
│   │   └── utils/             # Utility functions
│   ├── requirements.txt
│   └── Dockerfile
├── extension/                  # Chrome browser extension
│   ├── manifest.json
│   ├── popup/                 # Extension popup UI
│   ├── content/               # Content scripts
│   ├── background/            # Service workers
│   └── assets/                # Icons and resources
├── ml-models/                  # AI/ML models
│   ├── phishing/              # Phishing detection
│   ├── deepfake/              # Deepfake detection
│   └── training/              # Model training scripts
├── deployment/                 # Docker & cloud configs
├── tests/                      # Unit & integration tests
└── docs/                       # Documentation
```

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd ScamCap

# Setup virtual environment (external drive)
python -m venv D:\venvs\scamcap
D:\venvs\scamcap\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Database Setup
```bash
# Start MongoDB (Docker)
docker run -d -p 27017:27017 --name scamcap-mongo mongo:latest
```

### 3. API Service
```bash
cd backend
python app/main.py
```

### 4. Browser Extension
1. Open Chrome → Extensions → Developer mode
2. Load unpacked → Select `extension/` folder
3. Pin ScamCap extension to toolbar

## 🤖 AI Models

### Phishing Detection
- **Model**: Fine-tuned BERT for text classification
- **Features**: URL analysis, content scanning, domain reputation
- **Accuracy**: >95% on phishing datasets

### Deepfake Detection
- **Model**: EfficientNet-B4 CNN
- **Features**: Frame-level analysis, temporal consistency
- **Supported**: Images and videos up to 100MB

## 🔐 Security Features

### Adaptive MFA
- **Triggers**: Risk score ≥ 0.7 threshold
- **Methods**: SMS OTP, Email verification
- **Providers**: Twilio, Firebase Auth

### Real-time Protection
- **Content Scanning**: Text, links, media analysis
- **Risk Scoring**: 0.0 (safe) to 1.0 (dangerous)
- **User Alerts**: Visual indicators and notifications

## 📊 Monitoring & Logging
- **Threat Detection**: Real-time logs and analytics
- **Performance**: API response times and accuracy metrics
- **User Activity**: Anonymized usage patterns

## 🌐 Deployment
- **Cloud**: AWS EC2 + S3 storage
- **Database**: MongoDB Atlas
- **Containers**: Docker with auto-scaling
- **CDN**: CloudFront for global distribution

## 📝 License
MIT License - see LICENSE file for details
