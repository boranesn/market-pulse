CREATE TABLE IF NOT EXISTS snapshots (
    ticker VARCHAR,
    fetched_at TIMESTAMPTZ,
    close_price DECIMAL(10,4),
    volume BIGINT,
    pe_ratio FLOAT,
    sentiment_score FLOAT,
    anomalies JSON,
    raw JSON,
    PRIMARY KEY (ticker, fetched_at)
);

CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR NOT NULL,
    condition_expr VARCHAR NOT NULL,
    notify_via JSON,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_triggered TIMESTAMPTZ,
    trigger_count INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR NOT NULL,
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    depth VARCHAR,
    content JSON
);
