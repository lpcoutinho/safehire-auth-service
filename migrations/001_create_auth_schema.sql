-- Migration 001: Create auth_schema and usuarios table
-- Uso: psql -U user -d safehire_auth -f migrations/001_create_auth_schema.sql

CREATE SCHEMA IF NOT EXISTS auth_schema;

CREATE TABLE IF NOT EXISTS auth_schema.usuarios (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome        VARCHAR(255) NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    senha_hash  TEXT NOT NULL,
    tipo        VARCHAR(20) NOT NULL CHECK (tipo IN ('candidato', 'recrutador', 'admin')),
    ativo       BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em   TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_usuarios_email ON auth_schema.usuarios (email);
CREATE INDEX IF NOT EXISTS idx_usuarios_ativo ON auth_schema.usuarios (ativo);
