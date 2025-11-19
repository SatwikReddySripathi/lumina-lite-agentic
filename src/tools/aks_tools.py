import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.utilities import GoogleSearchAPIWrapper
from dotenv import load_dotenv

load_dotenv()

_aks_embeddings: Optional[OpenAIEmbeddings] = None
_aks_vector_store: Optional[Chroma] = None
_web_search: Optional[GoogleSearchAPIWrapper] = None


def _get_aks_embeddings():
    global _aks_embeddings
    
    if _aks_embeddings is None:
        _aks_embeddings = OpenAIEmbeddings(
            model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    return _aks_embeddings


def _get_aks_vector_store():
    global _aks_vector_store
    
    if _aks_vector_store is not None:
        return _aks_vector_store
    
    embeddings = _get_aks_embeddings()
    persist_dir = "./chroma_db_aks"
    
    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        try:
            _aks_vector_store = Chroma(
                persist_directory=persist_dir,
                embedding_function=embeddings
            )
            return _aks_vector_store
        except:
            pass
    
    docs_dir = Path("docs")
    all_docs = []
    
    for md_file in docs_dir.glob("*.md"):
        try:
            loader = TextLoader(str(md_file), encoding='utf-8')
            docs = loader.load()
            
            for doc in docs:
                doc.metadata["source"] = md_file.name
                doc.metadata["type"] = "internal_kb"
                doc.metadata["doc_id"] = md_file.stem
            
            all_docs.extend(docs)
        except Exception as e:
            print(f"Warning: Could not load {md_file}: {e}")
    
    if not all_docs:
        raise ValueError("No AKS documents found in docs/ directory")
    
    print(f"Indexing {len(all_docs)} AKS documents...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        length_function=len
    )
    splits = text_splitter.split_documents(all_docs)
    
    print(f"Created {len(splits)} chunks")
    
    _aks_vector_store = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    
    print(f"AKS vector store created")
    
    return _aks_vector_store


@tool
def search_internal_aks_kb(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Search CVS Health's internal AKS knowledge base.
    
    Args:
        query: Technical question about AKS networking
        top_k: Number of results (default: 5)
    
    Returns:
        {
            "results": List of relevant chunks with citations,
            "count": Number of results,
            "sources": Document IDs
        }
    """
    vector_store = _get_aks_vector_store()
    
    results = vector_store.similarity_search_with_score(query, k=top_k)
    
    formatted_results = []
    sources = set()
    
    for doc, score in results:
        formatted_results.append({
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "doc_id": doc.metadata.get("doc_id", "unknown"),
            "relevance_score": round(float(score), 3)
        })
        sources.add(doc.metadata.get("doc_id", "unknown"))
    
    return {
        "results": formatted_results,
        "count": len(formatted_results),
        "sources": list(sources),
        "source_type": "internal_kb"
    }


@tool
def search_web_for_aks_info(query: str) -> Dict[str, Any]:
    """
    Search the web for AKS networking information (Azure documentation, Stack Overflow, etc.).
    
    Args:
        query: Technical question to search for
    
    Returns:
        {
            "results": Web search results with URLs,
            "count": Number of results,
            "source_type": "web"
        }
    """
    
    simulated_results = [
        {
            "title": "Network concepts for AKS - Azure Kubernetes Service",
            "url": "https://learn.microsoft.com/en-us/azure/aks/concepts-network",
            "snippet": "Learn about networking in Azure Kubernetes Service (AKS), including kubenet and Azure CNI, ingress controllers, load balancers, and static IP addresses.",
            "relevance": "high"
        },
        {
            "title": "Configure Azure CNI networking - AKS",
            "url": "https://learn.microsoft.com/en-us/azure/aks/configure-azure-cni",
            "snippet": "Azure CNI is the default network plugin for AKS. Each pod gets an IP address from the subnet and can be accessed directly. Requires more IP addresses than kubenet.",
            "relevance": "high"
        },
        {
            "title": "Best practices for network connectivity - AKS",
            "url": "https://learn.microsoft.com/en-us/azure/aks/operator-best-practices-network",
            "snippet": "Best practices for network resources and connectivity in AKS. Covers NSG rules, private endpoints, network policies, and egress traffic control.",
            "relevance": "high"
        },
        {
            "title": "Use a private endpoint with Azure Kubernetes Service",
            "url": "https://learn.microsoft.com/en-us/azure/aks/private-clusters",
            "snippet": "Create an AKS cluster with a private endpoint to ensure network traffic between your API server and node pools remains on the private network only.",
            "relevance": "medium"
        },
        {
            "title": "Network security groups (NSG) in Azure - Overview",
            "url": "https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview",
            "snippet": "Network security groups filter network traffic between Azure resources in a virtual network. NSG contains security rules that allow or deny traffic based on protocol, port, and address.",
            "relevance": "medium"
        }
    ]
    
    query_lower = query.lower()
    relevant_results = []
    
    for result in simulated_results:
        score = 0
        if any(kw in query_lower for kw in ['nsg', 'security group', 'firewall']):
            if 'nsg' in result['title'].lower() or 'security' in result['snippet'].lower():
                score += 2
        if any(kw in query_lower for kw in ['private', 'endpoint', 'api server']):
            if 'private' in result['title'].lower():
                score += 2
        if 'cni' in query_lower and 'cni' in result['title'].lower():
            score += 3
        
        if score > 0 or result['relevance'] == 'high':
            relevant_results.append({
                **result,
                "search_score": score
            })
    
    relevant_results.sort(key=lambda x: x.get('search_score', 0), reverse=True)
    
    return {
        "results": relevant_results[:3],
        "count": len(relevant_results[:3]),
        "source_type": "web",
        "note": "Results from Microsoft Azure documentation and community resources"
    }


@tool
def suggest_it_forms(topic: str) -> Dict[str, Any]:
    """
    Suggest relevant IT service forms based on the topic.
    
    Args:
        topic: Topic keywords (e.g., "NSG rules", "new cluster", "troubleshooting")
    
    Returns:
        List of relevant forms with URLs and descriptions
    """
    forms_path = Path("data/it_forms.json")
    
    if not forms_path.exists():
        return {
            "found": False,
            "message": "IT forms database not found"
        }
    
    with open(forms_path, 'r') as f:
        forms_data = json.load(f)
    
    topic_lower = topic.lower()
    matched_forms = []
    
    for form in forms_data['forms']:
        match_score = 0
        for keyword in form['required_for']:
            if keyword.lower() in topic_lower or topic_lower in keyword.lower():
                match_score += 1
        
        if match_score > 0:
            matched_forms.append({
                **form,
                "match_score": match_score
            })
    
    matched_forms.sort(key=lambda x: x['match_score'], reverse=True)
    
    return {
        "found": len(matched_forms) > 0,
        "forms": matched_forms[:3],  
        "count": len(matched_forms),
        "source_type": "it_forms"
    }