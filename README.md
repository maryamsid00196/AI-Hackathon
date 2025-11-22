# Skill Assessment API

A comprehensive FastAPI-based REST API for conducting AI-powered skill assessments and gap analysis for frontend developers.

## Features

- 🤖 **AI-Powered Conversations**: Interactive discussions with OpenAI to understand candidate experience
- 📊 **Self-Assessment Tests**: Structured questionnaires for skill evaluation
- 🔍 **Gap Analysis**: Detailed comparison against industry standards (Junior/Senior/Team Lead)
- 📈 **Comprehensive Reports**: Combined AI and self-assessment insights
- 🎯 **Personalized Learning Paths**: Tailored recommendations based on gaps

## Skill Coverage

The API assesses proficiency in:
- HTML & Semantic Markup
- CSS (including Flexbox, Grid, Animations)
- JavaScript (ES6+, Async/Await)
- React (Hooks, Context, Performance)
- Next.js (SSR, SSG, Routing)
- Git & Version Control
- Debugging Skills
- API Integration
- State Management (Redux/Zustand)
- Performance Optimization

## Installation

### Prerequisites
- Python 3.8+
- OpenAI API Key

### Setup

1. **Clone the repository** (or navigate to the project directory)

```bash
cd "Hackathon Project"
```

2. **Create a virtual environment**

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the project root:

```bash
# Standard OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview

# For custom OpenAI endpoints (e.g., proxy or alternative providers):
# OPENAI_API_KEY=028fa2e1-fb69-4cca-89aa-1e11ffc4dcc1
# OPENAI_BASE_URL=https://openai.dplit.com/v1

# Application Configuration
DEBUG=False
HOST=0.0.0.0
PORT=8000
```

5. **Run the application**

```bash
python main.py
```

Or use uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Session Management

#### Start New Session
```http
POST /api/session/start
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "current_level": "Junior",
  "target_level": "Senior",
  "years_of_experience": 2.5,
  "primary_technologies": ["React", "JavaScript", "CSS"],
  "additional_info": "Worked on e-commerce projects"
}
```

**Response:**
```json
{
  "session_id": "uuid-here",
  "message": "Initial AI greeting and first question",
  "status": "conversation_started"
}
```

### Conversation

#### Continue Conversation
```http
POST /api/conversation/{session_id}
Content-Type: application/json

{
  "message": "I recently worked on a React e-commerce app..."
}
```

**Response:**
```json
{
  "message": "AI's follow-up question",
  "conversation_complete": false,
  "next_step": "continue_conversation"
}
```

#### Get Conversation History
```http
GET /api/conversation/{session_id}/history
```

### Assessment

#### Get Self-Assessment Test
```http
GET /api/assessment/test/{session_id}
```

**Response:**
```json
{
  "session_id": "uuid",
  "test": {
    "total_questions": 20,
    "skills_covered": ["HTML", "CSS", "JavaScript", ...],
    "questions": [...]
  },
  "instructions": "Please answer all questions honestly..."
}
```

#### Submit Assessment
```http
POST /api/assessment/submit/{session_id}
Content-Type: application/json

{
  "answers": [
    {
      "question_id": "uuid",
      "skill": "React",
      "answer": "Expert",
      "confidence_level": 4
    },
    ...
  ]
}
```

### Gap Analysis

#### Generate Gap Analysis Report
```http
POST /api/gap-analysis/{session_id}
```

**Response:**
```json
{
  "session_id": "uuid",
  "user_name": "John Doe",
  "current_level": "Junior",
  "target_level": "Senior",
  "overall_readiness": 72.5,
  "readiness_status": "Almost Ready",
  "skill_gaps": [...],
  "skills_on_track": ["HTML", "CSS"],
  "skills_need_improvement": ["React", "Next.js"],
  "critical_gaps": ["State Management"],
  "learning_path": [...],
  "estimated_time_to_target": "6-12 months with dedicated learning",
  "priority_areas": ["State Management", "Performance Optimization"]
}
```

## Workflow

1. **Start Session**: User provides initial data and target level
2. **AI Conversation**: 5-8 exchanges to understand experience and skills
3. **Self-Assessment**: User completes structured questionnaire
4. **Gap Analysis**: System generates comprehensive report comparing:
   - AI assessment from conversation
   - Self-assessment results
   - Industry standards for target level
5. **Learning Path**: Receive personalized recommendations and timeline

## Skill Level Standards

| Skill | Junior | Senior | Team Lead |
|-------|--------|--------|-----------|
| HTML | Basic | Intermediate | Expert |
| CSS | Basic | Expert | Expert |
| JavaScript | Basic | Expert | Expert |
| React | Basic | Expert | Expert |
| Next.js | Basic | Expert | Expert |
| Git Basics | Basic | Advanced | Expert |
| Debugging Skills | Basic | Expert | Expert |
| API Integration | Basic | Intermediate | Expert |
| State Management | Basic | Intermediate | Expert |
| Performance Optimization | Basic | Intermediate | Expert |

## Architecture

```
.
├── main.py                          # FastAPI application and endpoints
├── models.py                        # Pydantic data models
├── config.py                        # Configuration and skill standards
├── services/
│   ├── __init__.py
│   ├── openai_service.py           # OpenAI integration
│   ├── assessment_service.py       # Assessment logic
│   └── gap_analysis_service.py     # Gap analysis engine
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
└── README.md                        # This file
```

## Development

### Running in Development Mode

```bash
uvicorn main:app --reload
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (when test suite is added)
pytest
```

## Configuration

Edit `config.py` to customize:
- Skill standards matrix
- Proficiency level definitions
- Conversation parameters
- Assessment settings

## Security Considerations

⚠️ **Important for Production**:
- Replace in-memory storage with a proper database (PostgreSQL, MongoDB)
- Add authentication and authorization
- Implement rate limiting
- Secure API keys using secret management
- Add HTTPS/TLS
- Implement proper session expiration
- Add input validation and sanitization
- Set up logging and monitoring

## Future Enhancements

- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] User authentication (JWT)
- [ ] Email notifications for reports
- [ ] PDF report generation
- [ ] Admin dashboard
- [ ] Multiple assessment templates
- [ ] Team/organization management
- [ ] Historical progress tracking
- [ ] Integration with learning platforms

## License

MIT License

## Support

For issues or questions, please create an issue in the repository.

---

**Built with FastAPI, OpenAI, and ❤️**

