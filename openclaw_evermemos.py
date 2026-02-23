#!/usr/bin/env python3
"""
OpenClaw Memory Integration with EverMemOS
==========================================
This script provides integration between OpenClaw's memory system and EverMemOS.

Usage:
    python3 openclaw_evermemos.py --store "message content" --user main --group openclaw
    python3 openclaw_evermemos.py --search "query"
    python3 openclaw_evermemos.py --retrieve --user main
"""

import argparse
import json
import requests
import sys
from datetime import datetime

# EverMemOS API Configuration
EVERMEMOS_URL = "http://localhost:8001/api/v1/memories"

def store_memory(message: str, user_id: str, group_id: str = None, 
                 group_name: str = None, role: str = "assistant"):
    """
    Store a message into EverMemOS memory system.
    
    Args:
        message: Message content to store
        user_id: User/Sender identifier
        group_id: Optional group conversation ID
        group_name: Optional group name
        role: "user" or "assistant"
    """
    payload = {
        "message_id": f"msg_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "create_time": datetime.now().isoformat(),
        "sender": user_id,
        "sender_name": user_id,
        "content": message,
        "group_id": group_id or user_id,
        "group_name": group_name or f"{user_id}'s conversations",
        "role": role,
        "refer_list": []
    }
    
    try:
        response = requests.post(
            f"{EVERMEMOS_URL}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def retrieve_memories(user_id: str = None, group_id: str = None, 
                      memory_type: str = "episodic_memory", limit: int = 40):
    """
    Retrieve memories from EverMemOS.
    
    Args:
        user_id: User ID to filter by
        group_id: Group ID to filter by
        memory_type: Type of memory (episodic_memory, profile, event_log)
        limit: Maximum number of memories to retrieve
    """
    params = {
        "memory_type": memory_type,
        "limit": limit
    }
    
    if user_id:
        params["user_id"] = user_id
    if group_id:
        params["group_id"] = group_id
    
    try:
        response = requests.get(
            f"{EVERMEMOS_URL}",
            params=params,
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def search_memories(query: str, user_id: str = None, limit: int = 10):
    """
    Search memories using vector similarity.
    
    Args:
        query: Search query
        user_id: Optional user ID filter
        limit: Maximum results
    """
    params = {
        "query": query,
        "limit": limit
    }
    
    if user_id:
        params["user_id"] = user_id
    
    try:
        response = requests.get(
            f"{EVERMEMOS_URL}/search",
            params=params,
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def save_conversation_meta(conversation_id: str, metadata: dict):
    """
    Save conversation metadata.
    
    Args:
        conversation_id: Unique conversation identifier
        metadata: Metadata dictionary (title, participants, etc.)
    """
    payload = {
        "conversation_id": conversation_id,
        **metadata
    }
    
    try:
        response = requests.post(
            f"{EVERMEMOS_URL}/conversation-meta",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    parser = argparse.ArgumentParser(
        description="OpenClaw EverMemOS Integration Tool"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Store command
    store_parser = subparsers.add_parser("store", help="Store a memory")
    store_parser.add_argument("--message", "-m", required=True, help="Message content")
    store_parser.add_argument("--user", "-u", required=True, help="User ID")
    store_parser.add_argument("--group", "-g", help="Group ID")
    store_parser.add_argument("--group-name", help="Group name")
    store_parser.add_argument("--role", default="assistant", 
                             choices=["user", "assistant"], help="Message role")
    
    # Retrieve command
    retrieve_parser = subparsers.add_parser("retrieve", help="Retrieve memories")
    retrieve_parser.add_argument("--user", "-u", help="User ID filter")
    retrieve_parser.add_argument("--group", "-g", help="Group ID filter")
    retrieve_parser.add_argument("--type", default="episodic_memory",
                                choices=["episodic_memory", "profile", "event_log"],
                                help="Memory type")
    retrieve_parser.add_argument("--limit", type=int, default=40,
                                help="Maximum results")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search memories")
    search_parser.add_argument("--query", "-q", required=True, help="Search query")
    search_parser.add_argument("--user", "-u", help="User ID filter")
    search_parser.add_argument("--limit", type=int, default=10,
                              help="Maximum results")
    
    args = parser.parse_args()
    
    if args.command == "store":
        result = store_memory(
            message=args.message,
            user_id=args.user,
            group_id=args.group,
            group_name=args.group_name,
            role=args.role
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    elif args.command == "retrieve":
        result = retrieve_memories(
            user_id=args.user,
            group_id=args.group,
            memory_type=args.type,
            limit=args.limit
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    elif args.command == "search":
        result = search_memories(
            query=args.query,
            user_id=args.user,
            limit=args.limit
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
