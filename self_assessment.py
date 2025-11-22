from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restx import Api, Resource, fields, Namespace
import json
from datetime import datetime
from typing import Dict, List, Optional
import os
import openai

app = Flask(__name__)
CORS(app)

# Flask-RESTX API setup (better than Flasgger for REST APIs)
api = Api(
    app,
    version='1.0',
    title='Skill Assessment API',
    description='AI-powered skill assessment system with conversation, self-assessment, and gap analysis',
    doc='/docs',
    prefix='/api'
)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_base = 'https://openai.dplit.com/v1'

# Namespaces
assessment_ns = Namespace('assessment', description='Assessment operations')
conversation_ns = Namespace('conversation', description='AI conversation operations')
reports_ns = Namespace('reports', description='Reports and results')

api.add_namespace(assessment_ns, path='/assessment')
api.add_namespace(conversation_ns, path='/conversation')
api.add_namespace(reports_ns, path='/reports')

# In-memory storage
user_sessions = {}

# Skill standards database
skill_standards = {
    "Junior Software Engineer": {
        "backend_development": {
            "beginner": {"score": 30, "skills": ["Basic CRUD operations", "Simple API endpoints"]},
            "intermediate": {"score": 60, "skills": ["RESTful API design", "Authentication", "Database optimization"]},
            "advanced": {"score": 90, "skills": ["Microservices", "System design", "Performance optimization"]}
        }
    }
}

# ========== API Models ==========

start_assessment_model = api.model('StartAssessment', {
    'role': fields.String(required=True, description='Current job role', example='Junior Software Engineer'),
    'tech_stack': fields.List(fields.String, required=True, description='Technologies you work with', 
                              example=['JavaScript', 'Python', 'React']),
    'proficiency': fields.String(required=True, description='Proficiency level', 
                                enum=['beginner', 'intermediate', 'advanced'], example='intermediate'),
    'learning_goals': fields.String(required=True, description='Your learning objectives',
                                   example='I want to become a full-stack developer')
})

start_assessment_response = api.model('StartAssessmentResponse', {
    'session_id': fields.String(description='Session identifier'),
    'message': fields.String(description='Status message'),
    'initial_question': fields.String(description='First AI question'),
    'next_step': fields.String(description='Next step in process')
})

conversation_model = api.model('Conversation', {
    'session_id': fields.String(required=True, description='Session ID'),
    'message': fields.String(required=True, description='Your response', 
                            example='I built a REST API using Node.js')
})

conversation_response = api.model('ConversationResponse', {
    'message': fields.String(description='AI response'),
    'conversation_complete': fields.Boolean(description='Is conversation finished'),
    'turn': fields.Integer(description='Current turn number'),
    'error': fields.String(description='Error message if any', skip_none=True)
})

test_question = api.model('TestQuestion', {
    'id': fields.Integer(description='Question ID'),
    'category': fields.String(description='Question category'),
    'question': fields.String(description='Question text'),
    'type': fields.String(description='Question type'),
    'scale': fields.String(description='Answer scale')
})

test_response_item = api.model('TestResponseItem', {
    'question_id': fields.Integer(required=True, description='Question ID'),
    'answer': fields.Integer(required=True, description='Answer (1-5)', min=1, max=5)
})

submit_test_model = api.model('SubmitTest', {
    'session_id': fields.String(required=True, description='Session ID'),
    'responses': fields.List(fields.Nested(test_response_item), required=True, description='Test responses')
})

# ========== Assessment System Class ==========

class SkillAssessmentSystem:
    def __init__(self, user_data: Dict):
        self.user_data = user_data
        self.conversation_history = []
        self.ai_assessment = {}
        self.self_assessment_results = {}
        
    def generate_conversation_prompt(self, user_message: Optional[str] = None) -> List[Dict]:
        if not self.conversation_history:
            tech_stack = ", ".join(self.user_data.get('tech_stack', []))
            system_prompt = f"""You are a technical skill assessor. The candidate is a {self.user_data['role']} with {self.user_data['proficiency']} level. Tech stack: {tech_stack}.

Ask about:
1. Recent projects (role, tech, challenges)
2. Technical depth questions
3. Problem-solving approach

Keep responses to 2-3 sentences.
Each response from your side should be a question and the user should be evaluated based on the response.
"""
            
            return [
                {"role": "system", "content": system_prompt},
                {"role": "assistant", "content": "Hi! Let's discuss your experience. Can you tell me about your most recent project?"}
            ]
        else:
            messages = [{"role": "system", "content": "Continue technical assessment. Keep responses brief."}]
            for msg in self.conversation_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
            if user_message:
                messages.append({"role": "user", "content": user_message})
            return messages

    def get_ai_response(self, user_message: Optional[str] = None) -> Dict:
     try:
        messages = self.generate_conversation_prompt(user_message)
        
        response = openai.ChatCompletion.create(  # ← Old syntax
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )
        
        ai_message = response.choices[0].message.content
        
        if user_message:
            self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": ai_message})
        
        conversation_complete = len(self.conversation_history) >= 12
        
        return {
            "message": ai_message,
            "conversation_complete": conversation_complete,
            "turn": len(self.conversation_history) // 2
        }
     except Exception as e:
        print(f"❌ OPENAI ERROR: {e}")
        return {
            "message": "Tell me about a recent project you worked on.",
            "conversation_complete": False,
            "turn": 0,
            "error": str(e)
        }

    def generate_ai_assessment(self) -> Dict:
        try:
            conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.conversation_history])
            
            assessment_prompt = f"""Based on this technical interview:

{conversation_text}

Provide assessment as JSON:
{{
    "technical_skills": {{"score": 0-100, "details": "summary"}},
    "problem_solving": {{"score": 0-100, "details": "summary"}},
    "experience_level": {{"score": 0-100, "details": "summary"}},
    "communication": {{"score": 0-100, "details": "summary"}},
    "overall_score": 0-100,
    "strengths": ["strength1", "strength2"],
    "areas_for_improvement": ["area1", "area2"]
}}"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": assessment_prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
            assessment = json.loads(content)
            self.ai_assessment = assessment
            return assessment
        except Exception as e:
            return {
                "technical_skills": {"score": 60, "details": "Moderate technical knowledge"},
                "problem_solving": {"score": 55, "details": "Good problem-solving approach"},
                "experience_level": {"score": 50, "details": "Intermediate level"},
                "communication": {"score": 65, "details": "Clear communication"},
                "overall_score": 57,
                "strengths": ["Good foundation", "Willing to learn"],
                "areas_for_improvement": ["Deepen technical knowledge", "More experience"],
                "error": str(e)
            }

    def generate_self_assessment_test(self) -> List[Dict]:
        questions = [
            {"id": 1, "category": "API Design", "question": "How comfortable are you designing RESTful APIs?", "type": "scale", "scale": "1-5"},
            {"id": 2, "category": "Database", "question": "Rate your ability to write complex SQL queries.", "type": "scale", "scale": "1-5"},
            {"id": 3, "category": "Security", "question": "How well do you understand authentication patterns?", "type": "scale", "scale": "1-5"},
            {"id": 4, "category": "Architecture", "question": "Rate your understanding of system design.", "type": "scale", "scale": "1-5"},
            {"id": 5, "category": "Problem Solving", "question": "How often do you break problems into smaller tasks?", "type": "scale", "scale": "1-5"},
            {"id": 6, "category": "Learning", "question": "How quickly can you learn new technologies?", "type": "scale", "scale": "1-5"}
        ]
        
        tech_stack = self.user_data.get('tech_stack', [])
        for i, tech in enumerate(tech_stack[:3], 7):
            questions.append({
                "id": i, "category": tech, 
                "question": f"Rate your proficiency in {tech}.", 
                "type": "scale", "scale": "1-5"
            })
        
        return questions

    def calculate_combined_assessment(self) -> Dict:
        ai_score = self.ai_assessment.get('overall_score', 50)
        responses = self.self_assessment_results.get('responses', [])
        self_score = (sum(r['answer'] for r in responses) / len(responses)) * 20 if responses else 50
        combined_score = (ai_score * 0.6) + (self_score * 0.4)
        
        return {
            "ai_score": round(ai_score, 2),
            "self_assessment_score": round(self_score, 2),
            "combined_score": round(combined_score, 2),
            "ai_assessment": self.ai_assessment,
            "self_assessment": self.self_assessment_results
        }

    def generate_gap_analysis(self, combined_assessment: Dict) -> Dict:
        role = self.user_data['role']
        target_standard = skill_standards.get(role, {}).get('backend_development', {}).get('advanced', {"score": 90, "skills": []})
        
        combined_score = combined_assessment['combined_score']
        target_score = target_standard.get('score', 90)
        gap = target_score - combined_score
        
        if gap > 40:
            recommendations = ["Focus on foundational concepts", "Complete structured courses", "Build practice projects"]
            timeline = "6-12 months"
        elif gap > 20:
            recommendations = ["Work on intermediate projects", "Contribute to open-source", "Study system design"]
            timeline = "3-6 months"
        else:
            recommendations = ["Focus on advanced topics", "Lead technical projects", "Mentor others"]
            timeline = "1-3 months"
        
        return {
            "current_score": combined_score,
            "target_score": target_score,
            "gap": round(gap, 2),
            "gap_percentage": round((gap / target_score) * 100, 2) if target_score > 0 else 0,
            "target_level": "advanced",
            "required_skills": target_standard.get('skills', []),
            "current_strengths": self.ai_assessment.get('strengths', []),
            "areas_to_improve": self.ai_assessment.get('areas_for_improvement', []),
            "recommendations": recommendations,
            "estimated_timeline": timeline
        }

# ========== API ENDPOINTS ==========

@assessment_ns.route('/start')
class StartAssessment(Resource):
    @assessment_ns.expect(start_assessment_model)
    @assessment_ns.marshal_with(start_assessment_response)
    @assessment_ns.doc('start_assessment', description='Initialize a new skill assessment session')
    def post(self):
        """Start a new assessment session"""
        data = request.json
        
        required = ['role', 'tech_stack', 'proficiency', 'learning_goals']
        missing = [f for f in required if f not in data]
        if missing:
            api.abort(400, f"Missing fields: {', '.join(missing)}")
        
        session_id = f"session_{int(datetime.now().timestamp() * 1000)}"
        user_data = {
            "role": data['role'],
            "tech_stack": data['tech_stack'],
            "proficiency": data['proficiency'],
            "learning_goals": data['learning_goals']
        }
        
        assessment = SkillAssessmentSystem(user_data)
        initial_response = assessment.get_ai_response()
        user_sessions[session_id] = assessment
        
        return {
            "session_id": session_id,
            "message": "Assessment started successfully",
            "initial_question": initial_response['message'],
            "next_step": "conversation"
        }

@conversation_ns.route('/continue')
class ContinueConversation(Resource):
    @conversation_ns.expect(conversation_model)
    @conversation_ns.marshal_with(conversation_response)
    @conversation_ns.doc('continue_conversation', description='Continue the AI conversation')
    def post(self):
        """Continue AI conversation"""
        data = request.json
        session_id = data.get('session_id')
        user_message = data.get('message')
        
        if not session_id or not user_message:
            api.abort(400, "session_id and message required")
        
        if session_id not in user_sessions:
            api.abort(404, "Invalid session_id")
        
        assessment = user_sessions[session_id]
        response = assessment.get_ai_response(user_message)
        
        return response

@assessment_ns.route('/generate-test')
class GenerateTest(Resource):
    @assessment_ns.expect(api.model('SessionId', {'session_id': fields.String(required=True)}))
    @assessment_ns.doc('generate_test', description='Generate self-assessment test')
    def post(self):
        """Generate self-assessment test"""
        data = request.json
        session_id = data.get('session_id')
        
        if not session_id:
            api.abort(400, "session_id required")
        
        if session_id not in user_sessions:
            api.abort(404, "Invalid session_id")
        
        assessment = user_sessions[session_id]
        ai_assessment = assessment.generate_ai_assessment()
        test = assessment.generate_self_assessment_test()
        
        return {
            "questions": test,
            "ai_assessment_preview": {
                "overall_score": ai_assessment.get('overall_score'),
                "strengths": ai_assessment.get('strengths', [])
            }
        }

@assessment_ns.route('/submit-test')
class SubmitTest(Resource):
    @assessment_ns.expect(submit_test_model)
    @assessment_ns.doc('submit_test', description='Submit self-assessment responses')
    def post(self):
        """Submit self-assessment and get results"""
        data = request.json
        session_id = data.get('session_id')
        responses = data.get('responses')
        
        if not session_id or not responses:
            api.abort(400, "session_id and responses required")
        
        if session_id not in user_sessions:
            api.abort(404, "Invalid session_id")
        
        assessment = user_sessions[session_id]
        assessment.self_assessment_results = {"responses": responses}
        
        combined = assessment.calculate_combined_assessment()
        gap_analysis = assessment.generate_gap_analysis(combined)
        
        return {
            "combined_assessment": combined,
            "gap_analysis": gap_analysis,
            "status": "complete"
        }

@reports_ns.route('/get-report')
class GetReport(Resource):
    @reports_ns.doc('get_report', description='Get complete assessment report', 
                   params={'session_id': 'Session ID'})
    def get(self):
        """Get complete assessment report"""
        session_id = request.args.get('session_id')
        
        if not session_id:
            api.abort(400, "session_id required")
        
        if session_id not in user_sessions:
            api.abort(404, "Invalid session_id")
        
        assessment = user_sessions[session_id]
        combined = assessment.calculate_combined_assessment()
        gap_analysis = assessment.generate_gap_analysis(combined)
        
        return {
            "user_profile": assessment.user_data,
            "conversation_summary": {
                "total_turns": len(assessment.conversation_history) // 2,
                "sample_exchanges": assessment.conversation_history[:4]
            },
            "combined_assessment": combined,
            "gap_analysis": gap_analysis,
            "timestamp": datetime.now().isoformat()
        }

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Skill Assessment API Server Starting...")
    print("=" * 60)
    print(f"\n📍 Server: http://localhost:5000")
    print(f"📚 Swagger UI: http://localhost:5000/docs")
    print("\n📋 Endpoints:")
    print("  POST   /api/assessment/start          - Start assessment")
    print("  POST   /api/conversation/continue     - Continue conversation")
    print("  POST   /api/assessment/generate-test  - Generate test")
    print("  POST   /api/assessment/submit-test    - Submit test")
    print("  GET    /api/reports/get-report        - Get report")
    print("\n" + "=" * 60)
    print("✨ Press CTRL+C to stop")
    print("=" * 60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)