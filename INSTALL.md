# Quick Installation Guide

## For Windows Users

1. **Install Python** (if not installed)
   - Download from: https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **Install Dependencies**
   ```powershell
   cd path\to\ScamCap-Web-Extension
   pip install -r backend\requirements.txt
   ```

3. **Start the Backend Server**
   ```powershell
   python start_server.py
   ```
   The server will run on http://localhost:8000

4. **Install Chrome Extension**
   - Open Chrome/Edge browser
   - Go to `chrome://extensions/` (or `edge://extensions/`)
   - Enable "Developer mode" (toggle in top-right)
   - Click "Load unpacked"
   - Select the `extension` folder
   - Done! The extension icon will appear in your browser toolbar

## For macOS/Linux Users

1. **Install Python 3** (if not installed)
   ```bash
   # macOS (using Homebrew)
   brew install python3
   
   # Ubuntu/Debian
   sudo apt-get install python3 python3-pip
   ```

2. **Install Dependencies**
   ```bash
   cd path/to/ScamCap-Web-Extension
   pip3 install -r backend/requirements.txt
   ```

3. **Start the Backend Server**
   ```bash
   python3 start_server.py
   ```
   The server will run on http://localhost:8000

4. **Install Chrome Extension**
   - Same steps as Windows (see above)

## Optional: Frontend Website

If you want to run the frontend website:

```bash
cd frontend
npm install
npm run dev
```

The website will run on http://localhost:3000

## Troubleshooting

**"pip: command not found"**
- Windows: Use `py -m pip` instead of `pip`
- macOS/Linux: Use `pip3` instead of `pip`

**"Port 8000 already in use"**
- Stop any other servers running on port 8000
- Or edit `start_server.py` to use a different port

**Extension not loading**
- Make sure all files in the `extension` folder are present
- Check browser console (F12) for errors
- Try disabling and re-enabling the extension

## Need Help?

Open an issue on GitHub with:
- Your operating system
- Python version (`python --version`)
- Error message (if any)
