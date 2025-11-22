# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Or use the setup script:

```bash
python setup.py
```

### Step 2: Configure OpenAI API Key

Create a `.env` file in the project root:

```bash
# Standard OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview

# OR for custom OpenAI endpoints (proxy/alternative providers):
OPENAI_API_KEY=028fa2e1-fb69-4cca-89aa-1e11ffc4dcc1
OPENAI_BASE_URL=https://openai.dplit.com/v1
OPENAI_MODEL=gpt-4-turbo-preview

# Application Settings
DEBUG=False
HOST=0.0.0.0
PORT=8000
```

💡 **For standard OpenAI**: Get your API key from https://platform.openai.com/api-keys  
💡 **For custom endpoints**: Use your provider's API key and base URL

### Step 3: Start the Server

```bash
# Option 1: Direct Python
python main.py

# Option 2: Uvicorn with auto-reload
uvicorn main:app --reload

# Option 3: Use convenience scripts
# Windows:
run.bat

# macOS/Linux:
chmod +x run.sh
./run.sh
```

Server will start at: **http://localhost:8000**

### Step 4: Test the API

Open your browser and go to:
- **API Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc

Or run the example client:

```bash
python example_client.py
```

## 📋 Basic Usage Flow

### 1. Start a Session

```bash
curl -X POST "http://localhost:8000/api/session/start" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Your Name",
    "current_level": "Junior",
    "target_level": "Senior",
    "years_of_experience": 2,
    "primary_technologies": ["React", "JavaScript"]
  }'
```

Response includes `session_id` - save this!

### 2. Have Conversation

```bash
curl -X POST "http://localhost:8000/api/conversation/{session_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I worked on a React e-commerce project..."
  }'
```

Continue until AI says conversation is complete.

### 3. Get Self-Assessment Test

```bash
curl -X GET "http://localhost:8000/api/assessment/test/{session_id}"
```

### 4. Submit Assessment

```bash
curl -X POST "http://localhost:8000/api/assessment/submit/{session_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "answers": [
      {
        "question_id": "...",
        "skill": "React",
        "answer": "Intermediate",
        "confidence_level": 4
      }
    ]
  }'
```

### 5. Generate Gap Analysis

```bash
curl -X POST "http://localhost:8000/api/gap-analysis/{session_id}"
```

Get your complete assessment report!

## 🎯 Testing with Swagger UI

1. Go to http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in the parameters
5. Click "Execute"
6. See the response below

## 📝 Example with Real Data

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Start session
response = requests.post(f"{BASE_URL}/api/session/start", json={
    "name": "John Doe",
    "target_level": "Senior",
    "current_level": "Junior",
    "years_of_experience": 2.5
})
session_id = response.json()["session_id"]

# 2. Conversation
requests.post(f"{BASE_URL}/api/conversation/{session_id}", json={
    "message": "I built a React dashboard with Redux..."
})

# 3. Get test
test = requests.get(f"{BASE_URL}/api/assessment/test/{session_id}").json()

# 4. Submit answers (simplified)
answers = [
    {"question_id": q["id"], "skill": q["skill"], "answer": "Intermediate"}
    for q in test["test"]["questions"]
]
requests.post(f"{BASE_URL}/api/assessment/submit/{session_id}", json={"answers": answers})

# 5. Get report
report = requests.post(f"{BASE_URL}/api/gap-analysis/{session_id}").json()
print(f"Readiness: {report['overall_readiness']}%")
```

## ⚠️ Troubleshooting

### Port Already in Use

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

### OpenAI API Errors

- Check your API key is correct in `.env`
- Ensure you have API credits: https://platform.openai.com/usage
- Check OpenAI API status: https://status.openai.com

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Module Not Found

Make sure you're in the project directory and virtual environment is activated:

```bash
# Check current directory
pwd  # Should show your project directory

# Activate venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Try the example client: `python example_client.py`
- Use the `.http` file with REST Client extension in VS Code

## 🆘 Need Help?

1. Check the API docs at `/docs`
2. Review the error messages - they're descriptive
3. Check your `.env` file configuration
4. Ensure OpenAI API key is valid and has credits
5. Look at the console output for detailed logs

## 🎉 Success Checklist

- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] .env file created with OpenAI API key
- [ ] Server starts without errors
- [ ] Can access http://localhost:8000/docs
- [ ] Can create a session via API
- [ ] Example client runs successfully

Happy assessing! 🚀

