# 🐝 ResearchSwarm

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green.svg)](https://openai.com/)

**Multi-agent research system.** Ask a question, get a comprehensive research report from a swarm of AI specialists working in parallel.

## 🎯 The Idea

One agent is limited. A swarm is powerful.

ResearchSwarm spawns multiple specialist agents that work in parallel:
- 🔍 **Search Agent** — Finds relevant sources across the web
- 📊 **Data Agent** — Extracts and analyzes data
- 📚 **Literature Agent** — Reviews academic/industry sources
- ⚖️ **Critic Agent** — Identifies counterarguments and weaknesses
- ✍️ **Synthesis Agent** — Combines everything into a coherent report

```
┌────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   "What are the latest advances in AI agents and their             │
│    implications for software development?"                         │
│                                                                     │
└───────────────────────────┬────────────────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │      Coordinator Agent       │
              │   (Plans research strategy)  │
              └─────────────┬───────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Search Agent │   │  Data Agent  │   │ Literature   │
│   (Web)      │   │  (Analysis)  │   │   Agent      │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                          ▼
              ┌─────────────────────────────┐
              │      Synthesis Agent         │
              │   (Creates final report)     │
              └─────────────────────────────┘
                          │
                          ▼
              ┌─────────────────────────────┐
              │    Comprehensive Report      │
              │  • Executive Summary         │
              │  • Key Findings              │
              │  • Data & Evidence           │
              │  • Counterarguments          │
              │  • Conclusions               │
              │  • Sources                   │
              └─────────────────────────────┘
```

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🐝 **Parallel Execution** | Multiple agents work simultaneously |
| 🎯 **Specialized Agents** | Each agent has a specific research role |
| 🌐 **Web Search** | Real-time information from the internet |
| 📊 **Data Extraction** | Pull stats, figures, and structured data |
| ⚖️ **Critical Analysis** | Built-in skepticism and counterarguments |
| 📝 **Structured Reports** | Clean, professional output |
| 💾 **Source Tracking** | Every claim linked to its source |
| 🔄 **Iterative Depth** | Can go deeper on specific topics |

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/edwiniac/research-swarm.git
cd research-swarm

# Install dependencies
pip install -r requirements.txt

# Set API keys
export OPENAI_API_KEY="your-key"
export TAVILY_API_KEY="your-key"  # For web search (optional)
```

### Basic Usage

```bash
# Simple research query
python -m swarm research "What are the current trends in AI agents?"

# With depth control
python -m swarm research "Impact of LLMs on software engineering" --depth deep

# Output to file
python -m swarm research "Market analysis of AI startups" --output report.md

# Interactive mode
python -m swarm chat
```

### Python API

```python
from swarm import ResearchSwarm

swarm = ResearchSwarm()

# Run research
result = swarm.research(
    query="What are the latest advances in RAG systems?",
    depth="standard",  # quick, standard, deep
)

print(result.summary)
print(result.report)

# Access individual agent outputs
for agent_name, output in result.agent_outputs.items():
    print(f"{agent_name}: {output[:200]}...")
```

## 🛠️ CLI Commands

```bash
# Research commands
swarm research QUERY           # Run research on a query
swarm research QUERY --depth deep   # Deep research (more agents, more time)
swarm research QUERY --agents 3     # Limit number of parallel agents

# Interactive
swarm chat                     # Interactive research session

# Utilities
swarm agents                   # List available agent types
swarm config                   # Show configuration
```

## 🐝 Agent Types

### Core Agents (always active)

| Agent | Role | Tools |
|-------|------|-------|
| **Coordinator** | Plans research strategy, delegates tasks | Planning, task decomposition |
| **Search** | Web search and source discovery | Tavily, DuckDuckGo, Google |
| **Synthesis** | Combines findings into coherent report | Text analysis, summarization |

### Specialist Agents (activated based on query)

| Agent | Role | When Activated |
|-------|------|----------------|
| **Data** | Extract statistics, figures, data | Queries mentioning data, numbers, trends |
| **Literature** | Academic/research paper review | Technical or scientific queries |
| **News** | Recent news and events | Current events, market queries |
| **Critic** | Counterarguments and limitations | Always on deep research |
| **Code** | Technical implementation details | Programming-related queries |

## 📊 Research Depth Levels

### Quick (2-3 agents, ~30 seconds)
- Basic web search
- Quick synthesis
- Good for simple factual queries

### Standard (4-5 agents, ~2 minutes)
- Comprehensive web search
- Data extraction
- Multiple source synthesis
- Good for most research tasks

### Deep (6-8 agents, ~5 minutes)
- All specialist agents
- Critical analysis
- Iterative refinement
- Academic sources
- Good for thorough research

## 📝 Output Format

```markdown
# Research Report: [Your Query]

## Executive Summary
[2-3 paragraph overview of findings]

## Key Findings

### 1. [Finding Title]
[Detailed explanation with evidence]
- Supporting point 1 [Source 1]
- Supporting point 2 [Source 2]

### 2. [Finding Title]
...

## Data & Statistics
| Metric | Value | Source |
|--------|-------|--------|
| ...    | ...   | ...    |

## Counterarguments & Limitations
- [Limitation 1]
- [Limitation 2]

## Conclusions
[Final synthesis and recommendations]

## Sources
1. [Source 1 - URL]
2. [Source 2 - URL]
...

---
*Generated by ResearchSwarm on [date]*
*Agents used: Search, Data, Literature, Critic, Synthesis*
*Total research time: X minutes*
```

## 🔧 Configuration

```yaml
# config.yaml
llm:
  provider: openai
  model: gpt-4o
  temperature: 0.3

search:
  provider: tavily  # tavily, duckduckgo, serper
  max_results: 10

agents:
  max_parallel: 5
  timeout_seconds: 120
  
output:
  format: markdown  # markdown, json, html
  include_sources: true
  include_agent_logs: false
```

## 🏗️ Architecture

```
research-swarm/
├── swarm/
│   ├── __init__.py
│   ├── coordinator.py     # Main orchestration logic
│   ├── agents/
│   │   ├── base.py        # Base agent class
│   │   ├── search.py      # Web search agent
│   │   ├── data.py        # Data extraction agent
│   │   ├── literature.py  # Academic research agent
│   │   ├── critic.py      # Critical analysis agent
│   │   └── synthesis.py   # Report synthesis agent
│   ├── tools/
│   │   ├── web_search.py  # Search tool implementations
│   │   └── scraper.py     # Web scraping utilities
│   ├── output/
│   │   └── formatter.py   # Report formatting
│   └── cli.py             # Command-line interface
├── config.yaml
└── requirements.txt
```

## 🔌 Extending with Custom Agents

```python
from swarm.agents.base import BaseAgent

class CustomAgent(BaseAgent):
    name = "custom"
    description = "My custom research agent"
    
    def run(self, task: str, context: dict) -> str:
        # Your agent logic here
        result = self.llm.complete(
            f"Task: {task}\nContext: {context}"
        )
        return result

# Register the agent
from swarm import ResearchSwarm
swarm = ResearchSwarm()
swarm.register_agent(CustomAgent())
```

## 📈 Performance

| Depth | Agents | Avg Time | Tokens Used |
|-------|--------|----------|-------------|
| Quick | 2-3 | 30s | ~2,000 |
| Standard | 4-5 | 2min | ~8,000 |
| Deep | 6-8 | 5min | ~20,000 |

*Times and tokens vary based on query complexity.*

## ⚠️ Limitations

- Web search requires API keys (Tavily recommended)
- Deep research can be token-intensive
- Real-time data may have slight delays
- Academic sources limited to open-access content

## 🤝 Contributing

Contributions welcome! Areas of interest:
- New specialist agents
- Additional search providers
- Output format options
- Performance optimizations

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Research smarter, not harder.** Let the swarm do the work.
