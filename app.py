import streamlit as st
import json
import os
from datetime import datetime

# Configuração da página e layout executivo
st.set_page_config(
    page_title="Gestão de Afastamentos | Sistema Corporativo",
    layout="wide"
)

# Injeção de CSS refinado, sofisticado (Estilo 4K / UI Profissional com foco em harmonia artística)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        .stApp {
            background-color: #0B0E14;
            color: #F0F3F6;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* Tipografia e Títulos com fontes mais elegantes e equilibradas */
        h1, h2, h3, h4 {
            font-family: 'Inter', sans-serif;
            color: #FFFFFF;
            letter-spacing: -0.02em;
        }

        /* Redução sutil das fontes dos títulos das colunas para maior elegância */
        .col-title {
            font-size: 1.15rem !important;
            font-weight: 600 !important;
            color: #E1E4E8 !important;
            margin-bottom: 0.75rem !important;
        }

        /* Cartões de Monitoramento Sofisticados e limpos */
        .card-container {
            background: linear-gradient(135deg, #161B22 0%, #11161D 100%);
            border: 1px solid #30363D;
            border-left: 4px solid #8B949E;
            padding: 1rem;
            border-radius: 6px;
            margin-bottom: 0.85rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        
        .card-container:hover {
            border-color: #58A6FF;
        }
        
        .card-critico {
            border-left-color: #F85149;
        }

        .card-retorno-1dia {
            border-left-color: #F85149;
            background: linear-gradient(135deg, #2D1515 0%, #1E1215 100%);
        }

        .card-retorno-2dias {
            border-left-color: #D29922;
            background: linear-gradient(135deg, #2D2214 0%, #1E1712 100%);
        }

        /* Ajustes nos elementos de formulário para harmonia visual limpa */
        .stTextInput > div > div > input, .stNumberInput > div > div > input, .stSelectbox > div > div > div {
            background-color: #161B22;
            color: #F0F3F6;
            border: 1px solid #30363D;
            border-radius: 6px;
            font-size: 0.9rem;
        }
        
        .stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus {
            border-color: #58A6FF;
            box-shadow: 0 0 0 1px #58A6FF;
        }

        /* Botões sofisticados */
        .stButton > button, .stFormSubmitButton > button {
            background-color: #21262D;
            color: #F0F3F6;
            border: 1px solid #30363D;
            border-radius: 6px;
            font-weight: 500;
            font-size: 0.9rem;
            transition: all 0.2s ease;
        }

        .stButton > button:hover, .stFormSubmitButton > button:hover {
            background-color: #30363D;
            border-color: #8B949E;
            color: #FFFFFF;
        }
    </style>
""", unsafe_allow_html=True)

# Arquivo JSON para persistência na mesma pasta do projeto
ARQUIVO_DADOS = 'dados.json'

def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        return []
    try:
        with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def salvar_dados(registros):
    with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
        json.dump(registros, f, ensure_ascii=False, indent=4)

def inserir_registro(matricula, nome, produto, modulo_gravacao, estudio, dias, tipo):
    registros = carregar_dados()
    novo_registro = {
        "id": datetime.now().strftime('%Y%m%d%H%M%S%f'),
        "matricula": matricula,
        "nome": nome,
        "produto": produto,
        "modulo_gravacao": modulo_gravacao,
        "estudio": estudio,
        "dias": dias,
        "tipo": tipo,
        "data_registro": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    registros.append(novo_registro)
    salvar_dados(registros)

def excluir_registro(reg_id):
    registros = carregar_dados()
    registros = [r for r in registros if r.get("id") != reg_id]
    salvar_dados(registros)

# Layout Principal centralizado e esteticamente balanceado
st.markdown("<h2 style='text-align: center; margin-bottom: 0px;'>Sistema de Gestão de Afastamentos</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8B949E; font-size: 0.95rem; margin-top: 5px;'>Painel executivo para controle operacional, conformidade e acolhimento.</p>", unsafe_allow_html=True)
st.markdown("<div style='margin: 1.5rem auto; width: 60%; border-bottom: 1px solid #21262D;'></div>", unsafe_allow_html=True)

col_spacer1, col_form, col_space_mid, col_painel, col_spacer2 = st.columns([0.5, 1.3, 0.3, 2.2, 0.5], gap="small")

with col_form:
    st.markdown("<div class='col-title'>Registro de Ocorrência</div>", unsafe_allow_html=True)
    
    with st.form("form_cadastro", clear_on_submit=False):
        matricula = st.text_input("Matrícula do Colaborador")
        nome = st.text_input("Nome do Colaborador")
        produto = st.text_input("Produto / Produção (Ex: Novela X, Reality Y)")
        
        # Módulo de Gravação / Cidade Cenográfica
        modulo_gravacao = st.selectbox(
            "Módulo de Gravação / Cidade Cenográfica", 
            ["MG1", "MG2", "MG3", "MG4", "CC1", "CC2", "CC3"]
        )
        
        # Campo de texto livre para inserção personalizada
        estudio = st.text_input("Estúdio / CC (Ex: MG1 - Estúdio A, MG2 - Estúdio E, CC1, etc.)")
            
        dias = st.number_input("Dias de Afastamento", min_value=1, max_value=365, value=1)
        tipo = st.selectbox(
            "Classificação da Ocorrência", 
            ["Doença Comum", "Acidente Doméstico", "Acidente de Trabalho"]
        )
        
        cadastrar = st.form_submit_button("Salvar Registro")
        if cadastrar:
            if matricula.strip() and nome.strip() and produto.strip():
                inserir_registro(matricula.strip(), nome.strip(), produto.strip(), modulo_gravacao, estudio.strip(), dias, tipo)
                st.success("Ocorrência registrada com sucesso.")
                st.rerun()
            else:
                st.error("Os campos Matrícula, Nome e Produto são obrigatórios.")

    # Seção de Correção / Exclusão rápida
    st.markdown("<div style='margin: 1.2rem 0; border-bottom: 1px solid #21262D;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='col-title'>Gerenciar / Corrigir Cadastros</div>", unsafe_allow_html=True)
    registros_atuais = carregar_dados()
    if registros_atuais:
        opcoes_exclusao = {f"{r['nome']} (Mat: {r['matricula']} - {r['estudio']})": r.get('id') for r in registros_atuais}
        selecionado_para_excluir = st.selectbox("Selecionar registro para remover/corrigir", list(opcoes_exclusao.keys()))
        if st.button("Excluir Registro Selecionado"):
            if selecionado_para_excluir:
                reg_id_alvo = opcoes_exclusao[selecionado_para_excluir]
                excluir_registro(reg_id_alvo)
                st.warning("Registro removido. Você pode cadastrá-lo novamente com os dados corrigidos.")
                st.rerun()
    else:
        st.info("Nenhum registro para gerenciar no momento.")

with col_painel:
    st.markdown("<div class='col-title'>Monitoramento Ativo de Afastados</div>", unsafe_allow_html=True)
    
    locais_disponiveis = [
        "Visão Geral (Todos os Módulos e Cidades - Plantão Noturno)",
        "MG1 - Estúdio A", "MG1 - Estúdio B", "MG1 - Estúdio C", "MG1 - Estúdio D",
        "MG2 - Estúdio E", "MG2 - Estúdio F",
        "MG3 - Estúdio G", "MG3 - Estúdio H", "MG3 - Estúdio I", "MG3 - Estúdio J",
        "MG4 - Estúdio K", "MG4 - Estúdio L", "MG4 - Estúdio M",
        "CC1",
        "CC2",
        "CC3"
    ]
    
    filtro_selecionado = st.selectbox("Filtrar Visualização por Módulo / Estúdio", locais_disponiveis)
    
    st.markdown("<div style='margin: 0.8rem 0; border-bottom: 1px solid #21262D;'></div>", unsafe_allow_html=True)
    
    registros = carregar_dados()
    
    if not registros:
        st.info("Nenhum registro de afastamento ativo no momento. Os dados serão salvos no arquivo dados.json na pasta do projeto.")
    else:
        if filtro_selecionado.startswith("Visão Geral"):
            registros_filtrados = registros
        else:
            import unicodedata

            normalizar_estudio = lambda texto: unicodedata.normalize(
                "NFKD", " ".join(texto.strip().lower().split())
            ).encode("ascii", "ignore").decode("ascii")
            filtro_normalizado = normalizar_estudio(filtro_selecionado)
            registros_filtrados = [
                reg for reg in registros
                if (
                    filtro_normalizado in normalizar_estudio(reg.get("estudio", ""))
                    or normalizar_estudio(reg.get("estudio", "")) in filtro_normalizado
                )
            ]
            
        if not registros_filtrados:
            st.info("Nenhum registro encontrado para o filtro selecionado.")
        else:
            # Ordenação inteligente: menor número de dias no topo
            registros_filtrados = sorted(registros_filtrados, key=lambda x: x['dias'])
            
            for reg in registros_filtrados:
                col_matricula = reg.get("matricula", "N/D")
                col_nome = reg["nome"]
                col_produto = reg.get("produto", "N/D")
                col_mg = reg.get("modulo_gravacao", "N/D")
                col_estudio = reg.get("estudio", "N/D")
                col_dias = reg["dias"]
                col_tipo = reg["tipo"]
                col_data = reg["data_registro"]
                
                # Alertas visuais estilizados e com fonte levemente compactada para melhor respiro visual
                if col_dias == 1:
                    classe_card = "card-container card-retorno-1dia"
                    aviso_escala = "<br><strong style='color: #F85149;'>🚨 ALERTA CRÍTICO: 1 dia restante. Amanhã o colaborador estará apto para retornar à escala!</strong>"
                elif col_dias == 2:
                    classe_card = "card-container card-retorno-2dias"
                    aviso_escala = "<br><strong style='color: #D29922;'>⚠️ ATENÇÃO: 2 dias restantes para retorno à escala.</strong>"
                elif col_dias > 10:
                    classe_card = "card-container card-critico"
                    aviso_escala = ""
                else:
                    classe_card = "card-container"
                    aviso_escala = ""
                
                st.markdown(f"""
                    <div class="{classe_card}">
                        <div style="font-size: 0.88rem; line-height: 1.5;">
                            <strong>Matrícula:</strong> {col_matricula} &nbsp;|&nbsp; <strong>Colaborador:</strong> {col_nome}<br>
                            <strong>Produto:</strong> {col_produto} &nbsp;|&nbsp; <strong>Local:</strong> {col_mg} ({col_estudio})<br>
                            <strong>Tempo de Afastamento:</strong> {col_dias} dia(s) &nbsp;|&nbsp; <strong>Classificação:</strong> {col_tipo}
                            {aviso_escala}<br>
                            <span style="color: #8B949E; font-size: 0.78rem;">Registrado em: {col_data} &bull; Protocolo de Acolhimento Ativo (LGPD Compliant)</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)