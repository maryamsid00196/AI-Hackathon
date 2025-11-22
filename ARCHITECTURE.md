# Architecture Documentation

## System Overview

The Skill Assessment API is a REST-based system built with FastAPI that combines AI-powered conversational assessment with structured self-assessment to provide comprehensive skill gap analysis for frontend developers.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│  (Web App, Mobile App, CLI, or any HTTP client)             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Layer                           │
│                        (main.py)                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Endpoints                                        │  │
│  │  - Session Management                                 │  │
│  │  - Conversation Handler                               │  │
│  │  - Assessment Handler                                 │  │
│  │  - Gap Analysis Generator                             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     Business Logic Layer                     │
│                      (services/)                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   OpenAI     │  │  Assessment  │  │ Gap Analysis │    │
│  │   Service    │  │   Service    │  │   Service    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  In-Memory Storage (Development)                      │  │
│  │  - Sessions Dictionary                                │  │
│  │  - Conversations History                              │  │
│  │  - Assessment Results                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Note: Replace with Database for Production                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            OpenAI API (gpt-4-turbo)                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. API Layer (`main.py`)

**Purpose**: HTTP request handling and routing

**Key Responsibilities**:
- Endpoint definitions and request validation
- Session lifecycle management
- Response formatting
- CORS handling
- Error handling

**Main Endpoints**:
```
POST   /api/session/start          - Initiate new assessment
POST   /api/conversation/{id}      - Continue AI conversation
GET    /api/conversation/{id}/history - Get conversation log
GET    /api/assessment/test/{id}   - Retrieve assessment questions
POST   /api/assessment/submit/{id} - Submit assessment answers
POST   /api/gap-analysis/{id}      - Generate gap analysis report
GET    /api/session/{id}           - Get session details
GET    /api/sessions               - List all sessions (admin)
DELETE /api/session/{id}           - Delete session
```

### 2. Data Models (`models.py`)

**Purpose**: Data validation and serialization using Pydantic

**Key Models**:
- `UserInitialData` - Initial user information
- `ConversationRequest/Response` - Conversation data
- `AssessmentRequest/Result` - Assessment data structures
- `GapAnalysisReport` - Comprehensive report structure
- `SkillGap` - Individual skill gap details

### 3. Configuration (`config.py`)

**Purpose**: Centralized configuration management

**Contains**:
- Skill standards matrix (Junior/Senior/Team Lead requirements)
- Proficiency levels definition
- OpenAI settings
- Application parameters

**Skill Standards Example**:
```python
{
    "React": {
        "Junior": "Basic",
        "Senior": "Expert",
        "Team Lead": "Expert"
    }
}
```

### 4. Services Layer

#### 4.1 OpenAI Service (`services/openai_service.py`)

**Purpose**: Interface with OpenAI API for conversational assessment

**Key Methods**:
- `generate_initial_conversation()` - Create welcoming first message
- `continue_conversation()` - Handle ongoing dialogue
- `generate_assessment()` - Extract skill assessment from conversation

**Process Flow**:
```
User Input → System Prompt + Context → OpenAI API → 
  Response Processing → Determine Next Action
```

**Features**:
- Context-aware conversation
- Automatic conversation completion detection
- Structured skill assessment extraction
- Graceful error handling with fallbacks

#### 4.2 Assessment Service (`services/assessment_service.py`)

**Purpose**: Manage self-assessment tests

**Key Methods**:
- `generate_assessment_test()` - Create personalized test
- `calculate_assessment_scores()` - Process submitted answers
- `_answer_to_score()` - Convert qualitative to quantitative
- `_score_to_proficiency()` - Map scores to proficiency levels

**Test Structure**:
- 2 questions per skill
- Mix of proficiency scales and confidence ratings
- Total ~20 questions covering all skills

**Scoring Algorithm**:
```
Score = (Sum of question scores) / Number of questions
Proficiency = Map score to level (None/Basic/Intermediate/Advanced/Expert)
```

#### 4.3 Gap Analysis Service (`services/gap_analysis_service.py`)

**Purpose**: Generate comprehensive gap analysis reports

**Key Methods**:
- `generate_gap_analysis()` - Main analysis orchestrator
- `_calculate_alignment()` - Compare AI vs self-assessment
- `_generate_learning_path()` - Create personalized roadmap
- `_estimate_time_to_target()` - Calculate timeline

**Analysis Process**:
```
1. Normalize assessments (AI + Self)
2. Compare against standards
3. Calculate gaps for each skill
4. Prioritize (High/Medium/Low)
5. Generate recommendations
6. Create learning path
7. Estimate timeline
```

**Gap Calculation**:
```python
Combined Level = (AI Assessment * 0.6) + (Self Assessment * 0.4)
Gap = Required Level - Combined Level
Priority = High (gap >= 2) | Medium (gap >= 1) | Low (gap < 1)
```

**Readiness Score**:
```python
Readiness = 100 - (Total Gap / Max Possible Gap * 100)
Status: Ready (90+) | Almost Ready (70+) | Needs Improvement (50+) | Not Ready (<50)
```

## Data Flow

### Complete Assessment Flow

```
1. START SESSION
   ├─> User provides: name, current level, target level, experience
   ├─> System creates session with UUID
   └─> AI generates initial greeting and question

2. CONVERSATION PHASE (5-8 turns)
   ├─> User answers questions about experience
   ├─> AI asks follow-up questions about:
   │   ├─> Projects worked on
   │   ├─> Technologies used
   │   ├─> Problem-solving approaches
   │   └─> Team collaboration
   ├─> System tracks conversation history
   └─> AI determines when sufficient information gathered

3. AI ASSESSMENT GENERATION
   ├─> System sends conversation to OpenAI
   ├─> AI analyzes responses
   └─> Returns structured skill levels for each skill

4. SELF-ASSESSMENT PHASE
   ├─> System generates personalized test
   ├─> User answers 20 questions
   ├─> System calculates skill scores
   └─> Converts to proficiency levels

5. GAP ANALYSIS
   ├─> Combine AI (60%) + Self (40%) assessments
   ├─> Compare against target level standards
   ├─> Calculate gaps and priorities
   ├─> Generate recommendations
   ├─> Create learning path
   └─> Estimate timeline to target

6. REPORT DELIVERY
   └─> Return comprehensive JSON report with:
       ├─> Overall readiness score
       ├─> Skill-by-skill breakdown
       ├─> Priority areas
       ├─> Learning path
       └─> Timeline estimate
```

## Session State Management

### Session Object Structure

```python
{
    "session_id": "uuid",
    "user_data": {
        "name": "...",
        "target_level": "...",
        # ... other user info
    },
    "created_at": "ISO timestamp",
    "status": "active | ready_for_self_assessment | assessment_complete | complete",
    "conversation_history": [
        {
            "role": "assistant | user",
            "content": "message text",
            "timestamp": "ISO timestamp"
        }
    ],
    "ai_assessment": {
        "skills": [...],
        "overall_assessment": "...",
        "readiness_for_target": "..."
    },
    "self_assessment": {
        "skills": [...],
        "overall_score": 0.0
    },
    "gap_analysis": { /* full report */ }
}
```

### Status Transitions

```
active → ready_for_self_assessment → assessment_complete → complete
```

## Skill Proficiency Levels

### Level Definitions

1. **None (0)** - No experience or knowledge
2. **Basic (1)** - Fundamental understanding, can perform simple tasks
3. **Intermediate (2)** - Comfortable with common scenarios, some independence
4. **Advanced (3)** - Deep knowledge, handles complex scenarios, mentors others
5. **Expert (4)** - Mastery, innovates, recognized authority

### Mapping to Job Levels

**Junior Developer**:
- Most skills at Basic level
- Learning fundamentals
- Requires guidance
- 0-2 years experience

**Senior Developer**:
- Core skills at Expert/Advanced
- Independent problem solver
- Mentors juniors
- 3-7 years experience

**Team Lead**:
- All skills at Expert/Advanced
- Architects solutions
- Leads teams
- Makes technical decisions
- 7+ years experience

## Security Considerations

### Current Implementation (Development)

⚠️ **Not Production Ready**:
- No authentication
- In-memory storage (data lost on restart)
- No rate limiting
- API keys in environment variables
- No request logging
- No input sanitization beyond Pydantic validation

### Production Requirements

**Must Implement**:

1. **Authentication & Authorization**
   - JWT tokens or OAuth 2.0
   - Role-based access control
   - Session management

2. **Database**
   - PostgreSQL or MongoDB
   - Connection pooling
   - Proper indexing
   - Data encryption at rest

3. **Security**
   - HTTPS/TLS
   - API rate limiting
   - Input validation & sanitization
   - SQL injection prevention
   - XSS protection
   - CSRF tokens

4. **Monitoring**
   - Logging (ELK stack or similar)
   - Error tracking (Sentry)
   - Performance monitoring
   - API usage analytics

5. **Infrastructure**
   - Load balancing
   - Horizontal scaling
   - Caching (Redis)
   - CDN for static assets
   - Backup & disaster recovery

## Scalability Considerations

### Current Limitations

- Single instance (no horizontal scaling)
- In-memory storage (not distributed)
- Synchronous OpenAI calls (blocking)
- No caching

### Scaling Strategy

1. **Database Layer**
   ```
   Replace dict → PostgreSQL/MongoDB
   Add connection pooling
   Implement read replicas
   Add caching layer (Redis)
   ```

2. **Application Layer**
   ```
   Containerize (Docker)
   Deploy to Kubernetes
   Add load balancer
   Implement health checks
   Enable auto-scaling
   ```

3. **API Optimization**
   ```
   Add async/await for OpenAI calls
   Implement request queuing
   Cache AI responses (similar queries)
   Add rate limiting per user
   ```

4. **Performance**
   ```
   Response caching
   Database query optimization
   API response pagination
   Compression (gzip)
   ```

## Testing Strategy

### Unit Tests
- Models validation
- Service logic
- Scoring algorithms
- Gap analysis calculations

### Integration Tests
- API endpoints
- OpenAI service integration
- End-to-end workflows

### Test Example
```python
def test_gap_analysis():
    ai_assessment = {...}
    self_assessment = {...}
    
    report = gap_analysis_service.generate_gap_analysis(
        ai_assessment, self_assessment, "Senior", "Junior"
    )
    
    assert report["overall_readiness"] >= 0
    assert report["overall_readiness"] <= 100
    assert len(report["skill_gaps"]) == 10
```

## Extension Points

### Easy to Add

1. **New Skills**
   - Update `SKILL_STANDARDS` in `config.py`
   - Add questions in `assessment_service.py`
   - Update documentation

2. **Different Job Roles**
   - Add role definitions
   - Create role-specific standards
   - Customize questions per role

3. **Multiple Languages**
   - Add language parameter
   - Localize prompts
   - Translate responses

4. **Export Formats**
   - PDF reports
   - Excel spreadsheets
   - Email delivery

5. **Integrations**
   - Learning platforms (Udemy, Coursera)
   - HR systems
   - Slack/Teams notifications

## Deployment

### Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
# Using Gunicorn with Uvicorn workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or Docker
docker build -t skill-assessment-api .
docker run -p 8000:8000 skill-assessment-api
```

### Environment Variables
```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=...
```

## Performance Metrics

### Expected Response Times
- Session start: 2-5 seconds (OpenAI call)
- Conversation turn: 2-5 seconds (OpenAI call)
- Get assessment test: < 100ms (no external calls)
- Submit assessment: < 100ms (calculations only)
- Gap analysis: < 500ms (complex calculations)

### Throughput
- Current: ~10 concurrent users
- With scaling: 1000+ concurrent users

## Future Enhancements

1. **AI Improvements**
   - Multi-model support (Claude, Gemini)
   - Voice conversation support
   - Coding challenges integration
   - Portfolio analysis

2. **Features**
   - Progress tracking over time
   - Team assessments
   - Custom skill matrices
   - Interview preparation mode

3. **Analytics**
   - Industry benchmarking
   - Skill trend analysis
   - Hiring insights
   - Learning effectiveness tracking

## Support & Maintenance

### Monitoring Checklist
- [ ] API uptime
- [ ] Response times
- [ ] Error rates
- [ ] OpenAI API usage & costs
- [ ] Database performance
- [ ] Storage usage

### Regular Maintenance
- Update dependencies
- Review and update skill standards
- Analyze user feedback
- Optimize prompts based on results
- Update assessment questions

---

For questions or contributions, please refer to the main README.md

