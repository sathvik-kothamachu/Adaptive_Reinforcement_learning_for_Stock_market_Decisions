# Troubleshooting Guide - Model + Frontend Integration

## 🔴 Common Issues and Solutions

### 1. Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'api_server'`

**Solution**:
```powershell
# Make sure you're in the correct directory
cd C:\Users\manis\Downloads\nif50

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Try again
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000
```

**Error**: `Address already in use (':8000')`

**Solution**:
```powershell
# Find and kill process on port 8000
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force

# Or find the PID and kill it
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or change the port
python -m uvicorn api_server:app --port 8001
```

**Error**: `ImportError: No module named 'fastapi'`

**Solution**:
```powershell
# Install required packages
pip install -r requirements-backend.txt

# Or individual packages
pip install fastapi uvicorn python-multipart
```

---

### 2. Frontend Won't Connect to Backend

**Error**: Dashboard loads but data doesn't appear, or errors in browser console

**Solution**:

1. **Check backend is running**:
   ```powershell
   # In PowerShell
   curl http://localhost:8000/health
   # Should return: {"status":"healthy",...}
   ```

2. **Check frontend config**:
   ```powershell
   type trade-signal-dashboard-main\.env.local
   # Should show: VITE_API_BASE_URL=http://localhost:8000
   ```

3. **Check browser console** (F12):
   - Look for CORS errors
   - Look for network errors
   - Should see requests to `http://localhost:8000/api/analyze`

4. **Verify both servers are running**:
   - Backend: `http://localhost:8000/docs` should load
   - Frontend: `http://localhost:5173` should load

---

### 3. CORS Errors

**Error**: `Access to XMLHttpRequest blocked by CORS policy`

**Solution**:

The API server has CORS enabled, but check:

1. **Check backend is accessible**:
   ```powershell
   # From another terminal
   curl -H "Accept: application/json" http://localhost:8000/health
   ```

2. **Check frontend is calling correct URL**:
   ```javascript
   // Check in browser console
   console.log(import.meta.env.VITE_API_BASE_URL)
   // Should show: http://localhost:8000
   ```

3. **Rebuild frontend if .env changed**:
   ```powershell
   cd trade-signal-dashboard-main
   npm run build
   npm run dev
   ```

---

### 4. API Returns 400 Error

**Error**: `Analysis API returned 400`

**Solution**:

Check ticker format. Use the correct NSE format:

```
Valid tickers:
- RELIANCE.NS
- INFY.NS
- HDFCBANK.NS
- TCS.NS
- ICICIBANK.NS
- HINDUNILVR.NS
- ITC.NS
- SBIN.NS
- BHARTIARTL.NS
- KOTAKBANK.NS
```

Test directly:
```powershell
curl "http://localhost:8000/api/analyze?ticker=RELIANCE.NS"
```

---

### 5. First Request Takes Too Long

**Issue**: First analysis request takes 5-10 seconds

**This is normal** - the model is loading:
1. PPO model loaded from disk
2. Technical indicators computed
3. Sentiment analysis run
4. Backtest performed
5. Results formatted

Subsequent requests will be faster (2-3s) due to caching.

**To speed up**:
- Use SSD (faster I/O)
- Keep backend running (no reload time)
- Check system resources (RAM, CPU)

---

### 6. Model Accuracy Concerns

**Issue**: Results don't match original model

**Verification**:

1. **Check nothing was modified**:
   ```powershell
   # Look at git diff (if using git)
   git diff Nifty50_RL_Trading_MultiStock.py
   # Should only show compute_regime() function added
   ```

2. **Compare direct vs API**:
   ```python
   # Direct - Run original script
   python Nifty50_RL_Trading_MultiStock.py
   
   # Via API
   curl http://localhost:8000/api/all-stocks
   
   # Compare FINAL SIGNAL values
   ```

3. **Check metrics**:
   - Sharpe Ratio should match
   - Win Rate should match
   - Buy/Sell Precision should match
   - Signals (BUY/SELL/HOLD) should match

---

### 7. NPM Dependencies Issue

**Error**: `npm: command not found` or `npm install fails`

**Solution**:

1. **Install Node.js** if not present:
   - Download from https://nodejs.org/
   - Install LTS version
   - Restart terminal

2. **Clear cache and reinstall**:
   ```powershell
   cd trade-signal-dashboard-main
   rm -r node_modules package-lock.json
   npm install
   ```

3. **Check permissions**:
   ```powershell
   # Run PowerShell as Administrator
   npm install --legacy-peer-deps
   ```

---

### 8. Port Already Used

**Error**: `Address already in use (':5173')` or `(':8000')`

**Solution**:

```powershell
# List processes using ports
netstat -ano | findstr ":8000"
netstat -ano | findstr ":5173"

# Kill process by PID
taskkill /PID 12345 /F

# Or use lsof on Unix/Mac
lsof -i :8000
kill -9 <PID>

# Or change ports in .env files
```

---

### 9. Model Files Missing

**Error**: `FileNotFoundError: trained_models/PPO_RELIANCE.NS not found`

**Solution**:

The models should be in `trained_models/` folder. If missing:

1. **Run original model to train**:
   ```powershell
   python Nifty50_RL_Trading_MultiStock.py
   # This will train and save models
   ```

2. **Or download pre-trained models** if available

3. **Check disk space** - Large models need space

---

### 10. Memory Issues

**Error**: `MemoryError` or system hangs

**Solution**:

1. **Reduce concurrency**:
   ```env
   # .env.backend
   CONCURRENCY=1  # Was 2
   ```

2. **Run one analysis at a time** instead of all stocks

3. **Check system resources**:
   ```powershell
   # View available RAM
   Get-ComputerInfo | Select-Object CsPhysicallyInstalledMemorySize
   ```

4. **Close other applications** to free memory

---

### 11. GPU/CUDA Issues

**Error**: `AssertionError` related to CUDA or device

**Solution**:

The code uses `device='cuda'` for GPU. If no GPU:

Edit `api_server.py` line where PPO loads:
```python
# Change from:
ppo = PPO.load(load_path, env=env, device='cuda')

# To:
ppo = PPO.load(load_path, env=env, device='cpu')
```

Or in `Nifty50_RL_Trading_MultiStock.py`:
```python
# Find and change device='cuda' to device='cpu'
```

---

### 12. Dashboard Shows No Data

**Issue**: Dashboard loads but shows empty charts/tables

**Checklist**:

1. ✓ Backend running? `curl http://localhost:8000/health`
2. ✓ Frontend config correct? Check `.env.local`
3. ✓ Stock selected? Dropdown should show 10 stocks
4. ✓ Click Refresh button? May need to manually refresh
5. ✓ Check browser console (F12) for errors
6. ✓ Backend logs for error messages
7. ✓ Try accessing `/api/stocks` to see available stocks

---

### 13. Sentiment Data Missing

**Issue**: Headlines showing but empty or sentiment scores 0

**Solution**:

This is expected - API keys for news:
- `FINNHUB_API_KEY` - Limited free tier
- `NEWSAPI_KEY` - Limited free tier

To get full sentiment:

```python
# Update API keys in api_server.py
FINNHUB_API_KEY  = "your_key_here"
NEWSAPI_KEY      = "your_key_here"
```

Or purchase premium API access.

---

### 14. Slow Network Requests

**Issue**: Requests take >10 seconds

**Solutions**:

1. **Check internet connection**
2. **Verify data isn't being re-fetched**:
   ```env
   # .env.backend
   FORCE_REFETCH=False  # Don't re-download
   ```
3. **Check cache folder** has data files
4. **Verify file I/O** isn't bottleneck
5. **Use SSD** instead of HDD if possible

---

### 15. Integration Not Working After Update

**Issue**: Changed something, now it doesn't work

**Solution** - Start fresh:

```powershell
# Stop both servers
# Close all terminals

# Verify files are correct
type api_server.py | head -20
type trade-signal-dashboard-main\.env.local

# Clear caches
rm -r trade-signal-dashboard-main\node_modules
npm install

# Reinstall Python deps
pip install -r requirements-backend.txt --force-reinstall

# Start fresh
.\start_backend.bat
.\start_frontend.bat
```

---

## 🔧 Debug Mode

Enable debug logging:

```python
# In api_server.py, change log level
logging.basicConfig(level=logging.DEBUG)

# Or set env variable
set LOG_LEVEL=debug
```

```powershell
# Run with verbose output
python -m uvicorn api_server:app --log-level debug --reload
```

---

## 📊 Testing Endpoints

### Test Backend Directly

```powershell
# Health check
curl http://localhost:8000/health

# Single stock analysis
curl "http://localhost:8000/api/analyze?ticker=RELIANCE.NS"

# All stocks
curl http://localhost:8000/api/all-stocks

# Market regime
curl http://localhost:8000/api/market-regime

# Available stocks
curl http://localhost:8000/api/stocks
```

### Test Frontend Network

Open browser DevTools (F12):
```javascript
// Test API connection
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(d => console.log('Backend OK', d))
  .catch(e => console.error('Backend error', e))

// Test single stock
fetch('http://localhost:8000/api/analyze?ticker=RELIANCE.NS')
  .then(r => r.json())
  .then(d => console.log('Analysis:', d))
```

---

## 📝 Useful Commands

```powershell
# View backend logs in real-time
Get-Content -Path "backend.log" -Wait

# Test if port is open
Test-NetConnection -ComputerName localhost -Port 8000

# View environment variables
$env:VITE_API_BASE_URL

# Kill all Python processes
Get-Process python | Stop-Process -Force

# Check disk space
Get-Volume

# Monitor system resources
Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*node*"} | Format-Table Name, CPU, Memory
```

---

## 🆘 When Nothing Works

1. **Restart everything**:
   ```powershell
   # Close all terminals
   # Close browser
   # Wait 10 seconds
   # Start fresh
   ```

2. **Check system**:
   ```powershell
   # Verify Python
   python --version
   
   # Verify Node
   node --version
   
   # Check connections
   netstat -an | findstr LISTEN
   ```

3. **Clean install**:
   ```powershell
   # Remove and reinstall everything
   rm -r .venv node_modules
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements-backend.txt
   ```

4. **Read logs carefully** - They usually tell you what's wrong

5. **Check INTEGRATION_GUIDE.md** again - Answer might be there

---

## 📞 Getting Help

1. Check this file first
2. Read INTEGRATION_GUIDE.md
3. Check SETUP_CHECKLIST.md
4. Review error messages in:
   - Browser console (F12)
   - PowerShell/terminal
   - Backend logs
5. Try isolation testing - test each component separately

---

**Last Updated**: April 28, 2026
**Status**: Complete troubleshooting guide
