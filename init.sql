-- ============================================================
-- SCRIPT DE BANCO DE DADOS POSTGRESQL - GESTÃO DE AGENDAMENTOS
-- ============================================================

-- 0. Limpeza prévia (Opcional - Remove tabelas antigas se existirem) 🧹
DROP TABLE IF EXISTS receitas CASCADE;
DROP TABLE IF EXISTS agendamentos CASCADE;
DROP TABLE IF EXISTS servicos CASCADE;


-- 1. TABELA DE SERVIÇOS ✂️
-- Armazena o catálogo de serviços prestados e seus respectivos valores.
CREATE TABLE IF NOT EXISTS servicos (
    id SERIAL PRIMARY KEY,                          -- Identificador único auto-incrementado
    nome VARCHAR(100) NOT NULL UNIQUE,              -- Nome do serviço (ex: Manicure Tradicional)
    preco NUMERIC(10, 2) NOT NULL                   -- Valor cobrado pelo serviço
);


-- 2. TABELA DE AGENDAMENTOS 📅
-- Guarda os compromissos agendados pelos clientes para datas e horas específicas.
CREATE TABLE IF NOT EXISTS agendamentos (
    id SERIAL PRIMARY KEY,                          -- Identificador único do agendamento
    cliente_nome VARCHAR(255) NOT NULL,             -- Nome do cliente
    cliente_telefone VARCHAR(20) NOT NULL,          -- Telefone/WhatsApp de contato
    servico_id INT REFERENCES servicos(id) ON DELETE CASCADE, -- Vínculo com a tabela de serviços
    data_agendamento DATE NOT NULL,                 -- Data do atendimento (YYYY-MM-DD)
    hora_agendamento TIME NOT NULL,                 -- Horário do atendimento (HH:MM:SS)
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Registra quando a reserva foi feita

    -- Regra de negócio: Impede que o mesmo serviço seja marcado na mesma data e horário 🔒
    CONSTRAINT unique_servico_horario UNIQUE (servico_id, data_agendamento, hora_agendamento)
);


-- 3. TABELA DE RECEITAS (FINANCEIRO) 💰
-- Registra os pagamentos, históricos de vendas e caminhos dos comprovantes anexados.
CREATE TABLE IF NOT EXISTS receitas (
    id SERIAL PRIMARY KEY,                          -- Identificador único do registro financeiro
    cliente_nome VARCHAR(255) NOT NULL,             -- Nome do cliente associado ao pagamento
    data_agendamento DATE NOT NULL,                 -- Data associada ao atendimento
    hora_agendamento TIME NOT NULL,                 -- Hora associada ao atendimento
    descricao TEXT NOT NULL,                        -- Detalhamento da receita (ex: Serviço de Manicure)
    valor NUMERIC(10, 2) NOT NULL,                  -- Valor pago pelo cliente
    comprovante_nome VARCHAR(255),                  -- Caminho/Nome do arquivo de comprovante salvo
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Data e hora em que a receita foi lançada
);


-- 4. INSERÇÃO DE SERVIÇOS PADRÃO 💅
-- Registra os serviços iniciais do catálogo.
-- O 'ON CONFLICT' garante que registros repetidos não gerem erros se o script rodar novamente.
INSERT INTO servicos (nome, preco) VALUES
    ('Manicure Tradicional', 35.00),
    ('Pedicure Tradicional', 40.00),
    ('Alongamento em Gel', 160.00),
    ('Manutenção de Gel', 100.00),
    ('Banho de Gel', 90.00),
    ('Esmaltação em Gel', 70.00),
    ('Design de Sobrancelha', 45.00)
ON CONFLICT (nome) DO NOTHING;