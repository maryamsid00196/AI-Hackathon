from typing import Dict, List, Any
import uuid
from config import config


class AssessmentService:
    """Service for handling self-assessment tests"""
    
    def __init__(self):
        self.skill_standards = config.SKILL_STANDARDS
        self.proficiency_levels = config.PROFICIENCY_LEVELS
    
    def generate_assessment_test(self, target_level: str) -> Dict[str, Any]:
        """
        Generate a self-assessment test based on target level
        """
        questions = []
        
        # Define questions for each skill
        skill_questions = {
            "HTML": [
                {
                    "id": str(uuid.uuid4()),
                    "skill": "HTML",
                    "question": "How comfortable are you with semantic HTML5 elements and accessibility features?",
                    "type": "proficiency",
                    "options": self.proficiency_levels
                },
                {
                    "id": str(uuid.uuid4()),
                    "skill": "HTML",
                    "question": "Can you explain and implement complex HTML structures like forms with validation?",
                    "type": "boolean_with_confidence",
                    "options": ["Yes", "Somewhat", "No"]
                }
            ],
            "CSS": [
                {
                    "id": str(uuid.uuid4()),
                    "skill": "CSS",
                    "question": "Rate your proficiency with modern CSS (Flexbox, Grid, Animations, Custom Properties)?",
                    "type": "proficiency",
                    "options": self.proficiency_levels
                },
                {
                    "id": str(uuid.uuid4()),
                    "skill": "CSS",
                    "question": "How comfortable are you with CSS preprocessors (SASS/LESS) and CSS-in-JS solutions?",
                    "type": "proficiency",
                    "options": self.proficiency_levels
                }
            ],
            "JavaScript": [
                {
                    "id": str(uuid.uuid4()),
                    "skill": "JavaScript",
                    "question": "Rate your understanding of modern JavaScript (ES6+, async/await, closures, etc.)?",
                    "type": "proficiency",
                    "options": self.proficiency_levels
                },
                {
                    "id": str(uuid.uuid4()),
                    "skill": "JavaScript",
                    "question": "Can you effectively debug complex JavaScript issues and optimize code performance?",
                    "type": "boolean_with_confidence",
                    "options": ["Yes", "Somewhat", "No"]
                }
            ],
            "React": [
                {
                    "id": str(uuid.uuid4()),
                    "skill": "React",
                    "question": "How proficient are you with React hooks, context API, and component lifecycle?",
                    "type": "proficiency",
                    "options": self.proficiency_levels
                },
                {
                    "id": str(uuid.uuid4()),
                    "skill": "React",
                    "question": "Can you architect and build complex React applications from scratch?",
                    "type": "boolean_with_confidence",
                    "options": ["Yes", "Somewhat", "No"]
                }
            ],
            "Next.js": [
                {
                    "id": str(uuid.uuid4()),
                    "skill": "Next.js",
                    "question": "Rate your experience with Next.js features (SSR, SSG, API routes, routing)?",
                    "type": "proficiency",
                    "options": self.proficiency_levels
                },
                {
                    "id": str(uuid.uuid4()),
                    "skill": "Next.js",
                    "question": "Have you deployed and optimized Next.js applications in production?",
                    "type": "boolean_with_confidence",
                    "options": ["Yes", "Somewhat", "No"]
                }
            ],
            "Git Basics": [
                {
                    "id": str(uuid.uuid4()),
                    "skill": "Git Basics",
                    "question": "How comfortable are you with Git workflows (branching, merging, rebasing, PR reviews)?",
                    "type": "proficiency",
                    "options": self.proficiency_levels
                },
                {
                    "id": str(uuid.uuid4()),
                    "skill": "Git Basics",
                    "question": "Can you resolve complex merge conflicts and manage collaborative Git workflows?",
                    "type": "boolean_with_confidence",
                    "options": ["Yes", "Somewhat", "No"]
                }
            ],
            "Debugging Skills": [
                {
                    "id": str(uuid.uuid4()),
                    "skill": "Debugging Skills",
                    "question": "Rate your debugging skills using browser DevTools and debugging techniques?",
                    "type": "proficiency",
                    "options": self.proficiency_levels
                },
                {
                    "id": str(uuid.uuid4()),
                    "skill": "Debugging Skills",
                    "question": "Can you efficiently track down and fix bugs in complex codebases?",
                    "type": "boolean_with_confidence",
                    "options": ["Yes", "Somewhat", "No"]
                }
            ],
            "API Integration": [
                {
                    "id": str(uuid.uuid4()),
                    "skill": "API Integration",
                    "question": "How proficient are you with REST APIs, fetch/axios, and handling API responses?",
                    "type": "proficiency",
                    "options": self.proficiency_levels
                },
                {
                    "id": str(uuid.uuid4()),
                    "skill": "API Integration",
                    "question": "Can you implement authentication, error handling, and API rate limiting?",
                    "type": "boolean_with_confidence",
                    "options": ["Yes", "Somewhat", "No"]
                }
            ],
            "State Management (Redux/Zustand)": [
                {
                    "id": str(uuid.uuid4()),
                    "skill": "State Management (Redux/Zustand)",
                    "question": "Rate your experience with state management libraries (Redux, Zustand, etc.)?",
                    "type": "proficiency",
                    "options": self.proficiency_levels
                },
                {
                    "id": str(uuid.uuid4()),
                    "skill": "State Management (Redux/Zustand)",
                    "question": "Can you architect and implement complex state management solutions?",
                    "type": "boolean_with_confidence",
                    "options": ["Yes", "Somewhat", "No"]
                }
            ],
            "Performance Optimization": [
                {
                    "id": str(uuid.uuid4()),
                    "skill": "Performance Optimization",
                    "question": "How familiar are you with performance optimization techniques (lazy loading, code splitting, memoization)?",
                    "type": "proficiency",
                    "options": self.proficiency_levels
                },
                {
                    "id": str(uuid.uuid4()),
                    "skill": "Performance Optimization",
                    "question": "Can you identify performance bottlenecks and implement optimization strategies?",
                    "type": "boolean_with_confidence",
                    "options": ["Yes", "Somewhat", "No"]
                }
            ]
        }
        
        # Generate test
        for skill, skill_qs in skill_questions.items():
            questions.extend(skill_qs)
        
        return {
            "total_questions": len(questions),
            "skills_covered": list(skill_questions.keys()),
            "target_level": target_level,
            "questions": questions
        }
    
    def calculate_assessment_scores(self, answers: List[Dict]) -> Dict[str, Any]:
        """
        Calculate self-assessment scores from answers
        """
        skill_scores = {}
        
        for answer in answers:
            # Handle both Pydantic models and dictionaries
            if hasattr(answer, 'skill'):
                # Pydantic model
                skill = answer.skill
                answer_text = answer.answer
                confidence_level = answer.confidence_level if (hasattr(answer, 'confidence_level') and answer.confidence_level is not None) else 3
            else:
                # Dictionary
                skill = answer["skill"]
                answer_text = answer["answer"]
                confidence_level = answer.get("confidence_level") if answer.get("confidence_level") is not None else 3
            
            if skill not in skill_scores:
                skill_scores[skill] = {
                    "responses": [],
                    "total_score": 0,
                    "count": 0
                }
            
            # Convert answer to numeric score
            score = self._answer_to_score(answer_text)
            
            skill_scores[skill]["responses"].append({
                "answer": answer_text,
                "score": score,
                "confidence": confidence_level
            })
            skill_scores[skill]["total_score"] += score
            skill_scores[skill]["count"] += 1
        
        # Calculate average scores and determine proficiency levels
        skills = []
        for skill, data in skill_scores.items():
            avg_score = data["total_score"] / data["count"] if data["count"] > 0 else 0
            proficiency = self._score_to_proficiency(avg_score)
            
            # Calculate average confidence, handling None values
            confidence_values = [r["confidence"] for r in data["responses"] if r["confidence"] is not None]
            avg_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 3.0
            
            skills.append({
                "skill": skill,
                "proficiency": proficiency,
                "score": round(avg_score, 2),
                "confidence": round(avg_confidence, 2)
            })
        
        # Calculate overall metrics
        overall_score = sum(s["score"] for s in skills) / len(skills) if skills else 0
        
        return {
            "skills": skills,
            "overall_score": round(overall_score, 2),
            "assessment_date": None  # Will be set by caller
        }
    
    def _answer_to_score(self, answer: str) -> float:
        """Convert answer text to numeric score"""
        answer_lower = answer.lower()
        
        # Map proficiency levels
        if answer_lower in ["none", "no"]:
            return 0.0
        elif answer_lower in ["basic", "somewhat"]:
            return 1.0
        elif answer_lower == "intermediate":
            return 2.0
        elif answer_lower == "advanced":
            return 3.0
        elif answer_lower in ["expert", "yes"]:
            return 4.0
        else:
            return 2.0  # Default to intermediate
    
    def _score_to_proficiency(self, score: float) -> str:
        """Convert numeric score to proficiency level"""
        if score < 0.5:
            return "None"
        elif score < 1.5:
            return "Basic"
        elif score < 2.5:
            return "Intermediate"
        elif score < 3.5:
            return "Advanced"
        else:
            return "Expert"

