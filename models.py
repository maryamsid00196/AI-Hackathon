from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from datetime import datetime


class UserInitialData(BaseModel):
    """Initial data provided by user"""
    name: str = Field(..., description="User's name")
    email: Optional[str] = Field(None, description="User's email")
    current_level: Literal["Junior", "Senior", "Team Lead"] = Field(
        "Junior",
        description="User's current experience level"
    )
    target_level: Literal["Junior", "Senior", "Team Lead"] = Field(
        ...,
        description="Target level user wants to achieve"
    )
    years_of_experience: Optional[float] = Field(None, description="Years of experience")
    primary_technologies: Optional[List[str]] = Field(
        None,
        description="List of technologies user works with"
    )
    additional_info: Optional[str] = Field(None, description="Any additional information")


class ConversationRequest(BaseModel):
    """Request for continuing conversation"""
    message: str = Field(..., description="User's message")


class ConversationResponse(BaseModel):
    """Response from conversation"""
    message: str = Field(..., description="AI's response")
    conversation_complete: bool = Field(False, description="Whether conversation is complete")
    next_step: str = Field("continue_conversation", description="Next step in the process")


class AssessmentAnswer(BaseModel):
    """Single answer in assessment"""
    question_id: str
    skill: str
    answer: str
    confidence_level: Optional[int] = Field(None, ge=1, le=5, description="Confidence 1-5")


class AssessmentRequest(BaseModel):
    """Self-assessment submission"""
    answers: List[AssessmentAnswer]


class SkillLevel(BaseModel):
    """Skill proficiency level"""
    skill: str
    proficiency: Literal["None", "Basic", "Intermediate", "Advanced", "Expert"]
    confidence: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class AssessmentResult(BaseModel):
    """Assessment results"""
    skills: List[SkillLevel]
    overall_score: float
    strengths: List[str]
    weaknesses: List[str]


class SkillGap(BaseModel):
    """Gap for a specific skill"""
    skill: str
    current_level: str
    required_level: str
    gap: str
    ai_assessed_level: Optional[str] = None
    self_assessed_level: Optional[str] = None
    priority: Literal["High", "Medium", "Low"]
    recommendations: List[str]


class GapAnalysisRequest(BaseModel):
    """Request for gap analysis"""
    session_id: str


class GapAnalysisReport(BaseModel):
    """Comprehensive gap analysis report"""
    session_id: str
    user_name: str
    current_level: str
    target_level: str
    generated_at: str
    
    # Overall assessment
    overall_readiness: float = Field(..., ge=0, le=100, description="Overall readiness percentage")
    readiness_status: Literal["Not Ready", "Needs Improvement", "Almost Ready", "Ready"]
    
    # Skill gaps
    skill_gaps: List[SkillGap]
    
    # Summary
    skills_on_track: List[str]
    skills_need_improvement: List[str]
    critical_gaps: List[str]
    
    # Recommendations
    learning_path: List[Dict[str, str]]
    estimated_time_to_target: str
    priority_areas: List[str]
    
    # Detailed comparison
    ai_vs_self_assessment_alignment: float = Field(
        ...,
        ge=0,
        le=100,
        description="How well AI and self-assessment align"
    )
    assessment_notes: Optional[str] = None


class SkillStandard(BaseModel):
    """Standard skill requirements by level"""
    skill: str
    junior: Literal["None", "Basic", "Intermediate", "Advanced", "Expert"]
    senior: Literal["None", "Basic", "Intermediate", "Advanced", "Expert"]
    team_lead: Literal["None", "Basic", "Intermediate", "Advanced", "Expert"]

