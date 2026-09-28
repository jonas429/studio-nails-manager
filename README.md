# 💅 Studio Nails Manager

> **Projeto de Extensão Universitária — Gestão de Agendamentos e Fluxo Financeiro**  
> **Instituição:** Uninter  
> **Desenvolvedor:** Jonas Andre Moreira de Souza  

---

## 📌 Sobre o Projeto

O **Studio Nails Manager** é uma aplicação web completa voltada para a gestão operacional e financeira de estúdios de beleza e *nail design*. A plataforma permite o agendamento dinâmico de múltiplos serviços simultâneos, controle automático de caixa, upload seguro de comprovativos e emissão de confirmações via WhatsApp.

A solução foi projetada utilizando **Python** com **Streamlit**, apoiada por um banco de dados relacional **PostgreSQL**, e totalmente containerizada com **Docker** e **Docker Compose**, garantindo facilidade de implantação, portabilidade e isolamento de dependências.

---

## 🚀 Funcionalidades Principais

- 📅 **Agendamento Inteligente**: Seleção múltipla de serviços com cálculo automático do valor total.
- 📱 **Integração WhatsApp**: Geração de links diretos de confirmação pré-formatados para os clientes.
- ✂️ **Gestão de Serviços**: Cadastro, listagem e remoção de serviços e preços do catálogo.
- 📄 **Upload Seguro de Comprovativos**: Validação e salvamento de arquivos com identificadores únicos (UUIDs) para prevenção de vulnerabilidades.
- 📊 **Painel Financeiro & Relatórios**: Filtro por período, consolidação de faturamento e gráficos dinâmicos de receita diária.
- ❌ **Cancelamento Seguro**: Exclusão de agendamentos e registros de receitas associados com integridade referencial.

---

## 🛠️ Tecnologias Utilizadas

| Componente | Tecnologia / Biblioteca |
| :--- | :--- |
| **Linguagem Principal** | Python 3.10+ |
| **Interface Web** | Streamlit |
| **Análise de Dados & Gráficos** | Pandas, Plotly Express |
| **Banco de Dados** | PostgreSQL 15 |
| **Conector SQL** | Psycopg2 |
| **Containerização** | Docker & Docker Compose |

---

## 🗄️ Estrutura do Banco de Dados

A modelagem do banco segue as regras formais de integridade referencial no PostgreSQL:

- `servicos`: Guarda a lista de procedimentos oferecidos e os respetivos valores.
- `agendamentos`: Regista as marcações vinculando clientes, datas, horários e serviços (`ON DELETE CASCADE`).
- `receitas`: Armazena o histórico financeiro, descrições dos atendimentos e apontadores de comprovativos.

---

## 💻 Como Executar o Projeto Localmente

### Pré-requisitos
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e em execução.
- [Git](https://git-scm.com/) instalado.

### Passo a Passo

1. **Clonar o repositório:**
   ```bash
   git clone [https://github.com/jonas429/studio-nails-manager.git](https://github.com/jonas429/studio-nails-manager.git)
   cd studio-nails-manager
2. Subir os serviços via Docker Compose:
Bash
docker compose up --build -d
3. Acessar a aplicação:
Abra o seu navegador de preferência e aceda a: http://localhost:8501
4. Para encerrar a execução:
Bash
docker compose down

📁 Estrutura do Repositório
Plaintext
studio-nails-manager/
├── app.py              # Código-fonte principal da aplicação Streamlit
├── Dockerfile          # Definição do container da aplicação Python
├── docker-compose.yml  # Orquestração dos serviços (App + PostgreSQL)
├── init.sql            # Script de criação e população inicial do banco
├── requirements.txt    # Dependências do Python
├── .gitignore          # Regras de exclusão de arquivos no Git
└── README.md           # Documentação do projeto

📄 Licença
Este projeto foi desenvolvido estritamente para fins acadêmicos e de extensão universitária no âmbito do curso de Tecnologia em Gestão de Tecnologia da Informação da Uninter.
