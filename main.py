from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
import uuid

from models import (
    UserInitialData, ConversationRequest, ConversationResponse,
    AssessmentRequest, AssessmentResult, GapAnalysisRequest, GapAnalysisReport
)
from services.openai_service import OpenAIService
from services.assessment_service import AssessmentService
from services.gap_analysis_service import GapAnalysisService
from services.learning_path_service import LearningPathService
from services.content_generation_service import ContentGenerationService

app = FastAPI(
    title="Skill Assessment API",
    description="AI-powered skill assessment and gap analysis system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
openai_service = OpenAIService()
assessment_service = AssessmentService()
gap_analysis_service = GapAnalysisService()
learning_path_service = LearningPathService()
content_generation_service = ContentGenerationService()

# Content cache (in production, use Redis or similar)
content_cache = {}

# In-memory storage (replace with database in production)
sessions = {}
conversations = {}
assessments = {}

# User progress tracking (in production, use database)
user_progress = {}  # {session_id: {content_id: {completed: bool, xp_earned: int, answers: []}}}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "message": "Skill Assessment API is operational",
        "version": "1.0.0"
    }


@app.post("/api/session/start", response_model=Dict)
async def start_session(user_data: UserInitialData):
    """
    Start a new assessment session with user's initial data
    """
    session_id = str(uuid.uuid4())
    
    sessions[session_id] = {
        "session_id": session_id,
        "user_data": user_data.dict(),
        "created_at": datetime.now().isoformat(),
        "status": "active",
        "conversation_history": [],
        "ai_assessment": None,
        "self_assessment": None,
        "gap_analysis": None
    }
    
    # Generate initial conversation prompt
    initial_message = await openai_service.generate_initial_conversation(user_data)
    
    sessions[session_id]["conversation_history"].append({
        "role": "assistant",
        "content": initial_message,
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        "session_id": session_id,
        "message": initial_message,
        "status": "conversation_started"
    }


@app.post("/api/conversation/{session_id}", response_model=ConversationResponse)
async def continue_conversation(session_id: str, request: ConversationRequest):
    """
    Continue the conversation with the AI
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Add user message to history
    session["conversation_history"].append({
        "role": "user",
        "content": request.message,
        "timestamp": datetime.now().isoformat()
    })
    
    # Get AI response
    ai_response = await openai_service.continue_conversation(
        session["conversation_history"],
        session["user_data"]
    )
    
    session["conversation_history"].append({
        "role": "assistant",
        "content": ai_response["message"],
        "timestamp": datetime.now().isoformat()
    })
    
    # Check if conversation should end
    if ai_response.get("conversation_complete", False):
        # Generate AI assessment
        ai_assessment = await openai_service.generate_assessment(
            session["conversation_history"],
            session["user_data"]
        )
        session["ai_assessment"] = ai_assessment
        session["status"] = "ready_for_self_assessment"
    
    return ConversationResponse(
        message=ai_response["message"],
        conversation_complete=ai_response.get("conversation_complete", False),
        next_step=ai_response.get("next_step", "continue_conversation")
    )


@app.get("/api/conversation/{session_id}/history")
async def get_conversation_history(session_id: str):
    """
    Get conversation history for a session
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "history": sessions[session_id]["conversation_history"]
    }


@app.get("/api/assessment/test/{session_id}")
async def get_assessment_test(session_id: str):
    """
    Get the self-assessment test questions
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Generate personalized test based on target level
    test = assessment_service.generate_assessment_test(
        session["user_data"]["target_level"]
    )
    
    return {
        "session_id": session_id,
        "test": test,
        "instructions": "Please answer all questions honestly. This will help us provide accurate gap analysis."
    }


@app.post("/api/assessment/submit/{session_id}", response_model=GapAnalysisReport)
async def submit_assessment(session_id: str, request: AssessmentRequest):
    """
    Submit self-assessment test results and automatically generate gap analysis
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    if not session.get("ai_assessment"):
        raise HTTPException(
            status_code=400,
            detail="AI assessment not complete. Please complete the conversation first."
        )
    
    # Calculate self-assessment scores
    self_assessment = assessment_service.calculate_assessment_scores(request.answers)
    session["self_assessment"] = self_assessment
    session["status"] = "assessment_complete"
    
    # Automatically generate gap analysis
    gap_analysis = gap_analysis_service.generate_gap_analysis(
        ai_assessment=session["ai_assessment"],
        self_assessment=self_assessment,
        target_level=session["user_data"]["target_level"],
        current_level=session["user_data"].get("current_level", "Junior")
    )
    
    # Add session info to gap analysis
    gap_analysis["session_id"] = session_id
    gap_analysis["user_name"] = session["user_data"].get("name", "User")
    
    session["gap_analysis"] = gap_analysis
    session["status"] = "complete"
    
    return gap_analysis


@app.post("/api/gap-analysis/{session_id}", response_model=GapAnalysisReport)
async def generate_gap_analysis(session_id: str):
    """
    Generate comprehensive gap analysis report
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    if not session.get("ai_assessment") or not session.get("self_assessment"):
        raise HTTPException(
            status_code=400,
            detail="Complete conversation and self-assessment first"
        )
    
    # Generate gap analysis
    gap_analysis = gap_analysis_service.generate_gap_analysis(
        ai_assessment=session["ai_assessment"],
        self_assessment=session["self_assessment"],
        target_level=session["user_data"]["target_level"],
        current_level=session["user_data"].get("current_level", "Junior")
    )
    
    session["gap_analysis"] = gap_analysis
    session["status"] = "complete"
    
    return gap_analysis


@app.post("/api/learning-path/{session_id}")
async def generate_learning_path(session_id: str, request: Dict = Body(default={})):
    """
    Generate personalized learning paths based on gap analysis
    
    Expects gap analysis to be completed first.
    Request body can optionally include role: {"role": "Frontend Engineer"}
    Returns learning paths for skills that need improvement.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    if not session.get("gap_analysis"):
        raise HTTPException(
            status_code=400,
            detail="Complete gap analysis first"
        )
    
    gap_analysis = session["gap_analysis"]
    
    # Get role from request body, or default to "Frontend Engineer"
    role = request.get("role", "Frontend Engineer") if request else "Frontend Engineer"
    
    # Extract skill ratings from gap analysis
    skill_ratings = []
    
    # Add skills with gaps
    for skill_gap in gap_analysis.get("skill_gaps", []):
        skill_ratings.append({
            "skill_name": skill_gap.get("skill"),
            "current_level": skill_gap.get("current_level", "Basic")
        })
    
    # Add skills that need improvement
    for skill in gap_analysis.get("skills_need_improvement", []):
        # Check if already added
        if not any(sr["skill_name"] == skill for sr in skill_ratings):
            skill_ratings.append({
                "skill_name": skill,
                "current_level": "Intermediate"  # Default, could be improved
            })
    
    # Generate learning paths
    learning_paths = learning_path_service.generate_learning_paths(
        role=role,
        skill_ratings=skill_ratings
    )
    
    # Store learning paths in session
    session["learning_paths"] = learning_paths
    
    return learning_paths


@app.post("/api/content/generate/{session_id}")
async def generate_content(
    session_id: str,
    request: Dict = Body(...)
):
    """
    Generate AI content on-demand (lazy loading)
    
    Request body:
    {
        "content_type": "lesson" | "quiz" | "coding_challenge" | "flashcards" | "summary",
        "skill": "string",
        "milestone_number": int,
        "current_level": "string",
        "target_level": "string",
        "role": "string"
    }
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    user_data = session.get("user_data", {})
    role = request.get("role", "Frontend Engineer")
    
    content_type = request.get("content_type")
    skill = request.get("skill")
    milestone_number = request.get("milestone_number")
    current_level = request.get("current_level", "Basic")
    target_level = request.get("target_level", "Intermediate")
    
    if not all([content_type, skill, milestone_number]):
        raise HTTPException(
            status_code=400,
            detail="Missing required fields: content_type, skill, milestone_number"
        )
    
    # Check cache first
    cache_key = f"{session_id}_{content_type}_{skill}_{milestone_number}"
    if cache_key in content_cache:
        return {
            "cached": True,
            "content": content_cache[cache_key]
        }
    
    # Generate content based on type
    try:
        if content_type == "lesson":
            content = await content_generation_service.generate_lesson(
                skill=skill,
                milestone_number=milestone_number,
                current_level=current_level,
                target_level=target_level,
                role=role
            )
        elif content_type == "quiz":
            content = await content_generation_service.generate_quiz(
                skill=skill,
                milestone_number=milestone_number,
                current_level=current_level,
                target_level=target_level,
                role=role
            )
        elif content_type == "coding_challenge":
            content = await content_generation_service.generate_coding_challenge(
                skill=skill,
                milestone_number=milestone_number,
                current_level=current_level,
                target_level=target_level,
                role=role
            )
        elif content_type == "flashcards":
            content = await content_generation_service.generate_flashcards(
                skill=skill,
                milestone_number=milestone_number,
                current_level=current_level,
                target_level=target_level,
                role=role
            )
        elif content_type == "summary":
            content = await content_generation_service.generate_summary(
                skill=skill,
                milestone_number=milestone_number,
                current_level=current_level,
                target_level=target_level,
                role=role
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid content_type: {content_type}. Must be one of: lesson, quiz, coding_challenge, flashcards, summary"
            )
        
        # Cache the content
        content_cache[cache_key] = content
        
        return {
            "cached": False,
            "content": content
        }
    except Exception as e:
        print(f"Error generating content: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate content: {str(e)}"
        )


@app.get("/api/content/{session_id}")
async def get_cached_content(
    session_id: str,
    content_type: str,
    skill: str,
    milestone_number: int
):
    """
    Get cached content if available
    """
    cache_key = f"{session_id}_{content_type}_{skill}_{milestone_number}"
    if cache_key in content_cache:
        return {
            "cached": True,
            "content": content_cache[cache_key]
        }
    else:
        raise HTTPException(
            status_code=404,
            detail="Content not found. Generate it first using /api/content/generate/{session_id}"
        )


@app.post("/api/content/complete/{session_id}")
async def mark_content_complete(
    session_id: str,
    request: Dict = Body(...)
):
    """
    Mark content as complete and award XP
    
    Request body:
    {
        "content_id": "string",
        "content_type": "lesson" | "quiz" | "coding_challenge" | "flashcards" | "summary",
        "skill": "string",
        "milestone_number": int,
        "quiz_answers": [{"question_id": "string", "answer": "string"}] (for quizzes only),
        "marked_as_read": true (for lessons only)
    }
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    content_id = request.get("content_id")
    content_type = request.get("content_type")
    skill = request.get("skill")
    milestone_number = request.get("milestone_number")
    
    if not all([content_id, content_type, skill, milestone_number]):
        raise HTTPException(
            status_code=400,
            detail="Missing required fields: content_id, content_type, skill, milestone_number"
        )
    
    # Initialize progress tracking for session if not exists
    if session_id not in user_progress:
        user_progress[session_id] = {}
    
    # Get content to determine XP
    cache_key = f"{session_id}_{content_type}_{skill}_{milestone_number}"
    content = content_cache.get(cache_key)
    
    if not content:
        raise HTTPException(
            status_code=404,
            detail="Content not found. Generate it first."
        )
    
    xp_earned = 0
    passed = False
    
    # Handle different content types
    if content_type == "quiz":
        # Validate quiz answers
        quiz_answers = request.get("quiz_answers", [])
        if not quiz_answers:
            raise HTTPException(
                status_code=400,
                detail="Quiz answers required for quiz completion"
            )
        
        # Check answers against correct answers
        quiz_content = content.get("content", {})
        questions = quiz_content.get("questions", [])
        passing_score = content.get("passing_score", 70)
        
        correct_count = 0
        total_questions = len(questions)
        
        # Create a map of question IDs to questions for faster lookup
        question_map = {}
        for idx, q in enumerate(questions):
            q_id = q.get("id") or f"q{idx + 1}"
            question_map[q_id] = q
        
        for answer in quiz_answers:
            question_id = answer.get("question_id")
            user_answer = answer.get("answer")
            
            # Find the question using the map
            question = question_map.get(question_id)
            if question:
                correct_answer = question.get("correct_answer")
                # Compare answers (case-insensitive, trimmed)
                if correct_answer and str(correct_answer).strip().lower() == str(user_answer).strip().lower():
                    correct_count += 1
        
        score_percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
        passed = score_percentage >= passing_score
        
        if passed:
            xp_earned = content.get("xp", 0)
        else:
            xp_earned = 0  # No XP if quiz not passed
    
    elif content_type == "lesson":
        # For lessons, just mark as read
        marked_as_read = request.get("marked_as_read", True)
        if marked_as_read:
            xp_earned = content.get("xp", 0)
    
    elif content_type in ["coding_challenge", "flashcards", "summary"]:
        # For other types, mark as complete and award XP
        xp_earned = content.get("xp", 0)
        passed = True
    
    # Calculate score for quiz
    score = None
    if content_type == "quiz":
        score = (correct_count / total_questions * 100) if total_questions > 0 else 0
    
    # Store progress
    user_progress[session_id][content_id] = {
        "completed": True,
        "xp_earned": xp_earned,
        "completed_at": datetime.now().isoformat(),
        "content_type": content_type,
        "passed": passed,
        "quiz_answers": request.get("quiz_answers") if content_type == "quiz" else None,
        "score": score
    }
    
    # Update session total XP
    if "total_xp" not in sessions[session_id]:
        sessions[session_id]["total_xp"] = 0
    sessions[session_id]["total_xp"] += xp_earned
    
    return {
        "success": True,
        "content_id": content_id,
        "xp_earned": xp_earned,
        "passed": passed,
        "score": score,
        "total_xp": sessions[session_id]["total_xp"],
        "message": "Content completed successfully" if passed else f"Quiz not passed. Your score: {score:.0f}% (Required: {passing_score}%)"
    }


@app.get("/api/progress/{session_id}")
async def get_user_progress(session_id: str):
    """
    Get user's progress and XP summary
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    progress_data = user_progress.get(session_id, {})
    total_xp = sessions[session_id].get("total_xp", 0)
    completed_count = sum(1 for p in progress_data.values() if p.get("completed", False))
    
    return {
        "session_id": session_id,
        "total_xp": total_xp,
        "completed_tasks": completed_count,
        "progress": progress_data
    }


@app.get("/api/progress/{session_id}/content/{content_id}")
async def get_content_progress(session_id: str, content_id: str):
    """
    Get progress for a specific content item
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    progress_data = user_progress.get(session_id, {})
    content_progress = progress_data.get(content_id)
    
    if not content_progress:
        return {
            "content_id": content_id,
            "completed": False,
            "xp_earned": 0
        }
    
    return content_progress


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """
    Get complete session data
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return sessions[session_id]


@app.get("/api/sessions")
async def list_sessions():
    """
    List all sessions (for admin/debugging)
    """
    return {
        "total_sessions": len(sessions),
        "sessions": [
            {
                "session_id": sid,
                "created_at": data["created_at"],
                "status": data["status"],
                "user_name": data["user_data"].get("name", "Unknown")
            }
            for sid, data in sessions.items()
        ]
    }


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions[session_id]
    return {"message": "Session deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

