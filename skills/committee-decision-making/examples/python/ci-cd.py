#!/usr/bin/env python3
"""
CI/CD Example: Committee Decision Making (Python)

This example shows how to use the committee for automated decision-making in CI/CD.

Requirements:
    pip install requests

Usage in CI/CD:
    python ci-cd.py --topic "Should we deploy this change?" --decision-field decision
    
Exit codes:
    0 - Decision is "go"
    1 - Decision is "no-go" or error
    2 - Decision is "conditional"
"""

import requests
import time
import sys
import argparse

SERVER_URL = "http://localhost:8000/mcp"

def start_session(topic, participants, rounds=1):
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

def wait_for_completion(session_id, timeout=300):
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = requests.post(
            f"{SERVER_URL}/tools/get_session_status",
            json={"session_id": session_id}
        )
        response.raise_for_status()
        status = response.json()
        
        if status['status'] == 'completed':
            return True
        elif status['status'] == 'error':
            raise Exception("Session failed")
        
        time.sleep(5)
    
    raise TimeoutError("Session timeout")

def get_synthesis(session_id):
    response = requests.post(
        f"{SERVER_URL}/tools/synthesize_discussion",
        json={"session_id": session_id}
    )
    response.raise_for_status()
    return response.json()

def main():
    parser = argparse.ArgumentParser(description='Committee decision for CI/CD')
    parser.add_argument('--topic', required=True, help='Discussion topic')
    parser.add_argument('--decision-field', default='decision', help='Field to check for decision')
    parser.add_argument('--timeout', type=int, default=300, help='Timeout in seconds')
    args = parser.parse_args()
    
    print(f"🤖 CI/CD Committee Decision")
    print(f"📋 Topic: {args.topic}\n")
    
    # Start session with relevant roles for CI/CD
    result = start_session(
        topic=args.topic,
        participants=[
            {"role": "architect", "provider": "openai", "model": "gpt-4"},
            {"role": "security", "provider": "anthropic", "model": "claude-3-sonnet"}
        ],
        rounds=1
    )
    
    session_id = result['session_id']
    print(f"Session: {session_id}")
    
    # Wait for completion
    print("⏳ Waiting for decision...")
    wait_for_completion(session_id, args.timeout)
    
    # Get synthesis
    synthesis = get_synthesis(session_id)
    decision = synthesis['synthesis'].get(args.decision_field, 'no-go')
    
    print(f"\n📊 Decision: {decision}")
    print(f"Summary: {synthesis['synthesis']['summary'][:200]}...")
    
    # Exit based on decision
    if decision == 'go':
        print("\n✅ APPROVED - Proceeding with deployment")
        sys.exit(0)
    elif decision == 'conditional':
        print("\n⚠️  CONDITIONAL - Review required")
        print("Conditions:")
        for cond in synthesis['synthesis'].get('conditions', []):
            print(f"  - {cond}")
        sys.exit(2)
    else:
        print("\n❌ REJECTED - Deployment blocked")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
