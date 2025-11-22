from typing import Dict, List, Any
from datetime import datetime
from config import config


class GapAnalysisService:
    """Service for generating gap analysis reports"""
    
    def __init__(self):
        self.skill_standards = config.SKILL_STANDARDS
        self.proficiency_levels = config.PROFICIENCY_LEVELS
    
    def generate_gap_analysis(
        self,
        ai_assessment: Dict[str, Any],
        self_assessment: Dict[str, Any],
        target_level: str,
        current_level: str
    ) -> Dict[str, Any]:
        """
        Generate comprehensive gap analysis report
        """
        
        # Process AI assessment
        ai_skills = {}
        if "skills" in ai_assessment:
            for skill_data in ai_assessment["skills"]:
                ai_skills[skill_data["skill"]] = skill_data.get("level", "Basic")
        
        # Process self-assessment
        self_skills = {}
        for skill_data in self_assessment["skills"]:
            self_skills[skill_data["skill"]] = skill_data["proficiency"]
        
        # Generate skill gaps
        skill_gaps = []
        skills_on_track = []
        skills_need_improvement = []
        critical_gaps = []
        
        for skill, levels in self.skill_standards.items():
            required_level = levels.get(target_level, "Basic")
            
            # Get assessments
            ai_level = ai_skills.get(skill, "Basic")
            self_level = self_skills.get(skill, "Basic")
            
            # Calculate combined current level (weighted average)
            ai_score = self._proficiency_to_score(ai_level)
            self_score = self._proficiency_to_score(self_level)
            combined_score = (ai_score * 0.6 + self_score * 0.4)  # AI weighted more
            current_level_str = self._score_to_proficiency(combined_score)
            
            required_score = self._proficiency_to_score(required_level)
            gap_score = required_score - combined_score
            
            # Determine priority
            if gap_score >= 2:
                priority = "High"
                critical_gaps.append(skill)
            elif gap_score >= 1:
                priority = "Medium"
                skills_need_improvement.append(skill)
            else:
                priority = "Low"
                if gap_score <= 0:
                    skills_on_track.append(skill)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                skill,
                current_level_str,
                required_level,
                gap_score
            )
            
            skill_gaps.append({
                "skill": skill,
                "current_level": current_level_str,
                "required_level": required_level,
                "gap": self._describe_gap(gap_score),
                "ai_assessed_level": ai_level,
                "self_assessed_level": self_level,
                "priority": priority,
                "recommendations": recommendations
            })
        
        # Calculate overall readiness
        total_gap = sum(
            max(0, self._proficiency_to_score(gap["required_level"]) - 
                self._proficiency_to_score(gap["current_level"]))
            for gap in skill_gaps
        )
        max_possible_gap = len(skill_gaps) * 4  # Max gap per skill is 4
        readiness = max(0, 100 - (total_gap / max_possible_gap * 100))
        
        # Determine readiness status
        if readiness >= 90:
            readiness_status = "Ready"
        elif readiness >= 70:
            readiness_status = "Almost Ready"
        elif readiness >= 50:
            readiness_status = "Needs Improvement"
        else:
            readiness_status = "Not Ready"
        
        # Calculate AI vs self-assessment alignment
        alignment = self._calculate_alignment(ai_skills, self_skills)
        
        # Generate learning path
        learning_path = self._generate_learning_path(skill_gaps, target_level)
        
        # Estimate time to target
        estimated_time = self._estimate_time_to_target(total_gap, target_level)
        
        # Identify priority areas
        priority_areas = [gap["skill"] for gap in skill_gaps if gap["priority"] == "High"]
        if not priority_areas:
            priority_areas = [gap["skill"] for gap in skill_gaps if gap["priority"] == "Medium"][:3]
        
        return {
            "session_id": "",  # Will be set by caller
            "user_name": "",  # Will be set by caller
            "current_level": current_level,
            "target_level": target_level,
            "generated_at": datetime.now().isoformat(),
            "overall_readiness": round(readiness, 2),
            "readiness_status": readiness_status,
            "skill_gaps": skill_gaps,
            "skills_on_track": skills_on_track,
            "skills_need_improvement": skills_need_improvement,
            "critical_gaps": critical_gaps,
            "learning_path": learning_path,
            "estimated_time_to_target": estimated_time,
            "priority_areas": priority_areas,
            "ai_vs_self_assessment_alignment": round(alignment, 2),
            "assessment_notes": self._generate_assessment_notes(
                readiness,
                alignment,
                critical_gaps,
                ai_assessment.get("overall_assessment", "")
            )
        }
    
    def _proficiency_to_score(self, proficiency: str) -> float:
        """Convert proficiency level to numeric score"""
        try:
            return float(self.proficiency_levels.index(proficiency))
        except (ValueError, AttributeError):
            return 0.0
    
    def _score_to_proficiency(self, score: float) -> str:
        """Convert score to proficiency level"""
        index = min(int(round(score)), len(self.proficiency_levels) - 1)
        return self.proficiency_levels[max(0, index)]
    
    def _describe_gap(self, gap_score: float) -> str:
        """Describe the gap in human-readable terms"""
        if gap_score <= 0:
            return "On track or exceeding expectations"
        elif gap_score < 1:
            return "Minor gap - almost there"
        elif gap_score < 2:
            return "Moderate gap - needs focused improvement"
        elif gap_score < 3:
            return "Significant gap - requires dedicated learning"
        else:
            return "Major gap - fundamental skills needed"
    
    def _generate_recommendations(
        self,
        skill: str,
        current: str,
        required: str,
        gap_score: float
    ) -> List[str]:
        """Generate personalized recommendations for a skill"""
        recommendations = []
        
        skill_resources = {
            "HTML": [
                "Practice semantic HTML5 elements and ARIA attributes",
                "Build accessible forms and complex layouts",
                "Study HTML best practices and SEO optimization",
                "Create projects focusing on web standards compliance"
            ],
            "CSS": [
                "Master CSS Grid and Flexbox layouts",
                "Learn CSS animations and transitions",
                "Practice responsive design patterns",
                "Explore CSS architecture (BEM, CSS Modules)",
                "Study performance optimization techniques"
            ],
            "JavaScript": [
                "Deep dive into ES6+ features and async programming",
                "Master closures, prototypes, and this context",
                "Practice algorithmic thinking and problem-solving",
                "Build projects using modern JavaScript patterns",
                "Learn testing with Jest or similar frameworks"
            ],
            "React": [
                "Master React hooks (useState, useEffect, useContext, custom hooks)",
                "Practice component composition and reusability",
                "Learn React performance optimization (memo, useMemo, useCallback)",
                "Build complex applications with routing and state management",
                "Study React best practices and design patterns"
            ],
            "Next.js": [
                "Learn SSR vs SSG and when to use each",
                "Master Next.js routing and API routes",
                "Practice image optimization and SEO",
                "Deploy Next.js applications to production",
                "Study Next.js 13+ features (App Router, Server Components)"
            ],
            "Git Basics": [
                "Practice branching strategies (Git Flow, trunk-based)",
                "Master rebasing and interactive rebasing",
                "Learn to resolve complex merge conflicts",
                "Practice code review workflows",
                "Study advanced Git commands and workflows"
            ],
            "Debugging Skills": [
                "Master browser DevTools (Console, Network, Performance)",
                "Practice debugging React components and state",
                "Learn source map debugging",
                "Study common bug patterns and prevention",
                "Use debugging tools like React DevTools"
            ],
            "API Integration": [
                "Practice RESTful API design and consumption",
                "Master error handling and loading states",
                "Learn authentication patterns (JWT, OAuth)",
                "Study API rate limiting and caching strategies",
                "Build projects with complex API integrations"
            ],
            "State Management (Redux/Zustand)": [
                "Learn Redux Toolkit for modern Redux development",
                "Practice Zustand for lightweight state management",
                "Master async actions and middleware",
                "Study state management patterns and best practices",
                "Build applications requiring complex state logic"
            ],
            "Performance Optimization": [
                "Learn to use Chrome Lighthouse and Performance tab",
                "Master code splitting and lazy loading",
                "Practice React.memo and useMemo optimization",
                "Study bundle size optimization techniques",
                "Learn about Web Vitals and Core Web Vitals"
            ]
        }
        
        skill_recs = skill_resources.get(skill, [
            f"Study {skill} fundamentals",
            f"Practice {skill} through projects",
            f"Take online courses on {skill}",
            f"Join communities focused on {skill}"
        ])
        
        # Select recommendations based on gap
        if gap_score <= 0:
            recommendations.append(f"Continue practicing {skill} to maintain expertise")
        elif gap_score < 1.5:
            recommendations.extend(skill_recs[:2])
        elif gap_score < 2.5:
            recommendations.extend(skill_recs[:3])
        else:
            recommendations.extend(skill_recs[:4])
        
        return recommendations
    
    def _calculate_alignment(self, ai_skills: Dict, self_skills: Dict) -> float:
        """Calculate how aligned AI and self-assessments are"""
        if not ai_skills or not self_skills:
            return 50.0
        
        total_diff = 0
        count = 0
        
        for skill in ai_skills.keys():
            if skill in self_skills:
                ai_score = self._proficiency_to_score(ai_skills[skill])
                self_score = self._proficiency_to_score(self_skills[skill])
                diff = abs(ai_score - self_score)
                total_diff += diff
                count += 1
        
        if count == 0:
            return 50.0
        
        avg_diff = total_diff / count
        max_diff = 4.0  # Maximum difference between None and Expert
        
        # Convert to percentage (0 diff = 100% alignment)
        alignment = 100 - (avg_diff / max_diff * 100)
        return max(0, min(100, alignment))
    
    def _generate_learning_path(self, skill_gaps: List[Dict], target_level: str) -> List[Dict]:
        """Generate a prioritized learning path"""
        learning_path = []
        
        # Sort by priority and gap
        high_priority = [g for g in skill_gaps if g["priority"] == "High"]
        medium_priority = [g for g in skill_gaps if g["priority"] == "Medium"]
        
        phase = 1
        
        # Phase 1: Critical gaps
        if high_priority:
            for gap in high_priority[:3]:  # Top 3 critical
                learning_path.append({
                    "phase": f"Phase {phase}",
                    "skill": gap["skill"],
                    "focus": gap["recommendations"][0] if gap["recommendations"] else f"Learn {gap['skill']}",
                    "duration": "2-4 weeks",
                    "priority": "High"
                })
                phase += 1
        
        # Phase 2: Medium priority
        if medium_priority:
            for gap in medium_priority[:3]:  # Top 3 medium
                learning_path.append({
                    "phase": f"Phase {phase}",
                    "skill": gap["skill"],
                    "focus": gap["recommendations"][0] if gap["recommendations"] else f"Improve {gap['skill']}",
                    "duration": "1-2 weeks",
                    "priority": "Medium"
                })
                phase += 1
        
        # Phase 3: Polish and practice
        learning_path.append({
            "phase": f"Phase {phase}",
            "skill": "Integration & Practice",
            "focus": "Build comprehensive projects combining all skills",
            "duration": "4-6 weeks",
            "priority": "Essential"
        })
        
        return learning_path
    
    def _estimate_time_to_target(self, total_gap: float, target_level: str) -> str:
        """Estimate time needed to reach target level"""
        # Rough estimation: each gap point = 2-3 weeks of focused learning
        weeks = total_gap * 2.5
        
        if weeks < 4:
            return "1-2 months with focused effort"
        elif weeks < 12:
            return "3-6 months with consistent practice"
        elif weeks < 24:
            return "6-12 months with dedicated learning"
        else:
            return "12-18 months with structured learning path"
    
    def _generate_assessment_notes(
        self,
        readiness: float,
        alignment: float,
        critical_gaps: List[str],
        ai_notes: str
    ) -> str:
        """Generate comprehensive assessment notes"""
        notes = []
        
        # Readiness feedback
        if readiness >= 90:
            notes.append("Excellent! You're ready for the target level.")
        elif readiness >= 70:
            notes.append("You're close to the target level. Focus on the identified gaps.")
        elif readiness >= 50:
            notes.append("You have a solid foundation but need significant improvement in several areas.")
        else:
            notes.append("Consider focusing on foundational skills before targeting this level.")
        
        # Alignment feedback
        if alignment >= 80:
            notes.append("Your self-assessment aligns well with the AI assessment, showing good self-awareness.")
        elif alignment >= 60:
            notes.append("There's moderate alignment between assessments. Review the detailed gaps carefully.")
        else:
            notes.append("Significant discrepancy between self and AI assessment. Consider seeking mentor feedback.")
        
        # Critical gaps
        if critical_gaps:
            notes.append(f"Critical areas needing attention: {', '.join(critical_gaps[:3])}.")
        else:
            notes.append("No critical gaps identified. Focus on continuous improvement.")
        
        # Add AI insights
        if ai_notes:
            notes.append(f"AI Insights: {ai_notes}")
        
        return " ".join(notes)

