-- ============================================================
-- Marketing AI Agent Platform — Supabase Schema
-- Run this in your Supabase SQL Editor
-- ============================================================

-- Leads table
CREATE TABLE IF NOT EXISTS leads (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    email       TEXT,
    phone       TEXT,
    company     TEXT,
    industry    TEXT,
    notes       TEXT,
    score       INTEGER DEFAULT 0,
    grade       TEXT DEFAULT 'C',
    status      TEXT DEFAULT 'new' CHECK (status IN ('new','contacted','qualified','proposal','closed_won','closed_lost')),
    ai_notes    TEXT,
    recommended_action TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Campaigns table
CREATE TABLE IF NOT EXISTS campaigns (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    channel         TEXT NOT NULL CHECK (channel IN ('social','email','ads','sms','whatsapp')),
    budget          NUMERIC(10,2),
    goal            TEXT,
    target_audience TEXT,
    status          TEXT DEFAULT 'draft' CHECK (status IN ('active','paused','completed','draft')),
    impressions     BIGINT DEFAULT 0,
    clicks          BIGINT DEFAULT 0,
    conversions     BIGINT DEFAULT 0,
    spend           NUMERIC(10,2) DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Content items table
CREATE TABLE IF NOT EXISTS content_items (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type        TEXT NOT NULL,
    body        TEXT NOT NULL,
    platform    TEXT,
    topic       TEXT,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
    word_count  INTEGER DEFAULT 0,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Analytics events table
CREATE TABLE IF NOT EXISTS analytics_events (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    event       TEXT NOT NULL CHECK (event IN ('impression','click','conversion','spend')),
    value       NUMERIC(10,4) DEFAULT 1.0,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Chat messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id  TEXT NOT NULL,
    role        TEXT NOT NULL CHECK (role IN ('user','assistant')),
    content     TEXT NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Row Level Security (disable for dev, enable for prod) ───────────────────
ALTER TABLE leads            DISABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns        DISABLE ROW LEVEL SECURITY;
ALTER TABLE content_items    DISABLE ROW LEVEL SECURITY;
ALTER TABLE analytics_events DISABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages     DISABLE ROW LEVEL SECURITY;

-- ─── Indexes ─────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_analytics_campaign ON analytics_events(campaign_id);
CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_content_type ON content_items(type);

-- ─── Sample Seed Data ─────────────────────────────────────────────────────────
INSERT INTO campaigns (name, channel, budget, goal, status, impressions, clicks, conversions, spend) VALUES
    ('Summer Brand Awareness', 'social', 5000, 'Reach 100K users', 'active', 84500, 2340, 89, 1200),
    ('Email Nurture Sequence', 'email', 800, 'Re-engage cold leads', 'active', 3200, 512, 67, 320),
    ('Google Search Campaign', 'ads', 10000, 'Drive product signups', 'active', 196800, 6971, 156, 2730),
    ('WhatsApp Re-engagement', 'whatsapp', 200, 'Win-back churned users', 'paused', 0, 0, 0, 0),
    ('LinkedIn B2B Outreach', 'ads', 3000, 'Generate enterprise leads', 'draft', 0, 0, 0, 0)
ON CONFLICT DO NOTHING;

INSERT INTO leads (name, email, company, industry, score, grade, status) VALUES
    ('Priya Sharma', 'priya@techcorp.in', 'TechCorp', 'SaaS', 87, 'A', 'qualified'),
    ('Raj Mehta', 'raj@startup.io', 'StartupIO', 'E-commerce', 72, 'B', 'contacted'),
    ('Anika Singh', 'anika@fintech.co', 'FinTech Ltd', 'Finance', 91, 'A', 'proposal'),
    ('Dev Patel', 'dev@agency.com', 'Creative Agency', 'Marketing', 58, 'C', 'new'),
    ('Meera Joshi', 'meera@retail.in', 'RetailPlus', 'Retail', 65, 'B', 'new')
ON CONFLICT DO NOTHING;
