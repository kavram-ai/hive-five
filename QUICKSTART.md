# Hive Five - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Check Prerequisites

```bash
# Docker installed?
docker --version
docker-compose --version

# Python 3.10+ installed?
python --version
```

### 2. Get API Key

1. Go to [Zhipu AI](https://open.bigmodel.cn/)
2. Create account (free)
3. Get your API key

### 3. Setup Project

```bash
# Clone repository (or already downloaded)
cd hive-five

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env and add your API key
# GLM_API_KEY=your-api-key-here
```

### 4. Start Infrastructure

```bash
# Start Kafka, PostgreSQL, Redis
docker-compose up -d

# Wait for services to be ready (about 30 seconds)
docker-compose ps

# Check Kafka UI (optional)
# http://localhost:8080
```

### 5. Run the System

```bash
# Start the main program
python main.py
```

## 🎭 What You'll See

```
🐝 Starting Hive Five Multi-Agent System
Initializing services...
✓ Services initialized
Creating agents...
✓ Created 5 agents
  - Alex: The Extroverted Leader
  - Morgan: The Analytical Introvert
  - Jordan: The Agreeable Mediator
  - Casey: The Creative Chaotic
  - Taylor: The Stable Pragmatist
Starting agents...
✓ All agents started
✓ Initial trigger sent
✅ System ready - agents are interacting!

[10:30:45] [Alex] → all: I totally agree! I think communication is key...
[10:30:47] [Morgan] → all: From an analytical perspective, I'd add that...
[10:30:49] [Jordan] → all: I appreciate both perspectives. What if we...
[10:30:51] [Casey] → all: Wait, but what if we tried something completely different?
[10:30:53] [Taylor] → all: Let's focus on practical implementation...
```

## 🎯 Initial Observations

### Alex (Extroverted Leader)
- Usually the first to respond
- Tries to involve everyone in discussion
- Energetic, enthusiastic responses

### Morgan (Analytical Introvert)
- Speaks less but with depth
- Data and logic focused
- Thoughtful, longer responses

### Jordan (Agreeable Mediator)
- Validates everyone's opinion
- Smooths conflicts
- "We're all right" approach

### Casey (Creative Chaotic)
- Unexpected suggestions
- Emotional reactions
- Unconventional ideas

### Taylor (Stable Pragmatist)
- Focused on practical solutions
- Calm and consistent
- "How will we do this?" questions

## 🛠️ Troubleshooting

### Kafka connection error
```bash
# Check if Kafka is running
docker-compose ps

# Check logs
docker-compose logs kafka

# Restart
docker-compose restart kafka
```

### GLM API error
```bash
# Make sure API key is correct
cat .env | grep GLM_API_KEY

# Check internet connection
curl https://open.bigmodel.cn/
```

### Agents not talking
```bash
# Check logs in detail
# Change LOG_LEVEL=DEBUG in main.py

# Check Kafka topics
# http://localhost:8080 (Kafka UI)
```

## 📊 Monitoring

### Kafka UI (Recommended)
- URL: http://localhost:8080
- Topic: `agent.messages` - See all messages
- Consumer: Check lag

### Logs
```bash
# Main console - Agent messages
# Each message in format:
# [Time] [Agent Name] → target: message content
```

### Docker Services
```bash
# Status of all services
docker-compose ps

# Kafka logs
docker-compose logs -f kafka

# PostgreSQL logs
docker-compose logs -f postgres
```

## 🎮 Experiments

### 1. Personality Consistency
Observe whether agents maintain their personalities over time.

### 2. Conversation Dynamics
- Who talks the most?
- Who initiates, who follows?
- Who's the natural leader?

### 3. Disagreement Management
- What happens when Alex and Casey disagree?
- How does Jordan mediate?
- How does the group reach consensus?

### 4. Creativity vs Pragmatism
- Are Casey's ideas accepted?
- How does Taylor make them practical?

## ⚡ Advanced Usage

### Start Your Own Scenario

Modify the `_send_initial_trigger` function in `main.py`:

```python
initial_event = create_system_event(
    content="Write your own scenario here!",
    target_id="all"
)
```

### Adjust Personalities

Change trait values in `src/agents/agent_factory.py`:

```python
# Example: Make Alex less extroverted
extraversion=70,  # instead of 95
```

### Add New Agent

```python
# Add a new agent in agent_factory.py
new_agent_profile = AgentProfile(
    id="agent-6",
    name="YourAgent",
    personality=BigFiveProfile(
        openness=50,
        conscientiousness=50,
        extraversion=50,
        agreeableness=50,
        neuroticism=50
    )
)
```

## 🛑 Stopping

```bash
# Stop the program with Ctrl+C

# Stop infrastructure
docker-compose down

# Delete all data (careful!)
docker-compose down -v
```

## 📚 More Information

- **Detailed TODO**: `TODO.md` - Future features
- **Architecture**: Full architecture in spec file
- **Models**: `src/models/` - All data models
- **Agent**: `src/agents/base_agent.py` - Agent implementation

## 💡 Tips

1. **Start small**: 2-3 agents are enough for initial tests
2. **Watch logs**: Critical for understanding what's happening
3. **Use Kafka UI**: Visualize message flow
4. **Monitor token usage**: GLM API calls cost money
5. **Be patient**: LLM responses can take 2-5 seconds

## 🎉 Successful Setup!

Now your 5 AI agents are talking to each other! 🎭

If you have issues:
- Check "Known Issues" section in TODO.md
- Open GitHub Issues
- Share logs

Have fun! 🚀
