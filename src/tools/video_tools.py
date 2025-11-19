
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()

_video_embeddings: Optional[OpenAIEmbeddings] = None
_video_vector_store: Optional[Chroma] = None


def _get_video_embeddings():
    global _video_embeddings
    
    if _video_embeddings is None:
        _video_embeddings = OpenAIEmbeddings(
            model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    return _video_embeddings


def _load_video_transcript(video_path: Path) -> Dict[str, Any]:
    with open(video_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _get_video_vector_store():
    global _video_vector_store
    
    if _video_vector_store is not None:
        return _video_vector_store
    
    embeddings = _get_video_embeddings()
    persist_dir = "./chroma_db_videos"
    
    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        try:
            _video_vector_store = Chroma(
                persist_directory=persist_dir,
                embedding_function=embeddings
            )
            return _video_vector_store
        except:
            pass
    
    videos_dir = Path("videos")
    all_chunks = []
    
    for json_file in videos_dir.glob("*.json"):
        try:
            video_data = _load_video_transcript(json_file)
            
            for segment in video_data['transcript']:
                doc = Document(
                    page_content=segment['text'],
                    metadata={
                        "video_id": video_data['video_id'],
                        "video_title": video_data['title'],
                        "speaker": video_data['speaker'],
                        "date": video_data['date'],
                        "timestamp": segment['timestamp'],
                        "duration": segment['duration'],
                        "video_url": video_data['url'],
                        "thumbnail": video_data.get('thumbnail', ''),
                        "source_type": "video_transcript"
                    }
                )
                all_chunks.append(doc)
        
        except Exception as e:
            print(f"Warning: Could not load {json_file}: {e}")
    
    if not all_chunks:
        raise ValueError("No video transcripts found in videos/ directory")
    
    print(f"Indexing {len(all_chunks)} video segments from {len(list(videos_dir.glob('*.json')))} videos...")
    
    _video_vector_store = Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    
    print(f"Video vector store created")
    
    return _video_vector_store


@tool
def search_video_transcripts(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Search video transcripts for relevant content with timestamps.
    
    Args:
        query: Search query (e.g., "How do I deploy to AKS?")
        top_k: Number of results (default: 5)
    
    Returns:
        {
            "results": List of matching segments with timestamps,
            "count": Number of results,
            "videos": Unique video IDs found
        }
    """
    vector_store = _get_video_vector_store()
    
    results = vector_store.similarity_search_with_score(query, k=top_k)
    
    formatted_results = []
    video_ids = set()
    
    for doc, score in results:
        formatted_results.append({
            "text": doc.page_content,
            "video_id": doc.metadata.get("video_id"),
            "video_title": doc.metadata.get("video_title"),
            "speaker": doc.metadata.get("speaker"),
            "timestamp": doc.metadata.get("timestamp"),
            "duration": doc.metadata.get("duration"),
            "video_url": doc.metadata.get("video_url"),
            "thumbnail": doc.metadata.get("thumbnail"),
            "relevance_score": round(float(score), 3)
        })
        video_ids.add(doc.metadata.get("video_id"))
    
    return {
        "results": formatted_results,
        "count": len(formatted_results),
        "videos": list(video_ids),
        "source_type": "video_transcripts"
    }


@tool
def get_video_summary(video_id: str) -> Dict[str, Any]:
    """
    Get summary information about a specific video.
    
    Args:
        video_id: Video ID (e.g., "VID-001")
    
    Returns:
        Video metadata and full transcript
    """
    videos_dir = Path("videos")
    
    for json_file in videos_dir.glob("*.json"):
        try:
            video_data = _load_video_transcript(json_file)
            if video_data['video_id'] == video_id:
                return {
                    "found": True,
                    "video_id": video_data['video_id'],
                    "title": video_data['title'],
                    "speaker": video_data['speaker'],
                    "date": video_data['date'],
                    "duration": video_data['duration'],
                    "url": video_data['url'],
                    "thumbnail": video_data.get('thumbnail'),
                    "segment_count": len(video_data['transcript'])
                }
        except:
            continue
    
    return {
        "found": False,
        "message": f"Video {video_id} not found"
    }


@tool
def search_by_speaker(speaker_name: str) -> Dict[str, Any]:
    """
    Find all videos by a specific speaker.
    
    Args:
        speaker_name: Speaker name (e.g., "Sarah Chen")
    
    Returns:
        List of videos by that speaker
    """
    videos_dir = Path("videos")
    matching_videos = []
    
    for json_file in videos_dir.glob("*.json"):
        try:
            video_data = _load_video_transcript(json_file)
            if speaker_name.lower() in video_data['speaker'].lower():
                matching_videos.append({
                    "video_id": video_data['video_id'],
                    "title": video_data['title'],
                    "speaker": video_data['speaker'],
                    "date": video_data['date'],
                    "duration": video_data['duration'],
                    "url": video_data['url']
                })
        except:
            continue
    
    return {
        "found": len(matching_videos) > 0,
        "count": len(matching_videos),
        "videos": matching_videos
    }