import html
import os
import re
import urllib.parse
import uuid
import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA 💅
# ==============================================================================
st.set_page_config(
    page_title="Gestão de Agendamentos & Finanças",
    page_icon="💅",
    layout="wide",
)


# ==============================================================================
# 2. CONEXÃO COM O BANCO DE DADOS 🔒
# ==============================================================================
def get_connection():
  """Abre a conexão utilizando obrigatoriamente variáveis de ambiente."""
  db_name = os.environ.get("DB_NAME")
  db_user = os.environ.get("DB_USER")
  db_pass = os.environ.get("DB_PASS")
  db_host = os.environ.get("DB_HOST", "localhost")
  db_port = os.environ.get("DB_PORT", "5432")

  if not all([db_name, db_user, db_pass]):
    st.error(
        "⚠️ **Erro de Segurança**: As variáveis de ambiente do banco de dados"
        " não foram configuradas!"
    )
    st.stop()

  return psycopg2.connect(
      dbname=db_name, user=db_user, password=db_pass, host=db_host, port=db_port
  )


# ==============================================================================
# 3. FUNÇÕES AUXILIARES E SEGURANÇA 🛡️
# ==============================================================================
def salvar_comprovante_seguro(upload_file):
  """🔒 Valida extensão e gera UUID único contra Path Traversal."""
  if upload_file is None:
    return None

  extensoes_permitidas = {".png", ".jpg", ".jpeg", ".pdf"}
  ext = os.path.splitext(upload_file.name)[1].lower()

  if ext not in extensoes_permitidas:
    raise ValueError("Tipo de arquivo não permitido!")

  pasta_destino = "comprovantes"
  if not os.path.exists(pasta_destino):
    os.makedirs(pasta_destino)

  nome_seguro = f"{uuid.uuid4().hex}{ext}"
  caminho_completo = os.path.join(pasta_destino, nome_seguro)

  with open(caminho_completo, "wb") as f:
    f.write(upload_file.getbuffer())

  return nome_seguro


def validar_e_limpar_telefone(telefone):
  """🔒 Higieniza o número de telefone (Padrão BR com DDD)."""
  if not telefone:
    return None
  num_limpo = re.sub(r"\D", "", telefone)
  if len(num_limpo) in [10, 11]:
    return num_limpo
  return None


def gerar_link_whatsapp(
    telefone, nome, servicos_texto, valor_total, data, hora
):
  """Gera link para WhatsApp apenas se o número for válido."""
  num_limpo = validar_e_limpar_telefone(telefone)
  if not num_limpo:
    return None

  mensagem = (
      f"Olá, {nome}! 👋\n"
      f"Seu agendamento foi confirmado:\n"
      f"✂️ *Serviço(s):* {servicos_texto}\n"
      f"📅 *Data:* {data.strftime('%d/%m/%Y')}\n"
      f"⏰ *Horário:* {hora.strftime('%H:%M')}\n"
      f"💰 *Total:* R$ {valor_total:.2f}\n\n"
      f"Agradecemos a preferência! 😊"
  )
  msg_url = urllib.parse.quote(mensagem)
  return f"https://wa.me/55{num_limpo}?text={msg_url}"


# ==============================================================================
# 4. CONSULTAS AO BANCO DE DADOS 🗄️
# ==============================================================================
@st.cache_data(ttl=60, show_spinner=False)
def carregar_servicos():
  conn = get_connection()
  try:
    df = pd.read_sql_query("SELECT * FROM servicos ORDER BY nome;", conn)
  finally:
    conn.close()
  return df


@st.cache_data(ttl=60, show_spinner=False)
def carregar_agendamentos_agrupados():
  conn = get_connection()
  query = """
    SELECT 
        a.cliente_nome, 
        a.cliente_telefone, 
        a.data_agendamento, 
        a.hora_agendamento,
        STRING_AGG(s.nome, ', ') AS servicos,
        SUM(s.preco) AS valor_total
    FROM agendamentos a
    JOIN servicos s ON a.servico_id = s.id
    GROUP BY a.cliente_nome, a.cliente_telefone, a.data_agendamento, a.hora_agendamento
    ORDER BY a.data_agendamento DESC, a.hora_agendamento DESC;
    """
  try:
    df = pd.read_sql_query(query, conn)
  finally:
    conn.close()
  return df


@st.cache_data(ttl=60, show_spinner=False)
def carregar_receitas():
  conn = get_connection()
  try:
    df = pd.read_sql_query(
        "SELECT * FROM receitas ORDER BY data_registro DESC;", conn
    )
  finally:
    conn.close()
  return df


def cancelar_horario(cliente_nome, data, hora):
  conn = get_connection()
  cur = conn.cursor()
  try:
    cur.execute(
        "DELETE FROM agendamentos WHERE cliente_nome = %s AND data_agendamento"
        " = %s AND hora_agendamento = %s",
        (cliente_nome, data, hora),
    )
    cur.execute(
        "DELETE FROM receitas WHERE cliente_nome = %s AND data_agendamento ="
        " %s AND hora_agendamento = %s",
        (cliente_nome, data, hora),
    )
    conn.commit()
  finally:
    cur.close()
    conn.close()


# ==============================================================================
# 5. NAVEGAÇÃO 📌
# ==============================================================================
menu = [
    "📅 Novo Agendamento",
    "✂️ Gestão de Serviços",
    "❌ Cancelar Agendamento",
    "📊 Relatório Financeiro",
]
opcao = st.sidebar.selectbox("Menu Principal 📌", menu)


# ==============================================================================
# 6. TELA: NOVO AGENDAMENTO 📅
# ==============================================================================
if opcao == "📅 Novo Agendamento":
  st.header("📅 Novo Agendamento")

  df_servicos = carregar_servicos()

  if not df_servicos.empty:
    nome = st.text_input("Nome do Cliente 👤")
    telefone = st.text_input("Telefone WhatsApp 📱 (DDD + Número)")
    c1, c2 = st.columns(2)
    data = c1.date_input("Data 📅")
    hora = c2.time_input("Horário ⏰")

    col_serv, col_btn = st.columns([5, 1])
    with col_serv:
      servicos_selecionados = st.multiselect(
          "Selecione o(s) Serviço(s) ✂️",
          options=df_servicos["nome"].tolist(),
          placeholder="Escolha um ou mais serviços",
      )
    with col_btn:
      st.write("")
      st.write("")
      if st.button("🔄 Recarregar", help="Atualizar lista de serviços"):
        st.cache_data.clear()
        st.rerun()

    comprovante_file = st.file_uploader(
        "Enviar Comprovante (opcional) 📄", type=["png", "jpg", "jpeg", "pdf"]
    )

    if servicos_selecionados:
      df_escolhidos = df_servicos[
          df_servicos["nome"].isin(servicos_selecionados)
      ]
      lista_servico_ids = df_escolhidos["id"].tolist()
      valor_total = float(df_escolhidos["preco"].sum())

      st.info(f"💰 **Valor Total:** R$ {valor_total:.2f}")

      if st.button("Confirmar Agendamento ✅"):
        num_validado = validar_e_limpar_telefone(telefone)

        if not nome or not num_validado:
          st.warning(
              "Por favor, preencha o nome e um número de telefone válido com"
              " DDD."
          )
        else:
          try:
            nome_arquivo_salvo = (
                salvar_comprovante_seguro(comprovante_file)
                if comprovante_file
                else None
            )

            conn = get_connection()
            cur = conn.cursor()

            try:
              for servico_id in lista_servico_ids:
                cur.execute(
                    """
                                    INSERT INTO agendamentos 
                                    (cliente_nome, cliente_telefone, servico_id, data_agendamento, hora_agendamento) 
                                    VALUES (%s, %s, %s, %s, %s)
                                    """,
                    (nome, telefone, servico_id, data, hora),
                )

              texto_servicos = ", ".join(servicos_selecionados)
              cur.execute(
                  """
                                INSERT INTO receitas 
                                (cliente_nome, data_agendamento, hora_agendamento, descricao, valor, comprovante_nome) 
                                VALUES (%s, %s, %s, %s, %s, %s)
                                """,
                  (
                      nome,
                      data,
                      hora,
                      f"Atendimento: {texto_servicos}",
                      valor_total,
                      nome_arquivo_salvo,
                  ),
              )

              conn.commit()
            finally:
              cur.close()
              conn.close()

            st.cache_data.clear()
            st.success("✅ Agendamento registrado com sucesso!")

            link_wa = gerar_link_whatsapp(
                telefone, nome, texto_servicos, valor_total, data, hora
            )
            if link_wa:
              st.link_button("📲 Enviar Confirmação via WhatsApp", link_wa)

          except psycopg2.errors.UniqueViolation:
            st.error(
                "⚠️ **Conflito de Horário**: Este horário acabou de ser"
                " reservado. Por favor, selecione outro horário!"
            )
          except Exception as e:
            st.error(f"Erro ao processar o agendamento: {e}")
  else:
    st.warning(
        "Nenhum serviço cadastrado. Vá em **✂️ Gestão de Serviços** para"
        " cadastrar o primeiro serviço."
    )


# ==============================================================================
# 7. TELA: GESTÃO DE SERVIÇOS ✂️
# ==============================================================================
elif opcao == "✂️ Gestão de Serviços":
  st.header("✂️ Gerenciamento de Serviços")

  tab_listar, tab_cadastrar, tab_excluir = st.tabs(
      ["📋 Lista", "➕ Novo Serviço", "🗑️ Excluir"]
  )

  with tab_listar:
    df_servicos = carregar_servicos()
    st.dataframe(
        df_servicos[["id", "nome", "preco"]], use_container_width=True
    )

  with tab_cadastrar:
    with st.form("form_novo_servico", clear_on_submit=True):
      novo_nome = st.text_input("Nome do Serviço")
      novo_preco = st.number_input(
          "Preço (R$)", min_value=0.0, step=5.0, format="%.2f"
      )

      if st.form_submit_button("Cadastrar ➕"):
        if novo_nome and novo_preco > 0:
          conn = get_connection()
          cur = conn.cursor()
          try:
            cur.execute(
                "INSERT INTO servicos (nome, preco) VALUES (%s, %s);",
                (novo_nome.strip(), novo_preco),
            )
            conn.commit()
          finally:
            cur.close()
            conn.close()

          st.cache_data.clear()
          st.success("Serviço cadastrado com sucesso!")
          st.rerun()
        else:
          st.warning("Preencha dados válidos.")

  with tab_excluir:
    df_servicos = carregar_servicos()
    if not df_servicos.empty:
      servico_para_deletar = st.selectbox(
          "Selecione para remover 🗑️", options=df_servicos["nome"]
      )

      if st.button("Confirmar Exclusão ❌"):
        conn = get_connection()
        cur = conn.cursor()
        try:
          cur.execute(
              "DELETE FROM servicos WHERE nome = %s;", (servico_para_deletar,)
          )
          conn.commit()
        finally:
          cur.close()
          conn.close()

        st.cache_data.clear()
        st.success("Serviço excluído!")
        st.rerun()


# ==============================================================================
# 8. TELA: CANCELAR AGENDAMENTO ❌
# ==============================================================================
elif opcao == "❌ Cancelar Agendamento":
  st.header("❌ Cancelar Horário")

  df_agendamentos = carregar_agendamentos_agrupados()

  if not df_agendamentos.empty:
    df_agendamentos["identificador"] = (
        df_agendamentos["cliente_nome"]
        + " - "
        + df_agendamentos["data_agendamento"].astype(str)
        + " às "
        + df_agendamentos["hora_agendamento"].astype(str)
    )

    escolha = st.selectbox(
        "Selecione o agendamento 🗑️", df_agendamentos["identificador"]
    )
    item = df_agendamentos[
        df_agendamentos["identificador"] == escolha
    ].iloc[0]

    nome_sanitizado = html.escape(str(item["cliente_nome"]))
    servicos_sanitizados = html.escape(str(item["servicos"]))

    st.warning(
        f"Cancelar agendamento de **{nome_sanitizado}**"
        f" ({servicos_sanitizados})?"
    )

    if st.button("Confirmar Cancelamento ❌"):
      cancelar_horario(
          item["cliente_nome"],
          item["data_agendamento"],
          item["hora_agendamento"],
      )
      st.cache_data.clear()
      st.success("Agendamento cancelado com sucesso!")
      st.rerun()
  else:
    st.info("Nenhum agendamento encontrado.")


# ==============================================================================
# 9. TELA: RELATÓRIO FINANCEIRO 📊
# ==============================================================================
elif opcao == "📊 Relatório Financeiro":
  st.header("📊 Painel Financeiro")

  df_receitas = carregar_receitas()

  if not df_receitas.empty:
    df_receitas["data_agendamento"] = pd.to_datetime(
        df_receitas["data_agendamento"]
    )

    st.subheader("Filtro por Período 📅")
    col_d1, col_d2 = st.columns(2)

    data_minima = df_receitas["data_agendamento"].min().date()
    data_maxima = df_receitas["data_agendamento"].max().date()

    dt_inicio = col_d1.date_input("Data Inicial", data_minima)
    dt_fim = col_d2.date_input("Data Final", data_maxima)

    df_filtrado = df_receitas[
        (df_receitas["data_agendamento"].dt.date >= dt_inicio)
        & (df_receitas["data_agendamento"].dt.date <= dt_fim)
    ]

    st.markdown("---")

    if not df_filtrado.empty:
      c1, c2 = st.columns(2)
      c1.metric(
          "Faturamento do Período 💵", f"R$ {df_filtrado['valor'].sum():.2f}"
      )
      c2.metric("Atendimentos no Período 📋", len(df_filtrado))

      st.subheader("Registros 📑")
      st.dataframe(
          df_filtrado[[
              "cliente_nome",
              "data_agendamento",
              "hora_agendamento",
              "descricao",
              "valor",
              "comprovante_nome",
          ]],
          use_container_width=True,
      )

      st.subheader("Faturamento Diário 📈")
      df_diario = (
          df_filtrado.groupby("data_agendamento")["valor"].sum().reset_index()
      )
      fig = px.bar(
          df_diario,
          x="data_agendamento",
          y="valor",
          labels={"data_agendamento": "Data", "valor": "Faturamento (R$)"},
      )
      st.plotly_chart(fig, use_container_width=True)
    else:
      st.warning("Nenhum registro no período selecionado.")
  else:
    st.info("Nenhuma receita registrada.")