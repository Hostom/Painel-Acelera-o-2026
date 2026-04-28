-- SCRIPT DE CRIAÇÃO DO BANCO PAINEL 220
-- Executar no SQL Editor do Supabase

-- 1. Tabelas de Apoio (Core)
CREATE TABLE bairros (
    id SERIAL PRIMARY KEY,
    nome TEXT UNIQUE NOT NULL,
    cidade TEXT DEFAULT 'Bento Gonçalves'
);

CREATE TABLE corretores (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT,
    ativo BOOLEAN DEFAULT TRUE
);

CREATE TABLE tipos_imovel (
    id SERIAL PRIMARY KEY,
    nome TEXT UNIQUE NOT NULL
);

-- 2. MSI (Matriz de Segmentação Imobiliária - Alugados)
CREATE TABLE msi_alugados (
    id SERIAL PRIMARY KEY,
    codigo_imovel TEXT,
    dia INTEGER,
    mes TEXT,
    ano INTEGER,
    locador TEXT,
    locatario TEXT,
    bairro_id INTEGER REFERENCES bairros(id),
    tipo_imovel_id INTEGER REFERENCES tipos_imovel(id),
    valor_aluguel DECIMAL(12,2),
    taxa_adm_percent DECIMAL(5,4),
    corretor_id INTEGER REFERENCES corretores(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Leads & FDL (Funil)
CREATE TABLE leads (
    id SERIAL PRIMARY KEY,
    nome TEXT,
    telefone TEXT,
    dia INTEGER,
    mes TEXT,
    ano INTEGER,
    -- Semanas de progressão (Sem1, Sem2, etc)
    lead_semana TEXT DEFAULT '',
    interacao_semana TEXT DEFAULT '',
    visita_semana TEXT DEFAULT '',
    condicao_semana TEXT DEFAULT '',
    alugado_semana TEXT DEFAULT '',
    bairro_id INTEGER REFERENCES bairros(id),
    corretor_id INTEGER REFERENCES corretores(id),
    midia TEXT,
    objecao TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Desocupações (Churn)
CREATE TABLE desocupacoes (
    id SERIAL PRIMARY KEY,
    codigo_sistema TEXT,
    mes TEXT,
    ano INTEGER,
    locatario TEXT,
    valor_aluguel DECIMAL(12,2),
    taxa_adm_percent DECIMAL(5,4),
    motivo TEXT,
    bairro_id INTEGER REFERENCES bairros(id)
);

-- 5. Metas & OKRs
CREATE TABLE metas_mensais (
    id SERIAL PRIMARY KEY,
    mes TEXT,
    ano INTEGER,
    meta_vgl_1 DECIMAL(12,2),
    meta_qtd_1 INTEGER,
    meta_capt_1 INTEGER,
    UNIQUE(mes, ano)
);

CREATE TABLE okrs (
    id SERIAL PRIMARY KEY,
    mes TEXT,
    ano INTEGER,
    objetivo TEXT,
    key_result TEXT,
    meta DECIMAL(12,2),
    semana_1 DECIMAL(12,2) DEFAULT 0,
    semana_2 DECIMAL(12,2) DEFAULT 0,
    semana_3 DECIMAL(12,2) DEFAULT 0,
    semana_4 DECIMAL(12,2) DEFAULT 0,
    semana_5 DECIMAL(12,2) DEFAULT 0
);

-- Habilitar RLS (Row Level Security) se necessário
-- ALTER TABLE msi_alugados ENABLE ROW LEVEL SECURITY;
