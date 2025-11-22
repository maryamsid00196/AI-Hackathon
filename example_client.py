"""
Example client demonstrating how to use the Skill Assessment API
"""
import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"


def print_response(title: str, response: dict):
    """Pretty print API responses"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(json.dumps(response, indent=2))


def main():
    """Example workflow using the API"""
    
    print("🚀 Starting Skill Assessment API Demo\n")
    
    # Step 1: Start a new session
    print("Step 1: Creating new assessment session...")
    initial_data = {
        "name": "Jane Developer",
        "email": "jane@example.com",
        "current_level": "Junior",
        "target_level": "Senior",
        "years_of_experience": 2.0,
        "primary_technologies": ["React", "JavaScript", "CSS", "HTML"],
        "additional_info": "Working on e-commerce projects, want to advance to senior role"
    }
    
    response = requests.post(f"{BASE_URL}/api/session/start", json=initial_data)
    session_data = response.json()
    print_response("Session Started", session_data)
    
    session_id = session_data["session_id"]
    
    # Step 2: Have a conversation with AI
    print("\nStep 2: Having conversation with AI...")
    
    conversation_messages = [
        "I recently worked on a React e-commerce application where I built the product catalog and shopping cart features. I used Redux for state management and integrated with a REST API.",
        "Yes, I've worked with React hooks extensively. I'm comfortable with useState, useEffect, and useContext. I've also created custom hooks for data fetching.",
        "For debugging, I mainly use Chrome DevTools. I use console.log, breakpoints, and the React DevTools extension. I also use the Network tab to debug API calls.",
        "I haven't worked much with Next.js yet, but I've built several React SPAs. I'm familiar with client-side routing using React Router."
    ]
    
    for i, message in enumerate(conversation_messages, 1):
        print(f"\n  👤 User Message {i}: {message[:80]}...")
        response = requests.post(
            f"{BASE_URL}/api/conversation/{session_id}",
            json={"message": message}
        )
        conv_response = response.json()
        print(f"  🤖 AI Response: {conv_response['message'][:100]}...")
        
        if conv_response.get("conversation_complete"):
            print("\n  ✅ Conversation completed! Moving to self-assessment.")
            break
        
        time.sleep(1)  # Small delay for readability
    
    # Step 3: Get conversation history
    print("\nStep 3: Retrieving conversation history...")
    response = requests.get(f"{BASE_URL}/api/conversation/{session_id}/history")
    history = response.json()
    print(f"  Total messages: {len(history['history'])}")
    
    # Step 4: Get self-assessment test
    print("\nStep 4: Getting self-assessment test...")
    response = requests.get(f"{BASE_URL}/api/assessment/test/{session_id}")
    test_data = response.json()
    print(f"  Total questions: {test_data['test']['total_questions']}")
    print(f"  Skills covered: {', '.join(test_data['test']['skills_covered'][:5])}...")
    
    # Step 5: Submit self-assessment (sample answers)
    print("\nStep 5: Submitting self-assessment...")
    
    # Create sample answers
    sample_answers = []
    for question in test_data['test']['questions']:
        # Simulate realistic answers
        if question['type'] == 'proficiency':
            answer = "Intermediate"  # Default to intermediate
        else:
            answer = "Somewhat"
        
        sample_answers.append({
            "question_id": question['id'],
            "skill": question['skill'],
            "answer": answer,
            "confidence_level": 3
        })
    
    response = requests.post(
        f"{BASE_URL}/api/assessment/submit/{session_id}",
        json={"answers": sample_answers}
    )
    print_response("Assessment Submitted", response.json())
    
    # Step 6: Generate gap analysis report
    print("\nStep 6: Generating gap analysis report...")
    response = requests.post(f"{BASE_URL}/api/gap-analysis/{session_id}")
    report = response.json()
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"  📊 GAP ANALYSIS REPORT SUMMARY")
    print(f"{'='*60}")
    print(f"  Candidate: {report['user_name']}")
    print(f"  Current Level: {report['current_level']}")
    print(f"  Target Level: {report['target_level']}")
    print(f"  Overall Readiness: {report['overall_readiness']}%")
    print(f"  Status: {report['readiness_status']}")
    print(f"  Estimated Time: {report['estimated_time_to_target']}")
    print(f"\n  Skills On Track: {', '.join(report['skills_on_track'][:5])}")
    print(f"  Critical Gaps: {', '.join(report['critical_gaps'][:3]) if report['critical_gaps'] else 'None'}")
    print(f"  Priority Areas: {', '.join(report['priority_areas'][:3])}")
    
    # Print detailed skill gaps
    print(f"\n  📋 DETAILED SKILL GAPS:")
    for gap in report['skill_gaps'][:5]:  # Show first 5
        print(f"\n    • {gap['skill']}")
        print(f"      Current: {gap['current_level']} | Required: {gap['required_level']}")
        print(f"      Priority: {gap['priority']} | Gap: {gap['gap']}")
        if gap['recommendations']:
            print(f"      💡 {gap['recommendations'][0]}")
    
    # Print learning path
    print(f"\n  🎯 LEARNING PATH:")
    for step in report['learning_path'][:5]:
        print(f"\n    {step['phase']}: {step['skill']}")
        print(f"      Focus: {step['focus']}")
        print(f"      Duration: {step['duration']}")
    
    print(f"\n{'='*60}\n")
    print("✅ Demo completed successfully!")
    print(f"📄 Full report available at session: {session_id}")
    
    # Step 7: Retrieve full session data
    print("\n\nStep 7: Retrieving full session data...")
    response = requests.get(f"{BASE_URL}/api/session/{session_id}")
    print(f"  Session status: {response.json()['status']}")
    
    print("\n✨ All API endpoints tested successfully!\n")


if __name__ == "__main__":
    try:
        # Check if API is running
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            main()
        else:
            print("❌ API is not responding correctly. Make sure it's running on http://localhost:8000")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Please start the server first:")
        print("   python main.py")
        print("   or")
        print("   uvicorn main:app --reload")

