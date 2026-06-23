#!/usr/bin/env python3
"""
Basic Example: Committee Decision Making (Python)

This example shows the simplest way to use the committee decision-making skill.

Requirements:
    pip install requests
"""

import requests
import time
import json
import sys

SERVER_URL = "http://localhost:8000/mcp"

def start_session(topic, participants, rounds=1):
    """Start a committee discussion session."""
    response = requests.post(
        f"{SERVER_URL}/tools/start_committee_session",
        json={
            "topic": topic,
            "participants": participants,
            "debate_rounds": rounds
        }
    )
    response.raise_for_status()
    return response.json()

def get_status(session_id):
    """Get session status."""
    response = requests.post(
        f"{SERVER_URL}/tools/get_session_status",
        json={"session_id": session_id}
    )
    response.raise_for_status()
    return response.json()

def get_synthesis(session_id):
    """Get discussion synthesis."""
    response = requests.post(
        f"{SERVER_URL}/tools/synthesize_discussion",
        json={"session_id": session_id}
    )
    response.raise_for_status()
    return response.json()

def wait_for_completion(session_id, timeout=300):
    """Poll until session completes."""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        status = get_status(session_id)
        
        print(f"   Status: {status['status']}, Phase: {status.get('current_phase', 'N/A')}")
        
        if status['status'] == 'completed':
            return True
        elif status['status'] == 'error':
            raise Exception("Session failed")
        
        time.sleep(5)
    
    raise TimeoutError(f"Session did not complete within {timeout} seconds")

def main():
    print("🚀 Starting basic committee discussion...\n")
    
    # Start session
    result = start_session(
        topic="Should we adopt microservices architecture?",
        participants=[
            {"role": "architect", "provider": "openai", "model": "gpt-4"},
            {"role": "devops", "provider": "anthropic", "model": "claude-3-sonnet"}
        ],
        rounds=1
    )
    
    session_id = result['session_id']
    print(f"📋 Session started: {session_id}\n")
    
    # Wait for completion
    print("⏳ Waiting for discussion to complete...\n")
    wait_for_completion(session_id)
    
    # Get synthesis
    print("\n📊 Getting synthesis...\n")
    synthesis = get_synthesis(session_id)
    
    # Display results
    print("=== Committee Decision ===\n")
    print("Summary:")
    print(synthesis['synthesis']['summary'])
    print("\nRecommendations:")
    for i, rec in enumerate(synthesis['synthesis']['recommendations'], 1):
        print(f"{i}. {rec}")
    
    print("\n✅ Done!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
