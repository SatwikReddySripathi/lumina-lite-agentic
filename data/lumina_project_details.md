# Lumina Project Details

## Project History
- **Launch Date**: September 2024
- **Current Version**: v1.0
- **Users**: 5,000+ CVS colleagues
- **Queries Processed**: 150K+

## Technical Stack
- **LLM**: GPT-4o, GPT-4o-mini for simple queries
- **Vector DB**: MongoDB Atlas with vector search
- **Orchestration**: LangGraph for agentic workflows
- **Deployment**: Azure Kubernetes Service (AKS)
- **CI/CD**: GitHub Actions
- **Monitoring**: Azure Application Insights

## Key Features
1. **Document Search** - Semantic search across 10K+ internal docs
2. **Video Transcript Search** - Search meeting recordings with timestamps
3. **Colleague Finder** - Locate experts and team members
4. **AKS Network Assistant** - IT troubleshooting and form suggestions
5. **Policy Q&A** - Answer questions about HR policies, benefits

## Team Contributions

### Sarah Chen (Lead)
- Designed RAG architecture with hybrid search (semantic + keyword)
- Built evaluation harness with 500+ test cases
- Optimized chunking strategy: 512 tokens with 50 token overlap
- **Achievement**: Reduced hallucination rate from 12% to 3%

### Marcus Rodriguez
- Implemented LangGraph agents for multi-step workflows
- Built colleague lookup with 3-tool orchestration
- Created policy change detection system
- **Achievement**: Enabled complex queries requiring 5+ tool calls

### Priya Patel
- Built SharePoint document ingestion pipeline (processes 500 docs/day)
- Optimized embedding generation (reduced cost by 60%)
- Implemented video transcript chunking with timestamp preservation
- **Achievement**: Indexed 2,000 hours of video content

### Alex Kim
- Deployed Lumina to AKS with auto-scaling (2-20 pods)
- Set up GitHub Actions CI/CD with automated testing
- Implemented blue-green deployment for zero-downtime updates
- **Achievement**: 99.9% uptime since launch

### Jordan Taylor
- Built FastAPI backend with 15 endpoints
- Implemented cost tracking (saves $2K/month through smart routing)
- Created analytics dashboard for product team
- **Achievement**: API response time p95 < 2 seconds

## Success Metrics
- **User Satisfaction**: 4.6/5 stars
- **Query Success Rate**: 87%
- **Average Response Time**: 1.8 seconds
- **Cost per Query**: $0.015
- **Monthly Active Users**: 3,200+

## Roadmap
- Q4 2024: Add fine-tuning pipeline for domain-specific queries
- Q1 2025: Expand to 50K users, add multilingual support
- Q2 2025: Integrate with Slack, Teams for inline queries
- Q3 2025: Implement memory/personalization