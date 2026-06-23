#!/usr/bin/env python3
"""
Advanced Example: Committee Decision Making with SSE Events (Python)

This example shows how to use SSE events for real-time progress tracking.

Requirements:
    pip install requests sseclient-py
"""

import requests
from sseclient import SSEClient
import json
import sys
import threading

SERVER_URL = "http://localhost:8000/mcp"
SSE_URL = "http://localhost:8000/sse"

class CommitteeClient:
    def __init__(self, server_url=SERVER_URL, sse_url=SSE_URL):
        self.server_url = server_url
        self.sse_url = sse_url
        self.event_handlers = {}
    
    def on(self, event_type, handler):
        """Register event handler."""
        self.event_handlers[event_type] = handler
    
    def start_session(self, topic, participants, rounds=1, event_level="progress"):
        """Start a committee discussion session."""
        response = requests.post(
            f"{self.server_url}/tools/start_committee_session",
            json={
                "topic": topic,
                "participants": participants,
                "debate_rounds": rounds,
                "event_config": {
                    "default_level": event_level
                }
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_synthesis(self, session_id):
        """Get discussion synthesis."""
        response = requests.post(
            f"{self.server_url}/tools/synthesize_discussion",
            json={"session_id": session_id}
        )
        response.raise_for_status()
        return response.json()
    
    def listen_events(self):
        """Listen to SSE events."""
        messages = SSEClient(self.sse_url)
        
        for msg in messages:
            if msg.event and msg.data:
                try:
                    data = json.loads(msg.data)
                    event_type = data.get('event_type')
                    
                    if event_type in self.event_handlers:
                        self.event_handlers[event_type](data)
                except json.JSONDecodeError:
                    pass

def main():
    print("🚀 Starting advanced committee discussion with SSE...\n")
    
    client = CommitteeClient()
    session_completed = threading.Event()
    session_id_holder = {}
    
    # Register event handlers
    client.on('session.started', lambda data: 
        print(f"🎬 Session started: {data['data']['topic']}"))
    
    client.on('phase.started', lambda data: 
        print(f"📍 Phase started: {data['data']['phase']}"))
    
    client.on('agent.started', lambda data: 
        print(f"🤖 Agent started: {data['data']['agent']['role']}"))
    
    client.on('agent.completed', lambda data: 
        print(f"✅ Agent completed: {data['data']['agent']['role']}"))
    
    client.on('phase.completed', lambda data: 
        print(f"✅ Phase completed: {data['data']['phase']}"))
    
    client.on('session.completed', lambda data: (
        print(f"🎉 Session completed! Duration: {data['data']['duration_ms']}ms"),
        session_completed.set()
    ))
    
    # Start SSE listener in background
    sse_thread = threading.Thread(target=client.listen_events, daemon=True)
    sse_thread.start()
    
    # Start session
    result = client.start_session(
        topic="Should we adopt microservices architecture?",
        participants=[
            {"role": "architect", "provider": "openai", "model": "gpt-4"},
            {"role": "devops", "provider": "anthropic", "model": "claude-3-sonnet"},
            {"role": "security", "provider": "gemini", "model": "gemini-pro"}
        ],
        rounds=2,
        event_level="progress"
    )
    
    session_id = result['session_id']
    session_id_holder['id'] = session_id
    print(f"📋 Session ID: {session_id}\n")
    print("📊 Receiving events...\n")
    
    # Wait for completion
    if not session_completed.wait(timeout=300):
        print("⏱️  Timeout waiting for completion")
        sys.exit(1)
    
    # Get synthesis
    print("\n📊 Getting synthesis...\n")
    synthesis = client.get_synthesis(session_id)
    
    # Display results
    print("\n=== Committee Decision ===\n")
    print("Summary:")
    print(synthesis['synthesis']['summary'])
    print("\nKey Points:")
    for i, point in enumerate(synthesis['synthesis'].get('key_points', []), 1):
        print(f"{i}. {point}")
    print("\nRecommendations:")
    for i, rec in enumerate(synthesis['synthesis']['recommendations'], 1):
        print(f"{i}. {rec}")
    
    print("\n✅ Done!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
