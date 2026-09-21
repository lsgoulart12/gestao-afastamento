import json
import html
import os
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageOps
import streamlit as st


def preparar_logo_redonda(caminho_imagem, tamanho=(180, 180)):
  try:
    imagem = Image.open(caminho_imagem).convert("RGBA")
    imagem = ImageOps.fit(imagem, tamanho, Image.Resampling.LANCZOS)
    mascara = Image.new("L", tamanho, 0)
    ImageDraw.Draw(mascara).ellipse((0, 0, tamanho[0], tamanho[1]), fill=255)
    resultado = Image.new("RGBA", tamanho, (0, 0, 0, 0))
    resultado.paste(imagem, (0, 0), mask=mascara)
    return resultado
  except (OSError, ValueError):
    return caminho_imagem

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Sistema de Gestão de Afastamentos",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "tema" not in st.session_state:
  st.session_state.tema = "Escuro","claro"

tema = st.sidebar.radio("Tema", ["Claro", "Escuro"], index=1 if st.session_state.tema == "Escuro" else 0)
st.session_state.tema = tema

if tema == "Escuro":
  tema_background = "#0e1117"
  tema_surface = "#161b22"
  tema_text = "#ffffff"
  tema_border = "#30363d"
else:
  tema_background = "#f8fafc"
  tema_surface = "#ffffff"
  tema_text = "#1f2937"
  tema_border = "#9ca3af"

st.markdown(
    f"""
    <style>
    :root {{
        --background-color: {tema_background};
        --secondary-background-color: {tema_surface};
        --text-color: {tema_text};
      --form-background: #ffffff;
      --form-text: #000000;
      --form-placeholder: #555555;
      --form-border: #d1d5db;
      --form-border-hover: #9ca3af;
      --form-focus: #2563eb;
    }}

    .stApp {{
        background-color: {tema_background};
        color: {tema_text};
    }}

    /* BaseWeb e widgets Streamlit: todos os campos permanecem brancos */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stDateInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-baseweb="input"] input,
    [data-baseweb="input"] > div,
    [data-baseweb="select"] > div,
    [role="combobox"],
    [data-testid="stMultiSelect"] [data-baseweb="select"],
    [data-testid="stRadio"] label,
    [data-testid="stCheckbox"] label,
    [data-testid="stButton"] button,
    [data-testid="stFormSubmitButton"] button {{
      background-color: #ffffff !important;
      color: #000000 !important;
      -webkit-text-fill-color: #000000 !important;
      border: 1px solid #d1d5db !important;
      border-radius: 8px !important;
      opacity: 1 !important;
    }}

    /* Labels são independentes do texto nativo do tema e sempre têm contraste alto */
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label,
    [data-testid="stTextInput"] label,
    [data-testid="stNumberInput"] label,
    [data-testid="stSelectbox"] label,
    [data-testid="stDateInput"] label,
    [data-testid="stTextArea"] label,
    [data-testid="stMultiSelect"] label,
    [data-testid="stRadio"] label,
    [data-testid="stCheckbox"] label,
    div[data-testid="stForm"] label p {{
      color: #ffffff !important;
      font-weight: 700 !important;
      font-size: 16px !important;
      line-height: 1.4 !important;
      opacity: 1 !important;
      text-shadow: none !important;
    }}

    input::placeholder,
    textarea::placeholder {{
      color: #555555 !important;
      -webkit-text-fill-color: #555555 !important;
      opacity: 1 !important;
    }}

    [data-baseweb="select"] span,
    [data-baseweb="select"] input,
    [data-baseweb="select"] svg,
    [role="combobox"] span {{
      color: #000000 !important;
      fill: #000000 !important;
      -webkit-text-fill-color: #000000 !important;
    }}

    [data-testid="stTextInput"]:hover input,
    [data-testid="stNumberInput"]:hover input,
    [data-testid="stDateInput"]:hover input,
    [data-testid="stTextArea"]:hover textarea,
    [data-baseweb="input"]:hover > div,
    [data-baseweb="select"]:hover > div,
    [data-testid="stButton"] button:hover,
    [data-testid="stFormSubmitButton"] button:hover {{
      border-color: #9ca3af !important;
    }}

    [data-testid="stTextInput"]:focus-within input,
    [data-testid="stNumberInput"]:focus-within input,
    [data-testid="stDateInput"]:focus-within input,
    [data-testid="stTextArea"]:focus-within textarea,
    [data-baseweb="input"]:focus-within > div,
    [data-baseweb="select"]:focus-within > div,
    [role="combobox"]:focus,
    [data-testid="stButton"] button:focus,
    [data-testid="stFormSubmitButton"] button:focus {{
      border-color: #2563eb !important;
      box-shadow: 0 0 0 1px #2563eb !important;
      outline: none !important;
    }}

    [data-baseweb="menu"],
    [data-baseweb="popover"],
    [role="listbox"],
    [role="option"] {{
      background-color: #ffffff !important;
      color: #000000 !important;
    }}

    [role="option"] span,
    [role="option"]:hover,
    [role="option"][aria-selected="true"] {{
      color: #000000 !important;
    }}

    @media (max-width: 768px) {{
      [data-testid="stWidgetLabel"] p,
      [data-testid="stWidgetLabel"] label {{
        font-size: 16px !important;
      }}

      input, select, textarea,
      [data-testid="stButton"] button,
      [data-testid="stFormSubmitButton"] button {{
        min-height: 48px !important;
        font-size: 16px !important;
      }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    /* Alvo real dos labels dos widgets no Streamlit 1.58.0 */
    label[data-testid="stWidgetLabel"],
    label[data-testid="stWidgetLabel"] p,
    div[data-testid="stForm"] label[data-testid="stWidgetLabel"] p {
      color: #0066FF !important;
      font-size: 16px !important;
      font-weight: 700 !important;
      opacity: 1 !important;
    }

    [data-testid="stMarkdownContainer"] div[style*="background-color: #161b22"] {
      background-color: var(--secondary-background-color) !important;
      border-color: var(--secondary-background-color) !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
  f"""
  <style>
  .stApp {{
    background-color: {tema_background} !important;
    color: {tema_text} !important;
  }}

  /* Seletor definitivo de alta especificidade para os rótulos */
  .stTextInput label,
  .stSelectbox label,
  .stNumberInput label,
  .stDateInput label,
  div[data-baseweb="input"] label,
  div[data-baseweb="select"] label,
  label {{
    color: #0066FF !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
  }}

  /* Força também nos parágrafos internos caso o Streamlit aninhe elementos */
  .stTextInput label p,
  .stSelectbox label p,
  .stNumberInput label p,
  .stDateInput label p,
  div[data-testid="stForm"] label[data-testid="stWidgetLabel"] p,
  label p {{
    color: #0066FF !important;
    font-weight: 700 !important;
  }}

  /* Inputs e Selectboxes com fundo dinâmico */
  div[data-baseweb="input"] > div,
  div[data-baseweb="select"] > div,
  input, select {{
    background-color: {tema_surface} !important;
    color: {tema_text} !important;
    border-color: {tema_border} !important;
  }}

  div[data-baseweb="select"] span {{
    color: {tema_text} !important;
  }}
  </style>
  """,
  unsafe_allow_html=True,
)

# --- ARQUIVO DE PERSISTÊNCIA LOCAL ---
DATA_FILE = "dados.json"
MAX_TEXT_LENGTH = 200


def carregar_dados():
  if os.path.exists(DATA_FILE):
    try:
      with open(DATA_FILE, "r", encoding="utf-8") as f:
        dados = json.load(f)
        if not isinstance(dados, list):
          return []
        return [registro for registro in dados if isinstance(registro, dict)]
    except (OSError, json.JSONDecodeError, TypeError):
      return []
  return []


def salvar_dados(dados):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(dados, f, ensure_ascii=False, indent=4)


# Inicializa os dados na sessão
if "registros" not in st.session_state:
  st.session_state.registros = carregar_dados()

# --- CABEÇALHO DO SISTEMA ---
col_logo_esquerda, col_logo_centro, col_logo_direita = st.columns([1, 2, 1])
with col_logo_centro:
  st.image(preparar_logo_redonda("39147.jpg"), width=140)
st.markdown(
    "<h1 style='text-align: center; color: #0066FF; font-size: 1.4rem; "
    "font-weight: 700; margin-top: -10px;'>Sistema de Gestão de Afastamentos</h1>",
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
      matricula = matricula.strip()
      nome = nome.strip()
      produto = produto.strip()

      if not matricula or not nome:
        st.error("Preencha ao menos a Matrícula e o Nome do colaborador.")
      elif any(len(valor) > MAX_TEXT_LENGTH for valor in (matricula, nome, produto)):
        st.error(f"Os campos de texto devem ter no máximo {MAX_TEXT_LENGTH} caracteres.")
      else:
        novo_registro = {
            "matricula": matricula,
            "nome": nome,
            "produto": produto,
            "modulo": modulo,
            "dias": dias_afastamento,
            "classificacao": classificacao,
            "data_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        try:
          registros_atualizados = [*st.session_state.registros, novo_registro]
          salvar_dados(registros_atualizados)
          st.session_state.registros = registros_atualizados
          st.success("Registro salvo com sucesso!")
          st.rerun()
        except (OSError, TypeError, ValueError):
          st.error("Não foi possível salvar o registro. Tente novamente.")

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
          data_reg = datetime.strptime(str(reg["data_registro"]), "%Y-%m-%d %H:%M:%S")
          dias_af = int(reg["dias"])
          data_retorno = data_reg + timedelta(days=dias_af)
          dias_restantes = (data_retorno - datetime.now()).days
        except (KeyError, TypeError, ValueError, OverflowError):
          dias_restantes = 0

        matricula_exibicao = html.escape(str(reg.get("matricula", "N/D")))
        nome_exibicao = html.escape(str(reg.get("nome", "N/D")))
        produto_exibicao = html.escape(str(reg.get("produto", "N/D")))
        modulo_exibicao = html.escape(str(reg.get("modulo", "N/D")))
        dias_exibicao = html.escape(str(reg.get("dias", "N/D")))
        classificacao_exibicao = html.escape(str(reg.get("classificacao", "N/D")))
        data_exibicao = html.escape(str(reg.get("data_registro", "N/D")))

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
                <strong>Matrícula:</strong> {matricula_exibicao} | <strong>Colaborador:</strong> {nome_exibicao}<br>
                <strong>Produto:</strong> {produto_exibicao} | <strong>Local:</strong> {modulo_exibicao}<br>
                <strong>Tempo de Afastamento:</strong> {dias_exibicao} dia(s) | <strong>Classificação:</strong> {classificacao_exibicao}<br>
                <div style="margin-top: 8px; font-weight: bold; color: #ffcccc;">{status_msg}</div>
                <div style="font-size: 0.8rem; color: #8b949e; margin-top: 5px;">Registrado em: {data_exibicao} • Protocolo de Acolhimento Ativo (LGPD Compliant)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )