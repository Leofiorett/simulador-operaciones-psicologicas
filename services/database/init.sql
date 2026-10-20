-- Simulador de Operaciones Psicologicas (SOP) - schema inicial

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    role VARCHAR(16) NOT NULL DEFAULT 'alumno' CHECK (role IN ('instructor','alumno')),
    display_name VARCHAR(120),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS module_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    module_slug VARCHAR(64) NOT NULL,
    quiz_score INTEGER NOT NULL DEFAULT 0,
    quiz_total INTEGER NOT NULL DEFAULT 0,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    attempts INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (user_id, module_slug)
);

CREATE TABLE IF NOT EXISTS exercises (
    id VARCHAR(32) PRIMARY KEY,
    type VARCHAR(24) NOT NULL CHECK (type IN ('doctrina','planificacion','simulacion','defensa')),
    name TEXT NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'created'
        CHECK (status IN ('created','running','completed','stopped','timeout')),
    authorized_by VARCHAR(120),
    owner_username VARCHAR(64),
    scenario_code VARCHAR(48),
    config JSONB NOT NULL DEFAULT '{}'::jsonb,
    results JSONB,
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    timeout_hours INTEGER NOT NULL DEFAULT 24,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS exercise_events (
    id BIGSERIAL PRIMARY KEY,
    exercise_id VARCHAR(32) REFERENCES exercises(id) ON DELETE CASCADE,
    ts TIMESTAMPTZ DEFAULT now(),
    event_type VARCHAR(48) NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS campaigns (
    id SERIAL PRIMARY KEY,
    exercise_id VARCHAR(32) REFERENCES exercises(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    scenario_code VARCHAR(48) NOT NULL,
    config JSONB NOT NULL,
    created_by VARCHAR(64),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS simulation_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    scenario_code VARCHAR(48) NOT NULL,
    seed BIGINT,
    metrics JSONB NOT NULL,
    series JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

INSERT INTO users (username, password_hash, role, display_name)
VALUES ('instructor', 'seed-instructor', 'instructor', 'Instructor Responsable'),
       ('alumno', 'seed-alumno', 'alumno', 'Alumno Unidad')
ON CONFLICT (username) DO NOTHING;
