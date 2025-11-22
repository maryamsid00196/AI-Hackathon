from fastapi import FastAPI, HTTPException
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

# In-memory storage (replace with database in production)
sessions = {}
conversations = {}
assessments = {}


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

