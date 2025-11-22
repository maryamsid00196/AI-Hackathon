from typing import Dict, List, Any
from datetime import datetime, timedelta
from config import config


class LearningPathService:
    """Service for generating personalized learning paths"""
    
    def __init__(self):
        self.skill_standards = config.SKILL_STANDARDS
        self.proficiency_levels = config.PROFICIENCY_LEVELS
    
    def generate_learning_paths(
        self,
        role: str,
        skill_ratings: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Generate personalized learning paths based on skill ratings
        
        Args:
            role: User's role (e.g., "Frontend Engineer")
            skill_ratings: List of skill ratings with skill_name and current_level
        
        Returns:
            Dictionary containing learning paths for each skill
        """
        learning_paths = []
        total_xp = 0
        
        for skill_rating in skill_ratings:
            skill_name = skill_rating.get("skill_name")
            current_level = skill_rating.get("current_level")
            
            # Skip Expert-level skills (no path needed)
            if current_level == "Expert":
                continue
            
            # Determine target level (next level up)
            target_level = self._get_next_level(current_level)
            
            if not target_level:
                continue  # Already at highest level
            
            # Generate milestones for this skill
            milestones = self._generate_milestones(
                skill_name=skill_name,
                current_level=current_level,
                target_level=target_level,
                role=role
            )
            
            if milestones:
                path_xp = sum(m.get("xp", 0) for m in milestones)
                total_xp += path_xp
                
                learning_paths.append({
                    "skill": skill_name,
                    "current_level": current_level,
                    "target_level": target_level,
                    "milestones": milestones,
                    "total_xp": path_xp,
                    "estimated_weeks": len(milestones) * 2,  # 2 weeks per milestone
                    "progress": 0  # Will be tracked by frontend
                })
        
        return {
            "role": role,
            "generated_at": datetime.now().isoformat(),
            "learning_paths": learning_paths,
            "total_xp_available": total_xp,
            "total_skills": len(learning_paths),
            "estimated_total_weeks": max([p.get("estimated_weeks", 8) for p in learning_paths], default=8)
        }
    
    def _get_next_level(self, current_level: str) -> str:
        """Get the next proficiency level"""
        level_order = ["None", "Basic", "Intermediate", "Advanced", "Expert"]
        try:
            current_index = level_order.index(current_level)
            if current_index < len(level_order) - 1:
                return level_order[current_index + 1]
        except ValueError:
            pass
        return None
    
    def _generate_milestones(
        self,
        skill_name: str,
        current_level: str,
        target_level: str,
        role: str
    ) -> List[Dict[str, Any]]:
        """
        Generate milestones for a skill progression
        
        Args:
            skill_name: Name of the skill
            current_level: Current proficiency level
            target_level: Target proficiency level
            role: User's role
        
        Returns:
            List of milestone dictionaries
        """
        level_order = ["None", "Basic", "Intermediate", "Advanced", "Expert"]
        
        try:
            current_index = level_order.index(current_level)
            target_index = level_order.index(target_level)
            level_jump = target_index - current_index
        except ValueError:
            level_jump = 1
        
        # Determine number of milestones based on level jump
        # Small jump (1 level) = 3 milestones, Large jump (2+ levels) = 4 milestones
        num_milestones = 4 if level_jump >= 2 else 3
        
        milestones = []
        start_date = datetime.now()
        
        for i in range(num_milestones):
            milestone_num = i + 1
            week_start = i * 2 + 1
            week_end = (i + 1) * 2
            
            # Generate milestone content
            milestone = {
                "milestone_number": milestone_num,
                "title": self._generate_milestone_title(skill_name, milestone_num, current_level, target_level),
                "description": self._generate_milestone_description(skill_name, milestone_num, num_milestones),
                "weeks": f"Week {week_start}-{week_end}",
                "start_date": (start_date + timedelta(weeks=i*2)).isoformat(),
                "end_date": (start_date + timedelta(weeks=(i+1)*2)).isoformat(),
                "xp": 250 * milestone_num,  # Increasing XP per milestone
                "parts": self._generate_milestone_parts(skill_name, milestone_num, role),
                "mentor_checkpoint": milestone_num == num_milestones,  # Last milestone has mentor checkpoint
                "jira_integration": self._generate_jira_challenge(skill_name, milestone_num, role),
                "external_resources": self._generate_external_resources(skill_name, milestone_num)
            }
            
            milestones.append(milestone)
        
        return milestones
    
    def _generate_milestone_title(
        self,
        skill_name: str,
        milestone_num: int,
        current_level: str,
        target_level: str
    ) -> str:
        """Generate a title for a milestone"""
        titles = {
            1: f"Foundations of {skill_name}",
            2: f"Building {skill_name} Skills",
            3: f"Advanced {skill_name} Concepts",
            4: f"Mastering {skill_name}"
        }
        return titles.get(milestone_num, f"Milestone {milestone_num}: {skill_name}")
    
    def _generate_milestone_description(
        self,
        skill_name: str,
        milestone_num: int,
        total_milestones: int
    ) -> str:
        """Generate a description for a milestone"""
        descriptions = {
            1: f"Establish a solid foundation in {skill_name} with core concepts and fundamentals.",
            2: f"Build upon your {skill_name} knowledge with practical applications and real-world scenarios.",
            3: f"Explore advanced {skill_name} techniques and patterns to enhance your expertise.",
            4: f"Master {skill_name} by tackling complex challenges and implementing best practices."
        }
        return descriptions.get(milestone_num, f"Continue your journey in {skill_name}.")
    
    def _generate_milestone_parts(
        self,
        skill_name: str,
        milestone_num: int,
        role: str
    ) -> List[Dict[str, Any]]:
        """Generate parts (lesson, quiz, challenge, practice) for a milestone"""
        parts = []
        
        # Lesson
        parts.append({
            "type": "lesson",
            "title": f"{skill_name} Lesson {milestone_num}",
            "description": f"Interactive lesson covering key concepts for milestone {milestone_num}",
            "duration": "45-60 minutes",
            "xp": 50,
            "completed": False
        })
        
        # Quiz
        parts.append({
            "type": "quiz",
            "title": f"{skill_name} Knowledge Check {milestone_num}",
            "description": f"Test your understanding with {milestone_num * 5} questions",
            "duration": "15-20 minutes",
            "xp": 30,
            "completed": False
        })
        
        # Challenge
        parts.append({
            "type": "challenge",
            "title": f"{skill_name} Challenge {milestone_num}",
            "description": f"Hands-on coding challenge to apply what you've learned",
            "duration": "1-2 hours",
            "xp": 75,
            "completed": False
        })
        
        # Practice
        parts.append({
            "type": "practice",
            "title": f"{skill_name} Practice Session {milestone_num}",
            "description": f"Guided practice exercises to reinforce concepts",
            "duration": "30-45 minutes",
            "xp": 25,
            "completed": False
        })
        
        return parts
    
    def _generate_jira_challenge(
        self,
        skill_name: str,
        milestone_num: int,
        role: str
    ) -> Dict[str, Any]:
        """Generate a Jira integration challenge"""
        return {
            "enabled": True,
            "description": f"Real-world project challenge: Implement {skill_name} feature in your current project",
            "jira_ticket_template": f"Create a ticket for: {skill_name} milestone {milestone_num} implementation",
            "xp_bonus": 50
        }
    
    def _generate_external_resources(
        self,
        skill_name: str,
        milestone_num: int
    ) -> List[Dict[str, str]]:
        """Generate external resource recommendations"""
        resources = [
            {
                "title": f"{skill_name} Official Documentation",
                "url": f"https://example.com/{skill_name.lower()}/docs",
                "type": "documentation"
            },
            {
                "title": f"{skill_name} Best Practices Guide",
                "url": f"https://example.com/{skill_name.lower()}/best-practices",
                "type": "guide"
            }
        ]
        
        if milestone_num >= 3:
            resources.append({
                "title": f"Advanced {skill_name} Tutorial",
                "url": f"https://example.com/{skill_name.lower()}/advanced",
                "type": "tutorial"
            })
        
        return resources

