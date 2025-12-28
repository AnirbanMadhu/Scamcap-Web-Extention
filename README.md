# ScamCap - AI-Powered Browser Extension for Phishing & Deepfake Protection

## 🛡️ Overview
ScamCap is an intelligent browser extension that protects users from phishing attacks and deepfake threats using real-time AI analysis and adaptive multi-factor authentication.

## ✨ Features
- **Phishing Detection**: BERT-based NLP analysis of URLs and content
- **Deepfake Detection**: EfficientNet CNN analysis of images and videos
- **Adaptive MFA**: Context-aware multi-factor authentication
- **Real-time Protection**: Automatic scanning of web pages
- **Threat Logging**: Comprehensive security insights and analytics

## 📁 Project Structure
```
ScamCap/
├── backend/                    # FastAPI backend service
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── api/               # API endpoints
│   │   ├── config/            # Configuration
│   │   ├── models/            # Data models
│   │   └── services/          # Business logic
│   ├── extension/             # Chrome browser extension
│   │   ├── manifest.json
│   │   ├── popup/             # Extension UI
│   │   ├── content/           # Content scripts
│   │   └── background/        # Service worker
│   ├── ml-models/             # AI/ML models
│   │   ├── phishing/
│   │   └── deepfake/
│   └── requirements.txt
├── frontend/                   # Next.js website
│   └── src/
└── package.json
```

## 🚀 Quick Setup (Works on Any System)

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher (for frontend)
- MongoDB (local or cloud)
- Chrome/Edge browser

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/ScamCap-Web-Extension.git
cd ScamCap-Web-Extension
```

### 2. Backend Setup

**Windows:**
```powershell
# Install Python dependencies
pip install -r backend/requirements.txt

# Start backend server
python start_server.py
```

**macOS/Linux:**
```bash
# Install Python dependencies
pip3 install -r backend/requirements.txt

# Start backend server
python3 start_server.py
```

The backend will run on `http://localhost:8000`

### 3. Frontend Setup (Optional - for website)

**Windows:**
```powershell
cd frontend
npm install
npm run dev
```

**macOS/Linux:**
```bash
cd frontend
npm install
npm run dev
```

The frontend will run on `http://localhost:3000`

### 4. Load Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (top-right toggle)
3. Click **Load unpacked**
4. Select the `backend/extension/` folder from this project
5. Pin the ScamCap extension to your toolbar

## ⚙️ Configuration

### Environment Variables (Optional)

Create a `.env` file in the root directory:

```env
# Database
MONGODB_URL=mongodb://localhost:27017/scamcap

# Security
JWT_SECRET_KEY=your-secret-key-here

# MFA Providers (Optional)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-phone-number
```

If you don't provide these, the app will use default development settings.

## 📝 Usage

### Extension
1. Click the ScamCap icon in your browser toolbar
2. The extension automatically scans web pages for threats
3. View threat alerts and security status in the popup

### API Endpoints
- `GET /health` - Health check
- `POST /api/analyze/phishing` - Analyze URL for phishing
- `POST /api/analyze/deepfake` - Analyze image/video for deepfakes
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login

## 🔧 Development

### Training ML Models

**Phishing Model:**
```bash
python backend/ml-models/phishing/train_phishing_model.py
```

**Deepfake Model:**
```bash
python backend/ml-models/deepfake/train_deepfake_model.py
```

### Running Tests
```bash
# Backend tests
pytest

# Extension tests (requires Jest)
npm test
```

## 🐛 Troubleshooting

### Extension not loading
- Make sure all files are present in `backend/extension/` folder
- Check browser console (F12) for errors
- Try reloading the extension

### Backend connection failed
- Verify Python dependencies are installed
- Check if port 8000 is available
- Ensure `start_server.py` is running

### Database errors
- Install MongoDB or use MongoDB Atlas (cloud)
- Update `MONGODB_URL` in your `.env` file
- Check MongoDB is running: `mongod --version`

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/AmazingFeature`
3. Commit your changes: `git commit -m 'Add some AmazingFeature'`
4. Push to the branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔒 Security

- All analysis is performed securely
- No sensitive data is stored locally
- JWT-based authentication
- Encrypted data transmission

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section above
