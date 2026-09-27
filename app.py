import json
import os
import secrets
import tempfile
import uuid
from datetime import date, datetime, timedelta
from functools import wraps

import pytz
from flask import Flask, redirect, render_template, request, session, url_for

BASEDIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(BASEDIR, "templates")
STATIC_DIR = os.path.join(BASEDIR, "static")
DATA_FILE = os.path.join(BASEDIR, "dados.json")

app = Flask(
    __name__,
    template_folder=TEMPLATES_DIR,
    static_folder=STATIC_DIR,
)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)

FUSO_RIO = pytz.timezone("America/Sao_Paulo")
CENTROS_CUSTO = (
    "MG1 ABCD",
    "MG2 EF",
    "MG3 HIJL",
    "MG4 MKL",
    "CC1",
    "CC2",
    "CC3",
)
ALOCACOES = (
    "MG1 - Estúdio A",
    "MG1 - Estúdio B",
    "MG1 - Estúdio C",
    "MG1 - Estúdio D",
    "MG2 - Estúdio E",
    "MG2 - Estúdio F",
    "MG3 - Estúdio H",
    "MG3 - Estúdio I",
    "MG3 - Estúdio J",
    "MG3 - Estúdio L",
    "MG4 - Estúdio M",
    "MG4 - Estúdio K",
    "MG4 - Estúdio L",
    "CC1",
    "CC2",
    "CC3",
)
TIPOS_AFASTAMENTO = (
    "Atestado médico",
    "Acidente de trabalho",
    "Licença maternidade",
    "Licença paternidade",
    "Outro afastamento",
)


class DadosInvalidosError(ValueError):
    """Indica que o arquivo de persistência não contém uma lista de registros."""


def requer_autenticacao(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("autenticado"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapper


def carregar_registros():
    """Lê o JSON sem modificar o arquivo original em caso de erro."""
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as arquivo:
            registros = json.load(arquivo)
    except (OSError, json.JSONDecodeError) as erro:
        raise DadosInvalidosError("Não foi possível ler os dados salvos.") from erro

    if not isinstance(registros, list) or any(
        not isinstance(registro, dict) for registro in registros
    ):
        raise DadosInvalidosError("O arquivo de dados possui uma estrutura inválida.")
    return registros


def salvar_registros(registros):
    """Grava em arquivo temporário e substitui o JSON somente após sucesso."""
    caminho_temporario = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=BASEDIR,
            prefix=".dados-",
            suffix=".tmp",
            delete=False,
        ) as arquivo:
            caminho_temporario = arquivo.name
            json.dump(registros, arquivo, ensure_ascii=False, indent=2)
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(caminho_temporario, DATA_FILE)
    except OSError:
        if caminho_temporario and os.path.exists(caminho_temporario):
            os.remove(caminho_temporario)
        raise


def obter_data_inicio(registro):
    """Aceita o formato atual e os campos de data dos registros legados."""
    valor_data = registro.get("data_inicio") or registro.get("data_registro")
    if not valor_data:
        raise ValueError("Registro sem data de início.")
    return date.fromisoformat(str(valor_data)[:10])


def classificar_status(dias_restantes):
    if dias_restantes <= 0:
        return "Encerrado", "status-closed"
    if dias_restantes == 1:
        return "Retorno em 1 dia", "status-one-day"
    if dias_restantes == 2:
        return "Retorno em 2 dias", "status-two-days"
    if dias_restantes == 3:
        return "Retorno em 3 dias", "status-three-days"
    return "Retorno em 4 dias ou mais", "status-four-plus"


def obter_grupo_centro(centro_custo):
    if centro_custo.startswith("MG1"):
        return "MG1 ABCD"
    if centro_custo.startswith("MG2"):
        return "MG2 EF"
    if centro_custo.startswith("MG3"):
        return "MG3 HIJL"
    if centro_custo.startswith("MG4"):
        return "MG4 MKL"
    return centro_custo if centro_custo in {"CC1", "CC2", "CC3"} else None


def preparar_registros(registros, hoje):
    """Calcula previsão, prazo restante e alerta sem alterar os dados persistidos."""
    preparados = []
    for registro in registros:
        try:
            data_inicio = obter_data_inicio(registro)
            dias = int(registro["dias"])
            if dias < 1:
                continue
            data_termino = data_inicio + timedelta(days=dias)
        except (KeyError, TypeError, ValueError, OverflowError):
            continue

        dias_restantes = (data_termino - hoje).days
        status_texto, status_classe = classificar_status(dias_restantes)
        preparados.append(
            {
                **registro,
                "colaborador": registro.get("colaborador") or registro.get("nome", "N/D"),
                "matricula": registro.get("matricula", "N/D"),
                "produto": registro.get("produto") or registro.get("producao", "N/D"),
                "centro_custo": (
                    registro.get("centro_custo")
                    or registro.get("estudio")
                    or registro.get("modulo_gravacao")
                    or registro.get("modulo", "N/D")
                ),
                "tipo_afastamento": registro.get("tipo_afastamento")
                or registro.get("tipo", "N/D"),
                "data_inicio_exibicao": data_inicio.strftime("%d/%m/%Y"),
                "data_inicio_form": data_inicio.isoformat(),
                "data_termino_exibicao": data_termino.strftime("%d/%m/%Y"),
                "dias_restantes": dias_restantes,
                "status_texto": status_texto,
                "status_classe": status_classe,
            }
        )

    return sorted(preparados, key=obter_data_inicio, reverse=True)


@app.route("/login", methods=["GET", "POST"])
def login():
    erro_login = None
    if request.method == "POST":
        usuario = request.form.get("usuario", "")
        senha = request.form.get("senha", "")
        if usuario == "ADM" and senha == "8920":
            session.clear()
            session["autenticado"] = True
            return redirect(url_for("index"))
        erro_login = "Usuário ou senha incorretos."
    return render_template("login.html", erro_login=erro_login)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/", methods=["GET"])
@requer_autenticacao
def index():
    agora = datetime.now(FUSO_RIO)
    erro_dados = None
    try:
        registros = carregar_registros()
    except DadosInvalidosError:
        registros = []
        erro_dados = "Não foi possível ler os registros. O arquivo de dados foi preservado."

    afastamentos = [
        registro
        for registro in preparar_registros(registros, agora.date())
        if registro["dias_restantes"] > 0
    ]
    afastamentos.sort(
        key=lambda registro: (
            registro["dias_restantes"],
            registro["colaborador"].casefold(),
            registro["colaborador"],
        )
    )
    registro_edicao_id = request.args.get("editar")
    registro_edicao = next(
        (
            registro
            for registro in afastamentos
            if str(registro.get("id", "")) == registro_edicao_id
        ),
        None,
    )
    mensagens = {
        "salvo": ("success", "Afastamento registrado com sucesso."),
        "atualizado": ("success", "Afastamento atualizado com sucesso."),
        "excluido": ("success", "Afastamento excluído com sucesso."),
        "nao_encontrado": ("error", "O registro não foi encontrado."),
        "invalido": ("error", "Confira os campos obrigatórios e as opções selecionadas."),
        "falha": ("error", "Não foi possível salvar o registro. Os dados anteriores foram preservados."),
    }
    resultado = request.args.get("resultado")
    mensagem = mensagens.get(resultado)

    return render_template(
        "index.html",
        data_atual=agora.strftime("%d/%m/%Y %H:%M:%S"),
        afastamentos=afastamentos,
        registro_edicao=registro_edicao,
        centros_custo=CENTROS_CUSTO,
        alocacoes=ALOCACOES,
        tipos_afastamento=TIPOS_AFASTAMENTO,
        contagens_centros={
            centro: sum(
                obter_grupo_centro(registro["centro_custo"]) == centro
                for registro in afastamentos
            )
            for centro in CENTROS_CUSTO
        },
        mensagem=mensagem,
        erro_dados=erro_dados,
    )


@app.route("/excluir/<registro_id>", methods=["POST"])
@requer_autenticacao
def excluir(registro_id):
    try:
        registros = carregar_registros()
    except DadosInvalidosError:
        return redirect(url_for("index", resultado="falha"))

    indice = next(
        (
            indice
            for indice, registro in enumerate(registros)
            if str(registro.get("id", "")) == registro_id
        ),
        None,
    )
    if indice is None:
        return redirect(url_for("index", resultado="nao_encontrado"))

    registros.pop(indice)
    try:
        salvar_registros(registros)
    except OSError:
        return redirect(url_for("index", resultado="falha"))

    return redirect(url_for("index", resultado="excluido"))


@app.route("/atualizar/<registro_id>", methods=["POST"])
@requer_autenticacao
def atualizar(registro_id):
    colaborador = request.form.get("colaborador", "").strip()
    matricula = request.form.get("matricula", "").strip()
    produto = request.form.get("produto", "").strip()
    centro_custo = request.form.get("centro_custo", "")
    tipo_afastamento = request.form.get("tipo_afastamento", "")
    data_inicio_texto = request.form.get("data_inicio", "")

    try:
        dias = int(request.form.get("dias", ""))
        data_inicio = date.fromisoformat(data_inicio_texto)
    except (TypeError, ValueError):
        return redirect(url_for("index", resultado="invalido"))

    if (
        not colaborador
        or len(colaborador) > 200
        or not matricula
        or len(matricula) > 50
        or not produto
        or len(produto) > 200
        or centro_custo not in ALOCACOES
        or tipo_afastamento not in TIPOS_AFASTAMENTO
        or not 1 <= dias <= 3650
    ):
        return redirect(url_for("index", resultado="invalido"))

    try:
        registros = carregar_registros()
        registro = next(
            (item for item in registros if str(item.get("id", "")) == registro_id),
            None,
        )
        if registro is None:
            return redirect(url_for("index", resultado="nao_encontrado"))
        registro.update(
            {
                "colaborador": colaborador,
                "matricula": matricula,
                "produto": produto,
                "centro_custo": centro_custo,
                "tipo_afastamento": tipo_afastamento,
                "dias": dias,
                "data_inicio": data_inicio.isoformat(),
            }
        )
        salvar_registros(registros)
    except (DadosInvalidosError, OSError):
        return redirect(url_for("index", resultado="falha"))

    return redirect(url_for("index", resultado="atualizado"))


@app.route("/calcular", methods=["POST"])
@requer_autenticacao
def calcular():
    colaborador = request.form.get("colaborador", "").strip()
    matricula = request.form.get("matricula", "").strip()
    produto = request.form.get("produto", "").strip()
    centro_custo = request.form.get("centro_custo", "")
    tipo_afastamento = request.form.get("tipo_afastamento", "")
    data_inicio_texto = request.form.get("data_inicio", "")

    try:
        dias = int(request.form.get("dias", ""))
        data_inicio = date.fromisoformat(data_inicio_texto)
    except (TypeError, ValueError):
        return redirect(url_for("index", resultado="invalido"))

    if (
        not colaborador
        or len(colaborador) > 200
        or not matricula
        or len(matricula) > 50
        or not produto
        or len(produto) > 200
        or centro_custo not in ALOCACOES
        or tipo_afastamento not in TIPOS_AFASTAMENTO
        or not 1 <= dias <= 3650
    ):
        return redirect(url_for("index", resultado="invalido"))

    novo_registro = {
        "id": uuid.uuid4().hex,
        "colaborador": colaborador,
        "matricula": matricula,
        "produto": produto,
        "centro_custo": centro_custo,
        "tipo_afastamento": tipo_afastamento,
        "dias": dias,
        "data_inicio": data_inicio.isoformat(),
        "criado_em": datetime.now(FUSO_RIO).isoformat(),
    }

    try:
        registros = carregar_registros()
        salvar_registros([*registros, novo_registro])
    except (DadosInvalidosError, OSError):
        return redirect(url_for("index", resultado="falha"))

    return redirect(url_for("index", resultado="salvo"))


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
