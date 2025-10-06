# Big Five Multi-Agent System - Complete Technical Specification

## 🎯 Project Overview

A sophisticated multi-agent simulation system where AI agents with distinct Big Five personality profiles interact in real-time through an event-driven architecture. Each agent represents a unique personality type and communicates asynchronously via Apache Kafka, creating a dynamic virtual social environment.

---

## 🧠 Core Concept

### What is This?
- **Multi-agent system**: 5+ autonomous AI agents running concurrently
- **Personality-driven**: Each agent has a distinct Big Five personality profile
- **Event-driven architecture**: Agents communicate via Kafka message bus
- **LLM-powered**: GLM-4.6 provides reasoning and decision-making
- **Social simulation**: Agents form relationships, develop moods, and interact naturally

### Why This Matters?
- Research tool for studying personality-based AI interactions
- Testing ground for multi-agent coordination
- Simulation environment for social dynamics
- Foundation for complex AI systems (games, simulations, virtual worlds)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Control Plane Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ FastAPI      │  │ WebSocket    │  │ Admin CLI    │      │
│  │ REST API     │  │ Real-time UI │  │ Management   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent Orchestration Layer                 │
│                                                               │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐│
│  │Agent 1 │  │Agent 2 │  │Agent 3 │  │Agent 4 │  │Agent 5 ││
│  │ Alex   │  │ Morgan │  │ Jordan │  │ Casey  │  │ Taylor ││
│  │Leader  │  │Analyst │  │Mediator│  │Creative│  │Pragmat.││
│  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘│
│       │           │           │           │           │      │
│     inbox       inbox       inbox       inbox       inbox    │
│       ▲           ▲           ▲           ▲           ▲      │
│       └───────────┴───────────┴───────────┴───────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Event Bus Layer (Kafka)                   │
│                                                               │
│  Topics:                                                      │
│  • agent.messages    - Inter-agent communication             │
│  • agent.actions     - Action events (agree/disagree/etc)    │
│  • agent.internal    - Internal state changes                │
│  • system.control    - System-level commands                 │
│                                                               │
│  Partitioning: By agent_id for ordered delivery              │
│  Retention: 7 days (configurable)                            │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    ▼                    ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│   Persistence Layer      │  │    External Services     │
│                          │  │                          │
│  ┌────────────────────┐  │  │  ┌────────────────────┐  │
│  │ PostgreSQL         │  │  │  │ GLM-4.6 API        │  │
│  │ - Conversation log │  │  │  │ (Zhipu AI)         │  │
│  │ - Agent memories   │  │  │  │                    │  │
│  │ - Relationships    │  │  │  │ - Reasoning engine │  │
│  └────────────────────┘  │  │  │ - Response gen.    │  │
│                          │  │  └────────────────────┘  │
│  ┌────────────────────┐  │  │                          │
│  │ Redis              │  │  │                          │
│  │ - Agent state      │  │  │                          │
│  │ - Active sessions  │  │  │                          │
│  │ - Rate limiting    │  │  │                          │
│  └────────────────────┘  │  │                          │
└──────────────────────────┘  └──────────────────────────┘
```

---

## 👥 The Big Five Personality Model

### Understanding the Traits

**1. Openness (O)** - Imagination & Creativity
- **High**: Creative, curious, open to new ideas, imaginative
- **Low**: Practical, conventional, prefers routine, concrete thinking

**2. Conscientiousness (C)** - Organization & Dependability  
- **High**: Organized, responsible, plans ahead, disciplined
- **Low**: Spontaneous, flexible, less concerned with rules

**3. Extraversion (E)** - Sociability & Energy
- **High**: Outgoing, energetic, talkative, seeks social interaction
- **Low**: Reserved, introspective, prefers solitude, thoughtful

**4. Agreeableness (A)** - Cooperation & Empathy
- **High**: Cooperative, compassionate, trusting, helpful
- **Low**: Competitive, skeptical, direct, challenges others

**5. Neuroticism (N)** - Emotional Stability (inverted)
- **High**: Anxious, moody, emotionally reactive, sensitive
- **Low**: Calm, stable, resilient, even-tempered

### The Five Agent Personalities

#### Agent 1: Alex - The Extroverted Leader
```yaml
personality:
  openness: 85
  conscientiousness: 80
  extraversion: 95      # ⭐ Dominant trait
  agreeableness: 60
  neuroticism: 20

behavioral_patterns:
  - Initiates conversations frequently
  - Takes charge in group discussions
  - Direct communication style
  - Confident decision-making
  - Motivates others to participate
```

#### Agent 2: Morgan - The Analytical Introvert
```yaml
personality:
  openness: 90
  conscientiousness: 85
  extraversion: 25      # ⭐ Low extraversion
  agreeableness: 50
  neuroticism: 45

behavioral_patterns:
  - Responds thoughtfully, not impulsively
  - Provides data-driven insights
  - Prefers one-on-one interactions
  - Detailed, precise communication
  - Observes before engaging
```

#### Agent 3: Jordan - The Agreeable Mediator
```yaml
personality:
  openness: 60
  conscientiousness: 75
  extraversion: 60
  agreeableness: 90     # ⭐ Dominant trait
  neuroticism: 25

behavioral_patterns:
  - Seeks consensus and harmony
  - Empathetic responses
  - Smooths conflicts
  - Supportive and encouraging
  - Considers all perspectives
```

#### Agent 4: Casey - The Creative Chaotic
```yaml
personality:
  openness: 95          # ⭐ Dominant trait
  conscientiousness: 30 # ⭐ Low structure
  extraversion: 80
  agreeableness: 40
  neuroticism: 70

behavioral_patterns:
  - Proposes unconventional ideas
  - Unpredictable responses
  - Emotionally expressive
  - Challenges conventions
  - Spontaneous and impulsive
```

#### Agent 5: Taylor - The Stable Pragmatist
```yaml
personality:
  openness: 30
  conscientiousness: 95  # ⭐ Dominant trait
  extraversion: 55
  agreeableness: 75
  neuroticism: 15        # ⭐ Very stable

behavioral_patterns:
  - Focuses on practical solutions
  - Reliable and consistent
  - Prefers proven methods
  - Calm under pressure
  - Detail-oriented responses
```

---

## 🔄 Event-Driven Communication Flow

### Event Types

```python
class EventType(Enum):
    # Social Events
    MESSAGE = "message"           # General conversation
    QUESTION = "question"         # Asking for information
    ANSWER = "answer"            # Responding to question
    
    # Action Events
    PROPOSE = "propose"          # Suggesting an idea/action
    AGREE = "agree"              # Supporting a proposal
    DISAGREE = "disagree"        # Opposing a proposal
    
    # Emotional Events
    EMOTION = "emotion"          # Expressing feeling
    SUPPORT = "support"          # Emotional support
    
    # System Events
    JOIN = "join"                # Agent enters conversation
    LEAVE = "leave"              # Agent exits conversation
```

### Event Structure

```json
{
  "id": "evt_1234567890",
  "type": "message",
  "source_id": "agent-1",
  "target_id": "all",
  "content": "What do you all think about implementing feature X?",
  "metadata": {
    "reasoning": "Taking initiative as group leader",
    "mood": {
      "valence": 0.7,
      "arousal": 0.6
    },
    "confidence": 0.85
  },
  "timestamp": "2025-01-15T10:30:45.123Z"
}
```

### Communication Patterns

**1. Broadcast Pattern**
```
Agent 1 → [Kafka Topic] → All Agents
         (target_id = "all")
```

**2. Direct Message Pattern**
```
Agent 1 → [Kafka Topic] → Agent 3
         (target_id = "agent-3")
```

**3. Group Discussion Pattern**
```
Agent 1: Initial message (broadcast)
    ↓
Agent 2: Thoughtful response
Agent 3: Agrees with Agent 2
Agent 4: Proposes alternative
Agent 1: Synthesizes discussion
    ↓
Consensus or continued debate
```

---

## 🧩 Core Components

### 1. Agent Architecture

```python
class Agent:
    """
    Core agent with personality-driven behavior
    """
    
    # Identity
    id: str                          # Unique identifier
    name: str                        # Human-readable name
    personality: BigFiveProfile      # Personality traits
    
    # Communication
    inbox: asyncio.Queue             # Incoming events (from Kafka)
    outbox: asyncio.Queue            # Outgoing events (to Kafka)
    
    # State
    memory: Memory                   # Long-term memory system
    mood: EmotionalState            # Current emotional state
    relationships: Dict[str, Rel]   # Social connections
    
    # Processing
    llm: GLMClient                  # LLM for reasoning
    decision_engine: DecisionEngine  # Response generation
    
    # Lifecycle
    async def start()               # Begin processing loop
    async def stop()                # Graceful shutdown
    async def _run()                # Main event loop
    async def _process_event()      # Handle incoming event
```

**Agent Event Processing Pipeline:**
```
Incoming Event
    ↓
1. Store in Memory
    ↓
2. Update Emotional State
    ↓
3. Update Relationship
    ↓
4. Should Respond? (personality-based)
    ↓
5. Build Context-Aware Prompt
    ↓
6. Call GLM-4.6 API
    ↓
7. Parse LLM Response
    ↓
8. Generate Event
    ↓
Outgoing Event → Kafka
```

### 2. Memory System

```python
class Memory:
    """
    Multi-tiered memory for agents
    """
    
    # Short-term memory (last 10-20 events)
    short_term: Deque[Event]
    
    # Working memory (current conversation context)
    working_memory: List[Event]
    
    # Long-term memory (PostgreSQL)
    # - Significant interactions
    # - Learned patterns
    # - Important facts about other agents
    
    async def add_event(event: Event)
    async def get_recent_context(n: int) -> str
    async def search_relevant(query: str) -> List[Event]
```

**Memory Retrieval Strategy:**
- **Recency**: Last N events always included
- **Relevance**: Semantic search for similar past interactions
- **Importance**: Emotionally significant events weighted higher

### 3. Decision Engine

```python
class DecisionEngine:
    """
    Translates personality + context into responses
    """
    
    def should_respond(
        event: Event,
        personality: BigFiveProfile
    ) -> bool:
        """
        Probability-based response decision
        
        Factors:
        - Extraversion: Higher = more likely to respond
        - Target type: Direct message = always respond
        - Relationship: Closer = more likely
        - Current mood: Positive = more engaged
        """
        
    async def generate_response(
        event: Event,
        context: MemoryContext,
        personality: BigFiveProfile
    ) -> Optional[Event]:
        """
        Creates personality-appropriate response
        
        Process:
        1. Build personality-aware prompt
        2. Include relevant context
        3. Call LLM
        4. Parse and validate response
        5. Return Event or None
        """
```

### 4. Emotional State System

```python
class EmotionalState:
    """
    Two-dimensional emotion model
    """
    valence: float    # -1.0 (negative) to +1.0 (positive)
    arousal: float    # 0.0 (calm) to 1.0 (excited)
    
    def update(self, event: Event, personality: BigFiveProfile):
        """
        Update mood based on event and personality
        
        Rules:
        - Agreement → +valence
        - Disagreement → -valence (modulated by Neuroticism)
        - Exciting topics → +arousal (modulated by Extraversion)
        - Mood decay over time (return to baseline)
        - Neuroticism affects stability
        """
```

**Mood Affects Behavior:**
- **Positive Valence**: More agreeable, creative responses
- **Negative Valence**: More critical, withdrawn
- **High Arousal**: More exclamation marks, faster responses
- **Low Arousal**: More measured, calm responses

### 5. Relationship System

```python
class Relationship:
    """
    Dynamic relationships between agents
    """
    agent_id: str
    trust: float           # 0.0 to 1.0
    familiarity: float     # 0.0 to 1.0
    affinity: float        # -1.0 to 1.0
    interaction_count: int
    last_contact: datetime
    
    def update(self, event: Event):
        """
        Evolve relationship over time
        
        - Positive interactions → +trust, +affinity
        - Frequent interactions → +familiarity
        - Disagreements → -affinity (but not always bad!)
        - Time decay if no interaction
        """
```

---

## 🔌 Technology Stack

### Core Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.10+ | Core implementation |
| **Concurrency** | asyncio | Async agent processing |
| **Event Bus** | Apache Kafka | Message streaming |
| **LLM** | GLM-4.6 (Zhipu AI) | Reasoning & generation |
| **Database** | PostgreSQL 16 | Persistent storage |
| **Cache** | Redis 7 | State & sessions |
| **API** | FastAPI | REST & WebSocket |
| **Frontend** | React/Vue (future) | Visualization UI |

### Key Python Libraries

```python
# Core async & HTTP
asyncio              # Concurrency primitives
aiohttp              # Async HTTP client for LLM API

# Kafka
confluent-kafka      # Kafka producer/consumer

# Data validation
pydantic             # Schema validation & parsing

# Templating
jinja2               # Prompt template engine

# Database
sqlalchemy           # ORM
psycopg2-binary      # PostgreSQL driver
redis                # Redis client

# API
fastapi              # Web framework
uvicorn              # ASGI server
websockets           # Real-time updates

# Config & utilities
python-dotenv        # Environment variables
pyyaml               # YAML parsing
python-dateutil      # Date/time utilities
```

### Infrastructure (Docker)

```yaml
services:
  zookeeper:    # Kafka coordination
  kafka:        # Message broker
  postgres:     # Persistent storage
  redis:        # In-memory cache
  
  # Future additions:
  # grafana:    # Metrics visualization
  # prometheus: # Metrics collection
```

---

## 💬 LLM Integration (GLM-4.6)

### Why GLM-4.6?
- **Chinese AI model** from Zhipu AI (智谱AI)
- **Multilingual support** (English + Turkish for your use case)
- **Cost-effective** compared to GPT-4
- **Fast inference** (important for real-time interaction)
- **Good reasoning** for personality-based responses

### Prompt Engineering Strategy

**1. System Prompt Template**
```
You are {agent_name} with the following personality:
- Openness: {openness}/100
- Conscientiousness: {conscientiousness}/100
- Extraversion: {extraversion}/100
- Agreeableness: {agreeableness}/100
- Neuroticism: {neuroticism}/100

Current mood: Valence {valence}, Arousal {arousal}

[Recent context: Last 5 interactions]

Event received:
Type: {event_type}
From: {source_agent}
Content: "{content}"

Respond authentically based on your personality.
Your extraversion affects engagement eagerness.
Your agreeableness affects your tone.
Your neuroticism affects emotional reactions.

Return JSON only:
{
  "action": "message|agree|disagree|propose|ignore",
  "target": "agent_id or all",
  "content": "your response",
  "reasoning": "internal thought"
}
```

**2. Response Parsing**
```python
def parse_llm_response(text: str) -> Optional[Event]:
    """
    Extract JSON from LLM response
    Handle cases:
    - Valid JSON
    - JSON wrapped in markdown code blocks
    - Partial JSON
    - Non-JSON responses (fallback)
    """
```

**3. Error Handling**
- Timeout: Retry with exponential backoff
- Rate limit: Queue requests
- Invalid response: Use fallback simple response
- API error: Log and skip response

### Token Management
- **Context window**: ~8K tokens (GLM-4-Flash)
- **Prompt budget**: ~2K tokens (personality + context)
- **Response limit**: ~1K tokens
- **Total**: ~3K tokens per interaction

---

## 📊 Data Models

### PostgreSQL Schema

```sql
-- Agents table
CREATE TABLE agents (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    openness INT CHECK (openness BETWEEN 0 AND 100),
    conscientiousness INT CHECK (conscientiousness BETWEEN 0 AND 100),
    extraversion INT CHECK (extraversion BETWEEN 0 AND 100),
    agreeableness INT CHECK (agreeableness BETWEEN 0 AND 100),
    neuroticism INT CHECK (neuroticism BETWEEN 0 AND 100),
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Events/Messages table
CREATE TABLE events (
    id VARCHAR(50) PRIMARY KEY,
    event_type VARCHAR(20) NOT NULL,
    source_id VARCHAR(50) REFERENCES agents(id),
    target_id VARCHAR(50),
    content TEXT NOT NULL,
    metadata JSONB,
    timestamp TIMESTAMP NOT NULL,
    INDEX idx_timestamp (timestamp),
    INDEX idx_source (source_id),
    INDEX idx_target (target_id)
);

-- Relationships table
CREATE TABLE relationships (
    agent_id VARCHAR(50) REFERENCES agents(id),
    other_agent_id VARCHAR(50) REFERENCES agents(id),
    trust FLOAT CHECK (trust BETWEEN 0 AND 1),
    familiarity FLOAT CHECK (familiarity BETWEEN 0 AND 1),
    affinity FLOAT CHECK (affinity BETWEEN -1 AND 1),
    interaction_count INT DEFAULT 0,
    last_contact TIMESTAMP,
    PRIMARY KEY (agent_id, other_agent_id)
);

-- Emotional states (time-series)
CREATE TABLE emotional_states (
    agent_id VARCHAR(50) REFERENCES agents(id),
    valence FLOAT CHECK (valence BETWEEN -1 AND 1),
    arousal FLOAT CHECK (arousal BETWEEN 0 AND 1),
    timestamp TIMESTAMP NOT NULL,
    PRIMARY KEY (agent_id, timestamp)
);
```

### Redis Data Structures

```python
# Active agent states (TTL: 1 hour)
redis_key = f"agent:{agent_id}:state"
redis_value = {
    "status": "active|idle|processing",
    "last_activity": timestamp,
    "current_mood": {"valence": 0.5, "arousal": 0.3},
    "active_conversations": ["conv_id_1", "conv_id_2"]
}

# Rate limiting (sliding window)
redis_key = f"ratelimit:{agent_id}:{minute}"
redis_value = counter  # Number of events in this minute
```

---

## 🎬 Scenarios & Interactions

### Scenario 1: Team Meeting

```yaml
name: "Quarterly Planning Meeting"
description: "Discuss strategy for next quarter"

trigger:
  type: message
  source: system
  target: all
  content: "Let's discuss our strategy for next quarter. What are your thoughts?"

expected_behaviors:
  alex:
    - Takes charge immediately
    - Directs conversation flow
    - Asks for input from each agent
  
  morgan:
    - Provides data-driven analysis
    - Points out potential risks
    - Responds when directly addressed
  
  jordan:
    - Seeks consensus
    - Supports others' ideas
    - Smooths disagreements
  
  casey:
    - Proposes unconventional approaches
    - Challenges assumptions
    - Brings creative energy
  
  taylor:
    - Focuses on practical execution
    - Asks about timelines and resources
    - Grounds discussion in reality

metrics:
  - Total messages exchanged
  - Response latency per agent
  - Agreement/disagreement ratio
  - Conversation convergence time
```

### Scenario 2: Crisis Response

```yaml
name: "Production System Down"
description: "Urgent technical crisis requiring fast coordination"

trigger:
  type: message
  source: system
  target: all
  content: "URGENT: Production server is down. Customer data at risk!"

expected_behaviors:
  alex:
    - Takes immediate control
    - Assigns tasks quickly
    - High arousal, decisive
  
  morgan:
    - Analyzes root cause
    - Provides technical details
    - Stays calm (low neuroticism)
  
  jordan:
    - Manages team stress
    - Coordinates communication
    - Ensures everyone's on same page
  
  casey:
    - High emotional response (high neuroticism)
    - Proposes creative workarounds
    - May need calming
  
  taylor:
    - Follows established procedures
    - Documents everything
    - Implements fix methodically

metrics:
  - Time to first response
  - Stress indicators (arousal levels)
  - Decision quality under pressure
  - Team coordination effectiveness
```

### Scenario 3: Creative Brainstorm

```yaml
name: "Product Innovation Session"
description: "Generate new feature ideas"

trigger:
  type: message
  source: system
  target: all
  content: "We need fresh ideas for improving user engagement. Think outside the box!"

expected_behaviors:
  alex:
    - Energizes the group
    - Builds on others' ideas
    - Maintains momentum
  
  morgan:
    - Evaluates feasibility
    - Asks clarifying questions
    - Provides technical constraints
  
  jordan:
    - Encourages participation
    - Combines different perspectives
    - Finds common ground
  
  casey:
    - Generates wild ideas
    - Challenges conventions
    - Most active participant
  
  taylor:
    - Questions practicality
    - Concerned with implementation
    - May resist radical changes

metrics:
  - Unique ideas generated
  - Idea diversity (novelty)
  - Participation balance
  - Convergence on final concepts
```

---

## 📈 Metrics & Analytics

### Agent-Level Metrics

```python
class AgentMetrics:
    # Activity
    messages_sent: int
    messages_received: int
    response_rate: float  # % of received messages responded to
    initiation_rate: float  # % of self-initiated messages
    
    # Social
    unique_interactions: int  # Number of different agents interacted with
    avg_relationship_strength: float
    
    # Emotional
    mood_variance: float  # Emotional stability
    avg_valence: float
    avg_arousal: float
    
    # Personality alignment
    behavior_consistency: float  # How well actions match personality
```

### System-Level Metrics

```python
class SystemMetrics:
    # Throughput
    events_per_second: float
    kafka_lag: int  # Consumer lag
    
    # Interaction quality
    conversation_threads: int  # Active discussions
    avg_thread_length: float
    response_time_p50: float
    response_time_p95: float
    
    # Diversity
    topic_diversity: float  # Shannon entropy of topics
    interaction_network_density: float
    
    # LLM usage
    llm_calls_per_minute: int
    llm_token_usage: int
    llm_latency_avg: float
```

### Visualization Ideas

1. **Real-time Network Graph**
   - Nodes: Agents
   - Edges: Active conversations
   - Edge weight: Relationship strength
   - Node color: Current mood

2. **Timeline View**
   - Chronological event stream
   - Color-coded by event type
   - Filterable by agent

3. **Personality Radar Charts**
   - Big Five traits visualization
   - Compare across agents

4. **Mood Tracking**
   - Time-series plot
   - Valence & arousal over time
   - Per-agent or aggregate

---

## 🚀 Deployment Strategy

### Development Environment

```bash
# Local development setup
docker-compose up -d kafka postgres redis
export GLM_API_KEY="your-key"
python main.py
```

### Production Considerations

**1. Scaling**
- Run multiple agent instances across servers
- Kafka partitioning ensures agent affinity
- PostgreSQL read replicas for analytics

**2. Reliability**
- Kafka replication factor: 3
- PostgreSQL backup & replication
- Redis persistence (AOF + RDB)
- Agent process supervision (systemd/supervisor)

**3. Monitoring**
- Prometheus metrics export
- Grafana dashboards
- ELK stack for log aggregation
- Alert on agent failures, high latency

**4. Security**
- GLM API key rotation
- Kafka SSL/SASL authentication
- PostgreSQL SSL connections
- Rate limiting per agent

---

## 🎯 Development Roadmap

### Phase 1: MVP (2-3 weeks)
- ✅ Agent base class with personality
- ✅ Kafka event bus integration
- ✅ GLM-4.6 client
- ✅ Basic memory system
- ✅ 5 agents with distinct personalities
- ✅ Simple scenario trigger

**Deliverable**: Agents can hold basic conversations

### Phase 2: Enhanced Intelligence (2 weeks)
- Advanced memory (semantic search)
- Relationship dynamics
- Emotional state evolution
- Decision engine improvements
- Scenario library

**Deliverable**: Natural, personality-driven interactions

### Phase 3: Persistence & Analytics (2 weeks)
- PostgreSQL integration
- Conversation history
- Metrics collection
- Basic dashboard
- Export capabilities

**Deliverable**: Full data persistence and insights

### Phase 4: Production Polish (2 weeks)
- Error handling & retry logic
- Monitoring & alerting
- Performance optimization
- API for external control
- Documentation

**Deliverable**: Production-ready system

### Phase 5: Advanced Features (3-4 weeks)
- Multi-modal communication (future)
- Learning from interactions
- Dynamic personality evolution
- Complex scenario engine
- Advanced visualization

**Deliverable**: Research-grade platform

---

## 🔬 Research Questions

This system enables exploration of:

1. **Personality Impact**: How much do Big Five traits actually influence conversation patterns?

2. **Emergent Behavior**: Do agents form cliques? Leader-follower dynamics?

3. **Consensus Formation**: How do different personality mixes affect decision-making speed and quality?

4. **Emotional Contagion**: Do moods spread between agents?

5. **Relationship Evolution**: Can agents form meaningful "friendships"?

6. **LLM Consistency**: Does GLM-4.6 maintain personality across conversations?

---

## 📚 Key Design Decisions

### Why Async Python?
- Natural fit for I/O-bound operations (LLM API calls)
- Easy to reason about agent concurrency
- Rich ecosystem for AI/ML tasks

### Why Kafka over RabbitMQ?
- Better for event sourcing (persistent log)
- Can replay entire conversation history
- Scales horizontally more easily
- Built-in partitioning strategy

### Why Not Multi-Threading?
- Python GIL makes true parallelism difficult
- Async provides sufficient concurrency for our scale
- Easier debugging than threads

### Why GLM-4.6?
- Cost-effective
- Good multilingual support
- Fast enough for real-time
- Accessible API

---

## 🛠️ Implementation Tips

### 1. Start Simple
Don't build everything at once. Start with:
- 2 agents
- 1 scenario
- No persistence
- Basic personalities

Then iterate.

### 2. Debug with Logging
Every agent should log:
- Events received
- Decision rationale
- Mood changes
- Response generated

### 3. Test Personalities Individually
Before multi-agent testing, verify each personality behaves as expected in isolation.

### 4. Monitor LLM Costs
Track token usage. GLM-4.6 is cheap but can add up with many agents.

### 5. Handle Failures Gracefully
- LLM timeout? Skip response.
- Kafka down? Queue locally temporarily.
- Agent crash? Restart from last known state.

---

## 🎓 Learning Resources

- **Big Five Personality**: Research papers on OCEAN model
- **Multi-Agent Systems**: "Multiagent Systems" by Wooldridge
- **Event-Driven Architecture**: Martin Fowler's articles
- **Kafka**: Confluent documentation
- **LLM Prompt Engineering**: OpenAI & Anthropic guides

---

## 🤝 Contributing

Future areas for contribution:
- New personality profiles
- Additional scenarios
- Visualization improvements
- Alternative LLM backends
- Performance optimizations
- Research experiments

---

## 📝 Summary

This is a **research-grade multi-agent system** where:
- 5 AI agents with distinct Big Five personalities
- Communicate asynchronously via Kafka
- Make decisions via GLM-4.6 LLM
- Develop relationships and emotional states
- Form a dynamic social simulation

**Perfect for**:
- Understanding personality-driven AI behavior
- Testing multi-agent coordination
- Simulating social dynamics
- Building toward complex AI systems

**Technologies**: Python, asyncio, Kafka, GLM-4.6, PostgreSQL, Redis

**Timeline**: 8-12 weeks from concept to production-ready

The system is designed to be extensible, observable, and scientifically rigorous while remaining practical to implement and deploy.