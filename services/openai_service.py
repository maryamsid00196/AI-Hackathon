from openai import OpenAI
from typing import Dict, List, Any
import json
from config import config


class OpenAIService:
    """Service for OpenAI API interactions"""
    
    def __init__(self):
        # Initialize OpenAI client with optional custom base URL
        client_kwargs = {"api_key": config.OPENAI_API_KEY}
        if config.OPENAI_BASE_URL:
            client_kwargs["base_url"] = config.OPENAI_BASE_URL
        
        self.client = OpenAI(**client_kwargs)
        self.model = config.OPENAI_MODEL
        self.temperature = config.CONVERSATION_TEMPERATURE
    
    async def generate_initial_conversation(self, user_data: Any) -> str:
        """
        Generate initial conversation message based on user data
        """
        system_prompt = """You are an expert technical interviewer and skill assessor specializing in frontend development.
Your goal is to have a natural conversation with the candidate to understand their:
1. Project experience
2. Technical skills depth
3. Problem-solving approach
4. Team collaboration experience
5. Learning mindset

Ask thoughtful, open-ended questions. Be conversational and encouraging.
Focus on: HTML, CSS, JavaScript, React, Next.js, Git, Debugging, API Integration, State Management, and Performance Optimization.

Keep responses concise and focused."""

        user_prompt = f"""Start a conversation with {user_data.name}.
They currently consider themselves at {user_data.current_level} level and want to reach {user_data.target_level} level.
{f"They have {user_data.years_of_experience} years of experience." if user_data.years_of_experience else ""}
{f"Primary technologies: {', '.join(user_data.primary_technologies)}" if user_data.primary_technologies else ""}

Start with a warm greeting and ask about their most recent or favorite project."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=300
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            # Fallback message
            return f"""Hi {user_data.name}! 👋

I'm excited to learn more about your development experience and help assess your skills for reaching {user_data.target_level} level.

Let's start with your recent work - can you tell me about a project you've worked on recently that you're proud of? What technologies did you use, and what was your role in the project?"""
    
    async def continue_conversation(self, conversation_history: List[Dict], user_data: Dict) -> Dict[str, Any]:
        """
        Continue the conversation and determine if we have enough information
        """
        system_prompt = """You are an expert technical interviewer conducting a skill assessment interview.

Based on the conversation so far, ask follow-up questions to understand:
- Technical depth in frontend technologies (React, Next.js, JavaScript, CSS, HTML)
- Experience with Git, debugging, API integration, state management, performance optimization
- Problem-solving approach
- Team collaboration and leadership (if applicable)

After 3 meaningful exchanges, if you have enough information to assess the candidate's skills, 
respond with a JSON object with "conversation_complete": true.

Format your response as:
{
    "message": "your conversational response",
    "conversation_complete": false,
    "next_step": "continue_conversation"
}

When you have enough information (after 3-4 meaningful exchanges), end with a message like:
"Thank you for sharing your experience in handling [topic]. It's valuable to know that you [summary]. Given your detailed explanation, I can see that you have a solid understanding of [skills]. Let's now move to the next step for a self-assessment of your skills. Thank you for sharing your insights!"

Then respond with:
{
    "message": "Thank you for sharing your experience... [similar message as above]",
    "conversation_complete": true,
    "next_step": "self_assessment"
}"""

        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in conversation_history[-10:]:  # Last 10 messages
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=400
            )
            
            content = response.choices[0].message.content
            
            # Try to parse as JSON
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                # If not JSON, treat as regular message
                # Check if we've had enough turns (at least 6 messages = 3 exchanges)
                user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]
                conversation_complete = len(user_messages) >= 3
                
                if conversation_complete:
                    # Generate completion message
                    completion_message = """Thank you for sharing your experience in handling state management and frontend technologies. It's valuable to know that you have structured your approach effectively to ensure efficient data flow and updates throughout the application.

Given your detailed explanation of how you managed state in your project, I can see that you have a solid understanding of frontend technologies and best practices.

Let's now move to the next step for a self-assessment of your skills. Thank you for sharing your insights!"""
                    
                    return {
                        "message": completion_message,
                        "conversation_complete": True,
                        "next_step": "self_assessment"
                    }
                
                return {
                    "message": content,
                    "conversation_complete": False,
                    "next_step": "continue_conversation"
                }
        
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return {
                "message": "I appreciate you sharing that. Could you tell me more about the challenges you faced?",
                "conversation_complete": False,
                "next_step": "continue_conversation"
            }
    
    async def generate_assessment(self, conversation_history: List[Dict], user_data: Dict) -> Dict[str, Any]:
        """
        Generate AI assessment based on conversation
        """
        system_prompt = f"""Based on the conversation, assess the candidate's skill levels in these areas:
{json.dumps(list(config.SKILL_STANDARDS.keys()), indent=2)}

Rate each skill as: None, Basic, Intermediate, Advanced, or Expert.

Return a JSON object with this structure:
{{
    "skills": [
        {{"skill": "HTML", "level": "Intermediate", "reasoning": "brief explanation"}},
        ...
    ],
    "overall_assessment": "summary of candidate's strengths and areas for growth",
    "readiness_for_target": "assessment of readiness for {user_data.get('target_level', 'target')} level"
}}"""

        messages = [{"role": "system", "content": system_prompt}]
        messages.append({
            "role": "user",
            "content": f"Assess this conversation:\n\n{json.dumps(conversation_history, indent=2)}"
        })
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Lower temperature for more consistent assessment
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            try:
                assessment = json.loads(content)
                return assessment
            except json.JSONDecodeError:
                # Create a default assessment structure
                return {
                    "skills": [
                        {"skill": skill, "level": "Intermediate", "reasoning": "Based on conversation"}
                        for skill in config.SKILL_STANDARDS.keys()
                    ],
                    "overall_assessment": content,
                    "readiness_for_target": "Needs more information"
                }
        
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            # Return default assessment
            return {
                "skills": [
                    {"skill": skill, "level": "Basic", "reasoning": "Default assessment"}
                    for skill in config.SKILL_STANDARDS.keys()
                ],
                "overall_assessment": "Assessment based on limited conversation data",
                "readiness_for_target": "Requires further evaluation"
            }

