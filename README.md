# Hive Five - Big Five Multi-Agent System

A sophisticated multi-agent simulation system where AI agents with distinct Big Five personality profiles interact in real-time through an event-driven architecture.

## 🎯 Overview

Five AI agents with unique personalities (based on the Big Five model) communicate asynchronously via Apache Kafka, make decisions via GLM-4.6 LLM, develop relationships and emotional states, forming a dynamic social simulation.

### The Five Agents

- **Alex** - The Extroverted Leader (High E: 95)
- **Morgan** - The Analytical Introvert (Low E: 25, High O: 90)
- **Jordan** - The Agreeable Mediator (High A: 90)
- **Casey** - The Creative Chaotic (High O: 95, High N: 70)
- **Taylor** - The Stable Pragmatist (High C: 95, Low N: 15)

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.10+
- GLM-4.6 API key from [Zhipu AI](https://open.bigmodel.cn/)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd hive-five
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your GLM_API_KEY
```

3. Start infrastructure services:
```bash
docker-compose up -d
```

4. Install Python dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

5. Run the system:
```bash
python main.py
```

## 📁 Project Structure

```
hive-five/
├── src/
│   ├── agents/          # Agent implementations
│   ├── models/          # Data models (Pydantic)
│   ├── services/        # Core services (Kafka, LLM, DB)
│   ├── api/             # FastAPI REST & WebSocket
│   ├── db/              # Database layer
│   ├── scenarios/       # Interaction scenarios
│   └── utils/           # Utilities
├── config/              # Configuration files
├── tests/               # Test suite
├── docs/                # Documentation
├── docker-compose.yml   # Infrastructure setup
├── requirements.txt     # Python dependencies
└── main.py             # Entry point
```

## 🛠️ Technology Stack

- **Language**: Python 3.10+ (asyncio)
- **Event Bus**: Apache Kafka
- **LLM**: GLM-4.6 (Zhipu AI)
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **API**: FastAPI
- **Containerization**: Docker

## 🎮 Usage

### Start a Scenario

```python
# Coming soon - scenario system
```

### Monitor via API

Access the Kafka UI at http://localhost:8080 to monitor message flow.

## 📊 Architecture

The system uses an event-driven architecture where agents communicate through Kafka topics:

- `agent.messages` - Inter-agent communication
- `agent.actions` - Action events (agree/disagree/propose)
- `agent.internal` - Internal state changes
- `system.control` - System-level commands

Each agent runs in an async event loop, processing incoming events based on their personality profile and making decisions via the GLM-4.6 LLM.

## 🧪 Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
isort src/
flake8 src/
```

## 📈 Roadmap

- [x] Phase 1: Project setup and infrastructure
- [ ] Phase 2: Core agent implementation
- [ ] Phase 3: Memory and decision systems
- [ ] Phase 4: Persistence and analytics
- [ ] Phase 5: Production polish
- [ ] Phase 6: Advanced features

## 📝 License

[Add your license here]

## 🤝 Contributing

Contributions are welcome! Please read CONTRIBUTING.md for details.

## 📧 Contact

[Add your contact information]
