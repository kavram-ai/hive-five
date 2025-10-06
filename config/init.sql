-- Initialize database schema for Hive Five

-- Agents table
CREATE TABLE IF NOT EXISTS agents (
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
CREATE TABLE IF NOT EXISTS events (
    id VARCHAR(50) PRIMARY KEY,
    event_type VARCHAR(20) NOT NULL,
    source_id VARCHAR(50) REFERENCES agents(id),
    target_id VARCHAR(50),
    content TEXT NOT NULL,
    metadata JSONB,
    timestamp TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_source ON events(source_id);
CREATE INDEX IF NOT EXISTS idx_events_target ON events(target_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);

-- Relationships table
CREATE TABLE IF NOT EXISTS relationships (
    agent_id VARCHAR(50) REFERENCES agents(id),
    other_agent_id VARCHAR(50) REFERENCES agents(id),
    trust FLOAT CHECK (trust BETWEEN 0 AND 1) DEFAULT 0.5,
    familiarity FLOAT CHECK (familiarity BETWEEN 0 AND 1) DEFAULT 0.0,
    affinity FLOAT CHECK (affinity BETWEEN -1 AND 1) DEFAULT 0.0,
    interaction_count INT DEFAULT 0,
    last_contact TIMESTAMP,
    PRIMARY KEY (agent_id, other_agent_id)
);

-- Emotional states (time-series)
CREATE TABLE IF NOT EXISTS emotional_states (
    agent_id VARCHAR(50) REFERENCES agents(id),
    valence FLOAT CHECK (valence BETWEEN -1 AND 1) DEFAULT 0.0,
    arousal FLOAT CHECK (arousal BETWEEN 0 AND 1) DEFAULT 0.5,
    timestamp TIMESTAMP NOT NULL,
    PRIMARY KEY (agent_id, timestamp)
);

CREATE INDEX IF NOT EXISTS idx_emotional_states_agent ON emotional_states(agent_id);
CREATE INDEX IF NOT EXISTS idx_emotional_states_timestamp ON emotional_states(timestamp);

-- Insert initial agents
INSERT INTO agents (id, name, openness, conscientiousness, extraversion, agreeableness, neuroticism)
VALUES
    ('agent-1', 'Alex', 85, 80, 95, 60, 20),
    ('agent-2', 'Morgan', 90, 85, 25, 50, 45),
    ('agent-3', 'Jordan', 60, 75, 60, 90, 25),
    ('agent-4', 'Casey', 95, 30, 80, 40, 70),
    ('agent-5', 'Taylor', 30, 95, 55, 75, 15)
ON CONFLICT (id) DO NOTHING;

-- Initialize relationships (all agents start neutral)
INSERT INTO relationships (agent_id, other_agent_id)
SELECT a1.id, a2.id
FROM agents a1
CROSS JOIN agents a2
WHERE a1.id != a2.id
ON CONFLICT (agent_id, other_agent_id) DO NOTHING;
