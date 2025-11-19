import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from dotenv import load_dotenv

load_dotenv()

_embeddings: Optional[OpenAIEmbeddings] = None
_vector_store: Optional[Chroma] = None


def _get_embeddings():
    global _embeddings
    
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings(
            model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    return _embeddings


def _get_or_create_vector_store():
    """Get or create the vector store."""
    global _vector_store
    
    if _vector_store is not None:
        return _vector_store
    
    embeddings = _get_embeddings()
    persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    
    # Check if vector store exists
    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        try:
            _vector_store = Chroma(
                persist_directory=persist_dir,
                embedding_function=embeddings
            )
            return _vector_store
        except:
            pass
    
    docs_dir = Path("data")
    all_docs = []
    
    # Load markdown files
    for md_file in docs_dir.glob("*.md"):
        try:
            loader = TextLoader(str(md_file), encoding='utf-8')
            docs = loader.load()
            
            for doc in docs:
                doc.metadata["source"] = md_file.name
                doc.metadata["type"] = "team_doc"
            
            all_docs.extend(docs)
        except Exception as e:
            print(f"Warning: Could not load {md_file}: {e}")
            continue
    
    if not all_docs:
        raise ValueError("No documents found in data/ directory. Please add .md files.")
    
    print(f"Indexing {len(all_docs)} documents...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=50,
        length_function=len
    )
    splits = text_splitter.split_documents(all_docs)
    
    print(f"Created {len(splits)} chunks")
    
    _vector_store = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    
    print(f"Vector store created at {persist_dir}")
    
    return _vector_store


@tool
def search_team_documents(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Search team documentation using semantic search.
    
    Args:
        query: Search query (e.g., "who are the data scientists?")
        top_k: Number of results to return (default: 5)
    
    Returns:
        {
            "results": List of matching document chunks,
            "count": Number of results,
            "sources": List of source documents
        }
    """
    vector_store = _get_or_create_vector_store()
    
    results = vector_store.similarity_search_with_score(query, k=top_k)
    
    formatted_results = []
    sources = set()
    
    for doc, score in results:
        formatted_results.append({
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "score": float(score)
        })
        sources.add(doc.metadata.get("source", "unknown"))
    
    return {
        "results": formatted_results,
        "count": len(formatted_results),
        "sources": list(sources),
        "query": query
    }


@tool
def search_for_people(keywords: List[str]) -> Dict[str, Any]:
    """
    Search documents specifically for people/names.
    
    Args:
        keywords: List of keywords to search for (e.g., ["data scientist", "engineer"])
    
    Returns:
        Names and roles found in documents
    """
    vector_store = _get_or_create_vector_store()
    
    all_results = []
    for keyword in keywords:
        results = vector_store.similarity_search(keyword, k=3)
        all_results.extend(results)
    
    combined_text = "\n".join([doc.page_content for doc in all_results])
    
    return {
        "found_text": combined_text[:2000],  
        "document_count": len(all_results),
        "keywords_searched": keywords
    }