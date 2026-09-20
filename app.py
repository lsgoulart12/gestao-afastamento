import json
import os
from datetime import datetime, timedelta
import streamlit as st

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Sistema de Gestão de Afastamentos",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    /* Força as variáveis nativas de cor de fundo dos inputs e selects no Streamlit */
    :root {
        --background-color: #0e1117;
        --secondary-background-color: #161b22;
        --text-color: #ffffff;
    }

    /* Sobrescreve diretamente qualquer container de input e selectbox */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    input, select, textarea {
        background-color: #161b22 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border-color: #30363d !important;
    }

    /* Garante cor correta para o texto selecionado e ícones */
    div[data-baseweb="select"] span, div[data-baseweb="select"] svg {
        color: #ffffff !important;
        fill: #ffffff !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    /* Força os títulos/rótulos acima dos boxes a ficarem em branco puro e alto contraste */
    div[data-testid="stForm"] label p, 
    .stTextInput label, 
    .stSelectbox label, 
    .stNumberInput label, 
    .stDateInput label,
    label {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- ARQUIVO DE PERSISTÊNCIA LOCAL ---
DATA_FILE = "dados.json"


def carregar_dados():
  if os.path.exists(DATA_FILE):
    try:
      with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except json.JSONDecodeError:
      return []
  return []


def salvar_dados(dados):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(dados, f, ensure_ascii=False, indent=4)


# Inicializa os dados na sessão
if "registros" not in st.session_state:
  st.session_state.registros = carregar_dados()

# --- CABEÇALHO DO SISTEMA ---
st.markdown(
    "<h1 style='text-align: center;'>Sistema de Gestão de Afastamentos</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #8b949e;'>Painel executivo para"
    " controle operacional, conformidade de afastamentos e acolhimento.</p>",
    unsafe_allow_html=True,
)
st.write("")

# --- LAYOUT EM DUAS COLUNAS ---
col_form, col_monitor = st.columns([1.2, 1.8], gap="large")

with col_form:
  st.markdown("### Registro de Ocorrência")

  with st.form("form_afastamento", clear_on_submit=True):
    matricula = st.text_input(
        "Matrícula do Colaborador", placeholder="Ex: 997021"
    )
    nome = st.text_input("Nome do Colaborador", placeholder="Ex: Ricardo Silva")
    produto = st.text_input(
        "Produto / Produção", placeholder="Ex: Quem ama cuida"
    )

    modulo = st.selectbox(
        "Módulo de Gravação / Cidade Cenográfica",
        ["CC1", "CC2", "CC3", "Estúdios Globo", "Externa"],
    )

    dias_afastamento = st.number_input(
        "Dias de Afastamento", min_value=1, max_value=90, value=1
    )

    classificacao = st.selectbox(
        "Classificação da Ocorrência",
        [
            "Doença Comum",
            "Acidente Doméstico",
            "Acidente de Trabalho",
            "Acolhimento Preventivo",
        ],
    )

    submitted = st.form_submit_button("Salvar Registro")

    if submitted:
      if matricula and nome:
        novo_registro = {
            "matricula": matricula,
            "nome": nome,
            "produto": produto,
            "modulo": modulo,
            "dias": dias_afastamento,
            "classificacao": classificacao,
            "data_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        st.session_state.registros.append(novo_registro)
        salvar_dados(st.session_state.registros)
        st.success("Registro salvo com sucesso!")
        st.rerun()
      else:
        st.error("Preencha ao menos a Matrícula e o Nome do colaborador.")

with col_monitor:
  st.markdown("### Monitoramento Ativo de Afastados")

  # Filtro de visualização
  filtro_modulo = st.selectbox(
      "Filtrar Visualização por Módulo / Estúdio",
      ["Visão Geral (Todos os Módulos e Cidades)"]
      + [
          "CC1",
          "CC2",
          "CC3",
          "Estúdios Globo",
          "Externa",
      ],
  )

  registros = st.session_state.registros

  if not registros:
    st.info(
        "Nenhum afastamento registrado no momento. Utilize o formulário ao lado"
        " para incluir ocorrências."
    )
  else:
    # Filtragem
    if filtro_modulo != "Visão Geral (Todos os Módulos e Cidades)":
      registros_filtrados = [
          r for r in registros if r.get("modulo") == filtro_modulo
      ]
    else:
      registros_filtrados = registros

    if not registros_filtrados:
      st.warning(
          f"Nenhum registro encontrado para o filtro: {filtro_modulo}."
      )
    else:
      for reg in reversed(registros_filtrados):
        # Cálculo de retorno
        try:
          data_reg = datetime.strptime(reg["data_registro"], "%Y-%m-%d %H:%M:%S")
          dias_af = int(reg["dias"])
          data_retorno = data_reg + timedelta(days=dias_af)
          dias_restantes = (data_retorno - datetime.now()).days
        except Exception:
          dias_restantes = 0

        # Alerta visual baseado no prazo (mantendo apenas os dois ícones essenciais de status)
        if dias_restantes <= 1:
          status_msg = f"🚨 ALERTA CRÍTICO: {max(0, dias_restantes)} dia(s) restante(s). Amanhã o colaborador estará apto para retornar à escala!"
          borda_cor = "border-left: 5px solid #ff4b4b;"
        else:
          status_msg = f"⚠️ ATENÇÃO: {dias_restantes} dias restantes para retorno à escala."
          borda_cor = "border-left: 5px solid #ffa500;"

        st.markdown(
            f"""
            <div style="background-color: #161b22; padding: 20px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 15px; {borda_cor}">
                <strong>Matrícula:</strong> {reg['matricula']} | <strong>Colaborador:</strong> {reg['nome']}<br>
                <strong>Produto:</strong> {reg.get('produto', 'N/D')} | <strong>Local:</strong> {reg['modulo']}<br>
                <strong>Tempo de Afastamento:</strong> {reg['dias']} dia(s) | <strong>Classificação:</strong> {reg['classificacao']}<br>
                <div style="margin-top: 8px; font-weight: bold; color: #ffcccc;">{status_msg}</div>
                <div style="font-size: 0.8rem; color: #8b949e; margin-top: 5px;">Registrado em: {reg['data_registro']} • Protocolo de Acolhimento Ativo (LGPD Compliant)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )