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

## 🚀 Complete Installation Guide (All Operating Systems)

### Prerequisites

#### Required Software
- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
  - ✅ Verify installation: `python --version` or `python3 --version`
- **Git** - [Download Git](https://git-scm.com/downloads)
  - ✅ Verify installation: `git --version`
- **Chrome or Edge Browser** - For running the extension

#### Optional (for full development)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/) (only needed for frontend website)
  - ✅ Verify installation: `node --version`
- **MongoDB** - [Download MongoDB](https://www.mongodb.com/try/download/community) or use [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) (cloud - recommended for beginners)

---

## 📦 Step-by-Step Installation

### Step 1: Clone the Repository

Open your terminal/command prompt and run:

```bash
git clone https://github.com/YOUR_USERNAME/ScamCap-Web-Extension.git
cd ScamCap-Web-Extension
```

Or download as ZIP and extract to your desired location.

---

### Step 2: Setup Python Environment

#### Windows (PowerShell/Command Prompt)

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

#### macOS/Linux (Terminal)

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
python3 -m pip install --upgrade pip

# Install dependencies
pip3 install -r requirements.txt
```

**✅ Verification**: You should see `(.venv)` prefix in your terminal prompt

---

### Step 3: Configure Environment Variables (Optional)

Create a `.env` file in the project root directory:

**Windows:**
```powershell
# Create .env file
New-Item -Path .env -ItemType File

# Edit with notepad
notepad .env
```

**macOS/Linux:**
```bash
# Create and edit .env file
nano .env
# or
touch .env && code .env
```

Add the following content (modify as needed):

```env
# Database Configuration
MONGODB_URL=mongodb://localhost:27017/scamcap
# Or use MongoDB Atlas cloud:
# MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/scamcap

# Security
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production

# Server Configuration
PORT=8000
HOST=0.0.0.0

# MFA Providers (Optional - for SMS authentication)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**Note**: If you skip this step, the app will use default development settings.

---

### Step 4: Start the Backend Server

Make sure your virtual environment is activated (you should see `(.venv)` in your prompt).

#### Windows:
```powershell
python start_server.py
```

#### macOS/Linux:
```bash
python3 start_server.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ Backend is now running at `http://localhost:8000`

Test it by opening your browser and visiting: `http://localhost:8000/health`

You should see: `{"status": "healthy"}`

**Keep this terminal window open!** Open a new terminal for the next steps.

---

### Step 5: Install the Browser Extension

1. **Open Chrome/Edge** and navigate to:
   - Chrome: `chrome://extensions/`
   - Edge: `edge://extensions/`

2. **Enable Developer Mode**
   - Toggle the switch in the top-right corner

3. **Load the Extension**
   - Click **"Load unpacked"** button
   - Navigate to your project folder
   - Select the `backend/extension/` folder
   - Click **"Select Folder"**

4. **Pin the Extension**
   - Click the puzzle icon 🧩 in the browser toolbar
   - Find **ScamCap** in the list
   - Click the pin icon 📌

✅ You should now see the ScamCap icon in your browser toolbar!

---

### Step 6: Frontend Website Setup (Optional)

The frontend is a Next.js website for documentation and quick scans. **This is optional** - the extension works without it.

#### Windows:
```powershell
# Open new terminal/PowerShell
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### macOS/Linux:
```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

✅ Frontend is now running at `http://localhost:3000`

---

## 🧪 Testing Your Installation

### 1. Test Backend API
Open your browser and test these endpoints:

- Health Check: http://localhost:8000/health
- API Docs: http://localhost:8000/docs (Interactive Swagger UI)
- Test Endpoint: http://localhost:8000/api/test/quick-scan

### 2. Test Browser Extension

1. Click the ScamCap icon in your browser toolbar
2. You should see the extension popup
3. Try entering a URL to scan for phishing
4. Check the console (F12) for any errors

### 3. Test Frontend (if installed)
Visit http://localhost:3000 and try the quick scan feature

---

## 🔄 Running the Project After Installation

Every time you want to use ScamCap:

### Windows:
```powershell
# 1. Activate virtual environment
.venv\Scripts\activate

# 2. Start backend server
python start_server.py

# 3. (Optional) Start frontend in new terminal
cd frontend
npm run dev
```

### macOS/Linux:
```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Start backend server
python3 start_server.py

# 3. (Optional) Start frontend in new terminal
cd frontend
npm run dev
```

The browser extension will automatically connect to the backend.

## 🔧 Advanced Configuration

### Database Setup

#### Option 1: MongoDB Atlas (Cloud - Recommended for Beginners)

1. Create free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster (free tier available)
3. Get your connection string
4. Add it to your `.env` file:
   ```env
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/scamcap
   ```

#### Option 2: Local MongoDB Installation

**Windows:**
1. Download [MongoDB Community Server](https://www.mongodb.com/try/download/community)
2. Install with default settings
3. MongoDB will run automatically on `mongodb://localhost:27017`

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### Environment Variables Reference

All available configuration options:

```env
# === Database Configuration ===
MONGODB_URL=mongodb://localhost:27017/scamcap

# === Security Settings ===
JWT_SECRET_KEY=change-this-to-a-random-secure-string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# === Server Configuration ===
PORT=8000
HOST=0.0.0.0
CORS_ORIGINS=["http://localhost:3000", "chrome-extension://*"]

# === MFA/SMS (Optional) ===
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number

# === Email Notifications (Optional) ===
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@scamcap.com

# === ML Models Configuration ===
PHISHING_MODEL_PATH=backend/ml-models/phishing/phishing_model.pth
DEEPFAKE_MODEL_PATH=backend/ml-models/deepfake/deepfake_model.pth

# === Logging ===
LOG_LEVEL=INFO
```

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

## 🐛 Troubleshooting Common Issues

### Python/Installation Issues

#### ❌ "Python is not recognized as a command"
**Solution:**
- Windows: Reinstall Python and check "Add Python to PATH" during installation
- Verify by running: `python --version` or `py --version`

#### ❌ "pip is not recognized as a command"
**Solution:**
```bash
# Windows
python -m pip --version

# macOS/Linux
python3 -m pip --version
```

#### ❌ "Permission denied" when installing packages
**Solution:**
- **Do NOT use sudo!** Make sure you're in a virtual environment
- Activate virtual environment first: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (macOS/Linux)

#### ❌ Package installation fails
**Solution:**
```bash
# Update pip first
python -m pip install --upgrade pip

# Install with verbose output to see the error
pip install -r requirements.txt -v

# Or install packages one by one
pip install fastapi uvicorn python-multipart
```

### Backend Server Issues

#### ❌ "Port 8000 is already in use"
**Solution:**

**Windows:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or use different port
$env:PORT=8001; python start_server.py
```

**macOS/Linux:**
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
PORT=8001 python3 start_server.py
```

#### ❌ "Module not found" errors
**Solution:**
```bash
# Make sure virtual environment is activated
# Then reinstall dependencies
pip install -r requirements.txt

# If specific module is missing
pip install <module-name>
```

#### ❌ Backend crashes on startup
**Solution:**
1. Check Python version: `python --version` (must be 3.8+)
2. Review error message in terminal
3. Ensure all dependencies are installed
4. Check `.env` file syntax (no spaces around `=`)

### Extension Issues

#### ❌ Extension doesn't appear in browser
**Solution:**
1. Make sure you selected the correct folder: `backend/extension/`
2. Check that `manifest.json` exists in that folder
3. Try reloading the extension (refresh icon in `chrome://extensions/`)
4. Check browser console (F12) for errors

#### ❌ "Failed to load extension" error
**Solution:**
- Check `manifest.json` for syntax errors
- Ensure all referenced files exist (`popup.html`, `service-worker.js`, etc.)
- Try Chrome Canary or Edge if Chrome doesn't work

#### ❌ Extension can't connect to backend
**Solution:**
1. Verify backend is running: Visit `http://localhost:8000/health`
2. Check extension's console for errors:
   - Right-click extension icon → "Inspect popup"
   - Check Console tab
3. Verify CORS settings in backend
4. Check if firewall is blocking connections

### Database Issues

#### ❌ MongoDB connection failed
**Solution:**
- **Using local MongoDB**: Check if MongoDB is running
  ```bash
  # Windows
  net start MongoDB
  
  # macOS
  brew services start mongodb-community
  
  # Linux
  sudo systemctl start mongodb
  ```
- **Using MongoDB Atlas**: 
  - Check connection string in `.env`
  - Verify IP whitelist in Atlas dashboard (add 0.0.0.0/0 for testing)
  - Check username/password

#### ❌ "Authentication failed" for MongoDB
**Solution:**
- Verify credentials in `.env` file
- For Atlas: regenerate password and update `.env`
- For local: Remove authentication for development

### Frontend Issues

#### ❌ "npm: command not found"
**Solution:**
- Install Node.js from [nodejs.org](https://nodejs.org/)
- Restart terminal after installation
- Verify: `node --version` and `npm --version`

#### ❌ Frontend build/start fails
**Solution:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json  # macOS/Linux
# or
rmdir /s node_modules & del package-lock.json  # Windows

npm install
npm run dev
```

#### ❌ "Port 3000 already in use"
**Solution:**
```bash
# Kill process on port 3000
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:3000 | xargs kill -9

# Or use different port
PORT=3001 npm run dev
```

### Virtual Environment Issues

#### ❌ Virtual environment won't activate
**Windows PowerShell:**
```powershell
# Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
.venv\Scripts\activate
```

**Windows Command Prompt:**
```cmd
.venv\Scripts\activate.bat
```

**Git Bash (Windows):**
```bash
source .venv/Scripts/activate
```

#### ❌ "Cannot find .venv folder"
**Solution:**
- Make sure you're in the project root directory
- Create virtual environment: `python -m venv .venv`

### Still Having Issues?

1. **Check the logs**: Look at terminal output for specific error messages
2. **Test each component**: Backend → Extension → Frontend
3. **Verify versions**: Ensure Python 3.8+, Node 16+ are installed
4. **Clean install**: Delete `.venv` and `node_modules`, reinstall everything
5. **Open an issue**: Include error messages and your OS/Python/Node versions

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
