# Troubleshooting Guide - FitFusion AI Assistant

Common issues and their solutions.

---

## 🔧 Installation Issues

### Issue: Docker not found

**Error:** `docker: command not found` or `docker-compose: command not found`

**Solution:**

1. Install Docker Desktop from: https://www.docker.com/products/docker-desktop
2. Start Docker Desktop
3. Verify installation:
   ```bash
   docker --version
   docker-compose --version
   ```

---

### Issue: Permission denied (Linux/Mac)

**Error:** `permission denied while trying to connect to the Docker daemon socket`

**Solution:**

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, then test
docker ps
```

---

### Issue: Port 8501 already in use

**Error:** `Bind for 0.0.0.0:8501 failed: port is already allocated`

**Solution Option 1 - Stop conflicting service:**

```bash
docker-compose down
```

**Solution Option 2 - Change port:**
Edit `docker-compose.yml`:

```yaml
ports:
  - "8502:8501" # Use port 8502 instead
```

Then access at: `http://localhost:8502`

---

## 🔑 API Key Issues

### Issue: API key not found

**Error:** `GOOGLE_API_KEY not found in environment variables`

**Solution:**

1. Create `.env` file in project root
2. Add your API key:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```
3. Restart Docker:
   ```bash
   docker-compose restart
   ```

---

### Issue: Invalid API key

**Error:** `API key not valid` or `403 Forbidden`

**Solution:**

1. Verify your API key at: https://makersuite.google.com/app/apikey
2. Generate a new key if needed
3. Update `.env` file
4. Restart application

---

### Issue: API quota exceeded

**Error:** `Resource exhausted` or `Quota exceeded`

**Solution:**

1. Wait for quota reset (usually daily)
2. Check quota at: https://console.cloud.google.com/
3. Consider upgrading to paid tier
4. Reduce temperature or max_tokens to save quota

---

## 🗄️ Database Issues

### Issue: Database locked

**Error:** `database is locked`

**Solution:**

```bash
# Stop all containers
docker-compose down

# Remove volumes
docker-compose down -v

# Restart
docker-compose up
```

---

### Issue: Database not persisting

**Problem:** Data disappears after restart

**Solution:**
Verify volume mounts in `docker-compose.yml`:

```yaml
volumes:
  - ./data:/app/data
  - ./logs:/app/logs
```

Ensure these directories exist:

```bash
mkdir -p data logs
```

---

### Issue: Corrupted database

**Error:** `database disk image is malformed`

**Solution:**

```bash
# Backup if possible
cp data/fitfusion.db data/fitfusion.db.backup

# Remove corrupted database
rm data/fitfusion.db

# Restart - will create new database
docker-compose restart
```

---

## 🤖 Agent Issues

### Issue: Agent not responding

**Symptoms:** Infinite loading, no response

**Solution:**

1. Check Docker logs:
   ```bash
   docker-compose logs -f
   ```
2. Verify API key is working
3. Check internet connection
4. Restart container:
   ```bash
   docker-compose restart
   ```

---

### Issue: Tool usage errors

**Error:** Agent calls wrong tool or wrong parameters

**Solution:**

1. Switch to **Few-Shot** prompt style (better accuracy)
2. Increase temperature slightly (try 0.7)
3. Use `gemini-1.5-pro` for complex queries
4. Check logs for error details:
   ```bash
   cat logs/experiment_logs.json
   ```

---

### Issue: Persona not consistent

**Problem:** Agent breaks character

**Solution:**

1. Restart conversation (clear chat history)
2. Use **Few-Shot** prompt style
3. Try different persona
4. Check system prompts in `prompts/system_prompts.py`

---

### Issue: Agent runs out of iterations

**Error:** "I'm having trouble processing this request"

**Solution:**

1. Simplify your query
2. Break into multiple questions
3. This is max_iterations limit (5) - by design to prevent loops

---

## 🌐 Web Interface Issues

### Issue: Page won't load

**Error:** `This site can't be reached` or `ERR_CONNECTION_REFUSED`

**Solution:**

1. Verify Docker is running:
   ```bash
   docker ps
   ```
2. Check if container is healthy:
   ```bash
   docker-compose ps
   ```
3. View logs for errors:
   ```bash
   docker-compose logs
   ```
4. Restart:
   ```bash
   docker-compose restart
   ```

---

### Issue: Streamlit connection error

**Error:** Red error banner in UI

**Solution:**

1. Refresh the page (Ctrl+F5)
2. Clear browser cache
3. Try incognito/private window
4. Restart application

---

### Issue: Chat history not showing

**Problem:** Messages disappear

**Solution:**

- This is expected on page refresh
- Click "Clear Chat History" to reset properly
- Or continue new conversation

---

### Issue: Settings not applying

**Problem:** Changes to temperature/model don't work

**Solution:**

1. Wait 1-2 seconds after changing settings
2. Start new conversation for settings to take effect
3. Check Docker logs for errors

---

## 📦 Docker Issues

### Issue: Build fails

**Error:** `failed to build` or dependency errors

**Solution:**

```bash
# Clean rebuild
docker-compose build --no-cache

# If still fails, check requirements.txt
# Ensure all packages are available
```

---

### Issue: Container exits immediately

**Error:** Container starts then stops

**Solution:**

```bash
# View exit logs
docker-compose logs

# Common causes:
# - Missing .env file
# - Invalid API key
# - Port conflict
```

---

### Issue: Out of disk space

**Error:** `no space left on device`

**Solution:**

```bash
# Clean up Docker
docker system prune -a

# Remove unused volumes
docker volume prune
```

---

## 🔍 Debugging Tips

### Enable verbose logging

Edit `utils/helpers.py`:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    ...
)
```

---

### View real-time logs

```bash
# All logs
docker-compose logs -f

# Just fitfusion-app
docker-compose logs -f fitfusion-app
```

---

### Access container shell

```bash
# Get shell access
docker-compose exec fitfusion-app /bin/bash

# Check files
ls -la /app

# Check environment
env | grep GOOGLE
```

---

### Test API directly

```python
# Inside container or local environment
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content("Hello")
print(response.text)
```

---

## 🐛 Common Error Messages

### `ModuleNotFoundError: No module named 'streamlit'`

**Solution:** Dependencies not installed

```bash
docker-compose build --no-cache
```

---

### `sqlite3.OperationalError: no such table: users`

**Solution:** Database not initialized

```bash
# Remove and restart
rm data/fitfusion.db
docker-compose restart
```

---

### `TypeError: run() missing 1 required positional argument`

**Solution:** Check function calls in code, likely bug

- Review recent changes
- Check tool implementations

---

### `KeyError: 'GOOGLE_API_KEY'`

**Solution:** Environment variable not set

- Create `.env` file
- Add API key
- Restart Docker

---

## 🔄 Reset Everything

If all else fails, complete reset:

```bash
# Stop containers
docker-compose down

# Remove volumes and data
docker-compose down -v
rm -rf data/ logs/

# Clean Docker
docker system prune -a

# Rebuild
docker-compose build --no-cache

# Start fresh
docker-compose up
```

---

## 📊 Performance Issues

### Issue: Slow responses (>10 seconds)

**Possible causes:**

1. Using `gemini-1.5-pro` (slower model)
2. High max_tokens setting
3. Network latency
4. API rate limiting

**Solutions:**

- Switch to `gemini-1.5-flash`
- Reduce max_tokens to 2048
- Check internet connection
- Monitor API quotas

---

### Issue: High CPU/Memory usage

**Solution:**

```bash
# Check resource usage
docker stats

# Limit resources in docker-compose.yml
services:
  fitfusion-app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

---

## 🆘 Still Having Issues?

### Check these resources:

1. **README.md** - Full documentation
2. **REFLECTION.md** - Implementation details
3. **Logs** - `logs/experiment_logs.json`
4. **Docker logs** - `docker-compose logs`

### Gather information:

```bash
# System info
docker --version
python --version
cat .env | grep -v "API_KEY"

# Container status
docker-compose ps

# Recent logs
docker-compose logs --tail=50
```

### Report issues with:

- Error message (full text)
- Steps to reproduce
- Configuration used (persona, model, etc.)
- Docker logs
- System info

---

## ✅ Prevention Checklist

Before starting:

- [ ] Docker Desktop is running
- [ ] `.env` file exists with valid API key
- [ ] No other service using port 8501
- [ ] Internet connection is stable
- [ ] Sufficient disk space (>2GB free)

Regular maintenance:

- [ ] Clear old logs periodically
- [ ] Monitor API usage
- [ ] Update dependencies occasionally
- [ ] Backup database before major changes

---

**Most issues can be solved with a restart! 🔄**

```bash
docker-compose restart
```

---

_Last updated: October 26, 2025_
