import os
import json
from pathlib import Path
from typing import List, Dict, Any
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import difflib

load_dotenv()


def _load_policy_document(file_path: Path) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def _get_embeddings():
    return OpenAIEmbeddings(
        model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        api_key=os.getenv("OPENAI_API_KEY")
    )


@tool
def compare_policy_versions(old_version: str, new_version: str) -> Dict[str, Any]:
    """
    Compare two versions of a policy document and identify changes.
    
    Args:
        old_version: Filename of old version (e.g., "benefits_policy_v1.md")
        new_version: Filename of new version (e.g., "benefits_policy_v2.md")
    
    Returns:
        {
            "changes_detected": bool,
            "change_count": int,
            "changes": List of specific changes,
            "affected_sections": List of policy sections changed
        }
    """
    policy_dir = Path("data/policy_versions")
    
    old_path = policy_dir / old_version
    new_path = policy_dir / new_version
    
    if not old_path.exists() or not new_path.exists():
        return {
            "error": "Policy file not found",
            "old_exists": old_path.exists(),
            "new_exists": new_path.exists()
        }
    
    old_content = _load_policy_document(old_path)
    new_content = _load_policy_document(new_path)
    
    old_lines = old_content.splitlines()
    new_lines = new_content.splitlines()
    
    differ = difflib.unified_diff(old_lines, new_lines, lineterm='')
    diff_lines = list(differ)
    
    changes = []
    affected_sections = set()
    current_section = "Unknown"
    
    for line in diff_lines:
        if line.startswith('##'):
            current_section = line.replace('#', '').strip()
        elif line.startswith('+') and not line.startswith('+++'):
            changes.append({
                "type": "added",
                "section": current_section,
                "content": line[1:].strip()
            })
            affected_sections.add(current_section)
        elif line.startswith('-') and not line.startswith('---'):
            changes.append({
                "type": "removed",
                "section": current_section,
                "content": line[1:].strip()
            })
            affected_sections.add(current_section)
    
    meaningful_changes = [
        c for c in changes 
        if not any(keyword in c['content'].lower() for keyword in ['version', 'effective date', 'last updated'])
    ]
    
    return {
        "changes_detected": len(meaningful_changes) > 0,
        "change_count": len(meaningful_changes),
        "changes": meaningful_changes[:20],  # Limit to 20 most significant
        "affected_sections": list(affected_sections)
    }


@tool
def detect_semantic_drift(section_old: str, section_new: str) -> Dict[str, Any]:
    """
    Detect semantic changes in policy sections using embeddings.
    
    Args:
        section_old: Old section text
        section_new: New section text
    
    Returns:
        {
            "similarity_score": float (0-1),
            "significant_change": bool,
            "change_magnitude": str (minor/moderate/major)
        }
    """
    embeddings = _get_embeddings()
    
    old_emb = embeddings.embed_query(section_old)
    new_emb = embeddings.embed_query(section_new)
    
    import numpy as np
    similarity = np.dot(old_emb, new_emb) / (np.linalg.norm(old_emb) * np.linalg.norm(new_emb))
    
    if similarity > 0.95:
        magnitude = "minor"
        significant = False
    elif similarity > 0.85:
        magnitude = "moderate"
        significant = True
    else:
        magnitude = "major"
        significant = True
    
    return {
        "similarity_score": round(float(similarity), 3),
        "significant_change": significant,
        "change_magnitude": magnitude
    }


@tool
def route_notifications(affected_sections: List[str]) -> Dict[str, Any]:
    """
    Determine who should be notified based on policy sections changed.
    
    Args:
        affected_sections: List of policy section names that changed
    
    Returns:
        {
            "notification_plan": List of notifications to send,
            "total_recipients": int,
            "priority_breakdown": dict
        }
    """
    rules_path = Path("data/policy_versions/notification_rules.json")
    
    if not rules_path.exists():
        return {
            "error": "Notification rules not found"
        }
    
    with open(rules_path, 'r') as f:
        rules_data = json.load(f)
    
    notification_plan = []
    all_groups = set()
    priority_count = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    
    for section in affected_sections:
        for rule in rules_data['notification_rules']:
            if any(keyword.lower() in section.lower() for keyword in rule['keywords']):
                for notification in rule['notify']:
                    notification_plan.append({
                        "group": notification['group'],
                        "priority": notification['priority'],
                        "channel": notification['channel'],
                        "reason": f"Policy change in: {section}"
                    })
                    all_groups.add(notification['group'])
                    priority_count[notification['priority']] += 1
    
    return {
        "notification_plan": notification_plan,
        "total_recipient_groups": len(all_groups),
        "priority_breakdown": priority_count,
        "affected_sections": affected_sections
    }


@tool
def summarize_policy_changes(changes: List[Dict]) -> Dict[str, Any]:
    """
    Create a human-readable summary of policy changes.
    
    Args:
        changes: List of change dictionaries from compare_policy_versions
    
    Returns:
        {
            "summary": str,
            "key_changes": List of most important changes,
            "sections_modified": int
        }
    """
    if not changes:
        return {
            "summary": "No significant changes detected",
            "key_changes": [],
            "sections_modified": 0
        }
    
    by_section = {}
    for change in changes:
        section = change.get('section', 'Unknown')
        if section not in by_section:
            by_section[section] = []
        by_section[section].append(change)
    
    key_changes = [
        {
            "section": change['section'],
            "description": change['content']
        }
        for change in changes 
        if change['type'] == 'added' and len(change['content']) > 20
    ][:5]  
    
    summary_parts = []
    for section, section_changes in by_section.items():
        additions = sum(1 for c in section_changes if c['type'] == 'added')
        removals = sum(1 for c in section_changes if c['type'] == 'removed')
        summary_parts.append(f"{section}: {additions} additions, {removals} removals")
    
    summary = f"Policy updated across {len(by_section)} sections. " + "; ".join(summary_parts[:3])
    
    return {
        "summary": summary,
        "key_changes": key_changes,
        "sections_modified": len(by_section)
    }