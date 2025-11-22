from typing import Dict, List, Any, Optional
from openai import OpenAI
import json
from config import config


class ContentGenerationService:
    """Service for generating AI-powered learning content"""
    
    def __init__(self):
        # Initialize OpenAI client with optional custom base URL
        client_kwargs = {"api_key": config.OPENAI_API_KEY}
        if config.OPENAI_BASE_URL:
            client_kwargs["base_url"] = config.OPENAI_BASE_URL
        
        self.client = OpenAI(**client_kwargs)
        self.model = config.OPENAI_MODEL
        self.temperature = 0.7
    
    async def generate_lesson(
        self,
        skill: str,
        milestone_number: int,
        current_level: str,
        target_level: str,
        role: str
    ) -> Dict[str, Any]:
        """
        Generate a structured lesson with introduction, core concepts, examples, best practices
        """
        system_prompt = f"""You are an expert technical educator specializing in {role} development.
Create comprehensive, structured lesson content that is clear, practical, and engaging.
Focus on {skill} at the {current_level} to {target_level} level transition."""

        user_prompt = f"""Generate a structured lesson for {skill} - Milestone {milestone_number}.

The lesson should include:
1. Introduction (2-3 sentences explaining what will be covered)
2. Core Concepts (3-5 key concepts with brief explanations)
3. Examples (2-3 practical code examples or scenarios)
4. Best Practices (3-4 important best practices)
5. Common Pitfalls (2-3 things to avoid)

Target audience: {role} transitioning from {current_level} to {target_level} level.

Format the response as JSON with this structure:
{{
    "introduction": "string",
    "core_concepts": [
        {{"title": "string", "description": "string"}}
    ],
    "examples": [
        {{"title": "string", "code": "string", "explanation": "string"}}
    ],
    "best_practices": ["string"],
    "common_pitfalls": ["string"]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Try to parse as JSON
            try:
                lesson_data = json.loads(content)
            except json.JSONDecodeError:
                # Fallback structure if JSON parsing fails
                lesson_data = {
                    "introduction": content[:200] + "...",
                    "core_concepts": [
                        {"title": "Concept 1", "description": "Key concept explanation"},
                        {"title": "Concept 2", "description": "Another important concept"}
                    ],
                    "examples": [
                        {"title": "Example 1", "code": "# Example code", "explanation": "Explanation"}
                    ],
                    "best_practices": ["Best practice 1", "Best practice 2"],
                    "common_pitfalls": ["Pitfall 1", "Pitfall 2"]
                }
            
            return {
                "type": "lesson",
                "skill": skill,
                "milestone_number": milestone_number,
                "estimated_time": "15 minutes",
                "xp": 50,
                "content": lesson_data
            }
        except Exception as e:
            print(f"Error generating lesson: {e}")
            return self._get_fallback_lesson(skill, milestone_number)
    
    async def generate_quiz(
        self,
        skill: str,
        milestone_number: int,
        current_level: str,
        target_level: str,
        role: str
    ) -> Dict[str, Any]:
        """
        Generate a quiz with multiple choice, scenario-based, and true/false questions
        Passing score: 70%
        """
        system_prompt = f"""You are an expert technical educator creating assessment quizzes for {role} developers.
Create questions that test understanding of {skill} at the {current_level} to {target_level} level."""

        user_prompt = f"""Generate a quiz for {skill} - Milestone {milestone_number}.

Create 8-10 questions with a mix of:
- Multiple choice questions (4 options each)
- Scenario-based questions
- True/False questions

Target audience: {role} transitioning from {current_level} to {target_level} level.

Format the response as JSON with this structure:
{{
    "questions": [
        {{
            "id": "q1",
            "type": "multiple_choice" | "scenario" | "true_false",
            "question": "string",
            "options": ["option1", "option2", "option3", "option4"] (for multiple choice),
            "correct_answer": "string",
            "explanation": "string"
        }}
    ],
    "passing_score": 70
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,  # Lower temperature for more consistent questions
                max_tokens=2500
            )
            
            content = response.choices[0].message.content
            
            try:
                quiz_data = json.loads(content)
                # Ensure all questions have IDs and required fields
                if "questions" in quiz_data and isinstance(quiz_data["questions"], list):
                    for idx, question in enumerate(quiz_data["questions"]):
                        # Ensure ID exists
                        if "id" not in question or not question.get("id"):
                            question["id"] = f"q{idx + 1}"
                        # Ensure type exists
                        if "type" not in question:
                            question["type"] = "multiple_choice"
                        # Ensure options exist for multiple choice and scenario
                        if question.get("type") in ["multiple_choice", "scenario"]:
                            if "options" not in question or not question.get("options"):
                                question["options"] = ["Option A", "Option B", "Option C", "Option D"]
                        # Ensure options exist for true/false
                        elif question.get("type") == "true_false":
                            if "options" not in question or not question.get("options"):
                                question["options"] = ["True", "False"]
                        # Ensure correct_answer exists
                        if "correct_answer" not in question or not question.get("correct_answer"):
                            if question.get("options"):
                                question["correct_answer"] = question["options"][0]
                            else:
                                question["correct_answer"] = "Option A"
                        # Ensure explanation exists
                        if "explanation" not in question or not question.get("explanation"):
                            question["explanation"] = "This is the correct answer."
                    # Ensure we have at least 8 questions
                    if len(quiz_data["questions"]) < 8:
                        # Add fallback questions to reach 8
                        fallback_quiz = self._get_fallback_quiz()
                        existing_ids = {q.get("id") for q in quiz_data["questions"]}
                        for fallback_q in fallback_quiz["questions"]:
                            if fallback_q["id"] not in existing_ids and len(quiz_data["questions"]) < 10:
                                quiz_data["questions"].append(fallback_q)
                                existing_ids.add(fallback_q["id"])
                else:
                    quiz_data = self._get_fallback_quiz()
            except json.JSONDecodeError:
                quiz_data = self._get_fallback_quiz()
            
            return {
                "type": "quiz",
                "skill": skill,
                "milestone_number": milestone_number,
                "estimated_time": "10 minutes",
                "xp": 30,
                "passing_score": quiz_data.get("passing_score", 70),
                "content": quiz_data
            }
        except Exception as e:
            print(f"Error generating quiz: {e}")
            return self._get_fallback_quiz_response(skill, milestone_number)
    
    async def generate_coding_challenge(
        self,
        skill: str,
        milestone_number: int,
        current_level: str,
        target_level: str,
        role: str
    ) -> Dict[str, Any]:
        """
        Generate a coding challenge with problem statement, requirements, and hints
        """
        system_prompt = f"""You are an expert technical educator creating coding challenges for {role} developers.
Create practical, hands-on challenges that reinforce {skill} concepts."""

        user_prompt = f"""Generate a coding challenge for {skill} - Milestone {milestone_number}.

The challenge should include:
1. Problem Statement (clear description of what needs to be built/solved)
2. Requirements (specific functional requirements)
3. Constraints (any limitations or constraints)
4. Hints (2-3 progressive hints)
5. Expected Output (description of expected result)

Target audience: {role} transitioning from {current_level} to {target_level} level.

Format the response as JSON with this structure:
{{
    "problem_statement": "string",
    "requirements": ["requirement1", "requirement2"],
    "constraints": ["constraint1", "constraint2"],
    "hints": [
        {{"level": 1, "hint": "string"}},
        {{"level": 2, "hint": "string"}}
    ],
    "expected_output": "string",
    "starter_code": "string (optional)"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            try:
                challenge_data = json.loads(content)
            except json.JSONDecodeError:
                challenge_data = self._get_fallback_challenge()
            
            return {
                "type": "coding_challenge",
                "skill": skill,
                "milestone_number": milestone_number,
                "estimated_time": "30 minutes",
                "xp": 100,
                "content": challenge_data
            }
        except Exception as e:
            print(f"Error generating coding challenge: {e}")
            return self._get_fallback_challenge_response(skill, milestone_number)
    
    async def generate_flashcards(
        self,
        skill: str,
        milestone_number: int,
        current_level: str,
        target_level: str,
        role: str
    ) -> Dict[str, Any]:
        """
        Generate 10 question-answer flashcard pairs
        """
        system_prompt = f"""You are an expert technical educator creating flashcards for {role} developers.
Create concise question-answer pairs that help reinforce {skill} concepts."""

        user_prompt = f"""Generate 10 flashcards for {skill} - Milestone {milestone_number}.

Each flashcard should have:
- A clear, concise question
- A brief, accurate answer

Target audience: {role} transitioning from {current_level} to {target_level} level.

Format the response as JSON with this structure:
{{
    "cards": [
        {{
            "id": "card1",
            "question": "string",
            "answer": "string"
        }}
    ]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            try:
                flashcard_data = json.loads(content)
            except json.JSONDecodeError:
                flashcard_data = self._get_fallback_flashcards()
            
            return {
                "type": "flashcards",
                "skill": skill,
                "milestone_number": milestone_number,
                "estimated_time": "5 minutes",
                "xp": 20,
                "content": flashcard_data
            }
        except Exception as e:
            print(f"Error generating flashcards: {e}")
            return self._get_fallback_flashcards_response(skill, milestone_number)
    
    async def generate_summary(
        self,
        skill: str,
        milestone_number: int,
        current_level: str,
        target_level: str,
        role: str
    ) -> Dict[str, Any]:
        """
        Generate a summary with key takeaways, skills developed, and next steps
        """
        system_prompt = f"""You are an expert technical educator creating learning summaries for {role} developers.
Create concise summaries that reinforce learning and guide next steps."""

        user_prompt = f"""Generate a summary for {skill} - Milestone {milestone_number}.

The summary should include:
1. Key Takeaways (3-5 main points learned)
2. Skills Developed (list of skills/concepts mastered)
3. Next Steps (what to learn or practice next)

Target audience: {role} transitioning from {current_level} to {target_level} level.

Format the response as JSON with this structure:
{{
    "key_takeaways": ["takeaway1", "takeaway2"],
    "skills_developed": ["skill1", "skill2"],
    "next_steps": ["step1", "step2"]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            
            try:
                summary_data = json.loads(content)
            except json.JSONDecodeError:
                summary_data = self._get_fallback_summary()
            
            return {
                "type": "summary",
                "skill": skill,
                "milestone_number": milestone_number,
                "estimated_time": "5 minutes",
                "xp": 25,
                "content": summary_data
            }
        except Exception as e:
            print(f"Error generating summary: {e}")
            return self._get_fallback_summary_response(skill, milestone_number)
    
    # Fallback methods for when AI generation fails
    def _get_fallback_lesson(self, skill: str, milestone_number: int) -> Dict[str, Any]:
        return {
            "type": "lesson",
            "skill": skill,
            "milestone_number": milestone_number,
            "estimated_time": "15 minutes",
            "xp": 50,
            "content": {
                "introduction": f"This lesson covers key concepts of {skill} for milestone {milestone_number}.",
                "core_concepts": [
                    {"title": "Core Concept", "description": "Important concept to understand"}
                ],
                "examples": [
                    {"title": "Example", "code": "# Code example", "explanation": "Explanation"}
                ],
                "best_practices": ["Follow best practices", "Write clean code"],
                "common_pitfalls": ["Avoid common mistakes", "Watch out for errors"]
            }
        }
    
    def _get_fallback_quiz(self) -> Dict[str, Any]:
        """Generate a fallback quiz with 8-10 questions when AI generation fails"""
        return {
            "questions": [
                {
                    "id": "q1",
                    "type": "multiple_choice",
                    "question": "What is a key concept in this skill?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option A",
                    "explanation": "This is the correct answer because it represents the fundamental concept."
                },
                {
                    "id": "q2",
                    "type": "multiple_choice",
                    "question": "Which approach is considered best practice?",
                    "options": ["Approach 1", "Approach 2", "Approach 3", "Approach 4"],
                    "correct_answer": "Approach 2",
                    "explanation": "Approach 2 follows industry best practices and standards."
                },
                {
                    "id": "q3",
                    "type": "true_false",
                    "question": "This statement is true or false?",
                    "options": ["True", "False"],
                    "correct_answer": "True",
                    "explanation": "This statement is correct based on the fundamentals."
                },
                {
                    "id": "q4",
                    "type": "scenario",
                    "question": "In a scenario where you need to implement X, what would you do?",
                    "options": ["Solution A", "Solution B", "Solution C", "Solution D"],
                    "correct_answer": "Solution C",
                    "explanation": "Solution C is the most appropriate for this scenario."
                },
                {
                    "id": "q5",
                    "type": "multiple_choice",
                    "question": "What is the primary purpose of this feature?",
                    "options": ["Purpose A", "Purpose B", "Purpose C", "Purpose D"],
                    "correct_answer": "Purpose B",
                    "explanation": "Purpose B accurately describes the primary function."
                },
                {
                    "id": "q6",
                    "type": "multiple_choice",
                    "question": "Which method is most efficient?",
                    "options": ["Method 1", "Method 2", "Method 3", "Method 4"],
                    "correct_answer": "Method 3",
                    "explanation": "Method 3 provides the best performance and efficiency."
                },
                {
                    "id": "q7",
                    "type": "true_false",
                    "question": "This technique is recommended for production use.",
                    "options": ["True", "False"],
                    "correct_answer": "True",
                    "explanation": "This technique is widely recommended and tested in production."
                },
                {
                    "id": "q8",
                    "type": "scenario",
                    "question": "When facing this challenge, what is the recommended approach?",
                    "options": ["Approach A", "Approach B", "Approach C", "Approach D"],
                    "correct_answer": "Approach B",
                    "explanation": "Approach B is the recommended solution for this challenge."
                }
            ],
            "passing_score": 70
        }
    
    def _get_fallback_quiz_response(self, skill: str, milestone_number: int) -> Dict[str, Any]:
        return {
            "type": "quiz",
            "skill": skill,
            "milestone_number": milestone_number,
            "estimated_time": "10 minutes",
            "xp": 30,
            "passing_score": 70,
            "content": self._get_fallback_quiz()
        }
    
    def _get_fallback_challenge(self) -> Dict[str, Any]:
        return {
            "problem_statement": "Implement a solution to demonstrate understanding.",
            "requirements": ["Requirement 1", "Requirement 2"],
            "constraints": ["Constraint 1"],
            "hints": [
                {"level": 1, "hint": "First hint"},
                {"level": 2, "hint": "Second hint"}
            ],
            "expected_output": "Expected result description",
            "starter_code": "# Starter code here"
        }
    
    def _get_fallback_challenge_response(self, skill: str, milestone_number: int) -> Dict[str, Any]:
        return {
            "type": "coding_challenge",
            "skill": skill,
            "milestone_number": milestone_number,
            "estimated_time": "30 minutes",
            "xp": 100,
            "content": self._get_fallback_challenge()
        }
    
    def _get_fallback_flashcards(self) -> Dict[str, Any]:
        return {
            "cards": [
                {"id": f"card{i}", "question": f"Question {i}?", "answer": f"Answer {i}"}
                for i in range(1, 11)
            ]
        }
    
    def _get_fallback_flashcards_response(self, skill: str, milestone_number: int) -> Dict[str, Any]:
        return {
            "type": "flashcards",
            "skill": skill,
            "milestone_number": milestone_number,
            "estimated_time": "5 minutes",
            "xp": 20,
            "content": self._get_fallback_flashcards()
        }
    
    def _get_fallback_summary(self) -> Dict[str, Any]:
        return {
            "key_takeaways": ["Takeaway 1", "Takeaway 2", "Takeaway 3"],
            "skills_developed": ["Skill 1", "Skill 2"],
            "next_steps": ["Next step 1", "Next step 2"]
        }
    
    def _get_fallback_summary_response(self, skill: str, milestone_number: int) -> Dict[str, Any]:
        return {
            "type": "summary",
            "skill": skill,
            "milestone_number": milestone_number,
            "estimated_time": "5 minutes",
            "xp": 25,
            "content": self._get_fallback_summary()
        }

