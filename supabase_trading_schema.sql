-- ============================================================
-- ARIA Trading Bot — Supabase Schema
-- Run this in your Supabase SQL Editor
-- ============================================================

CREATE TABLE IF NOT EXISTS portfolios (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     TEXT UNIQUE NOT NULL DEFAULT 'default_user',
    balance     NUMERIC(15,2) DEFAULT 10000.00,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS portfolio_holdings (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE,
    symbol      TEXT NOT NULL,
    quantity    NUMERIC(15,4) DEFAULT 0,
    avg_price   NUMERIC(15,2) DEFAULT 0,
    UNIQUE(portfolio_id, symbol)
);

CREATE TABLE IF NOT EXISTS trades (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE,
    symbol      TEXT NOT NULL,
    action      TEXT NOT NULL CHECK (action IN ('BUY', 'SELL')),
    quantity    NUMERIC(15,4) NOT NULL,
    price       NUMERIC(15,2) NOT NULL,
    total_value NUMERIC(15,2) NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Seed initial virtual portfolio
INSERT INTO portfolios (user_id, balance) VALUES ('default_user', 10000.00) ON CONFLICT DO NOTHING;
