import os
import queue
import threading
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file

from insert_sheet import insert, search

load_dotenv()

app = Flask(__name__)

pasta_ti = Path(__file__).parent / "version"

# =========================================================
# Infraestrutura da fila FIFO
# =========================================================
# Um único worker thread processa os jobs em ordem de chegada.
# Isso garante que search() e insert() nunca rodem em paralelo,
# eliminando a condição de corrida em que dois usuários pegam
# o mesmo id_planilha ao chamar /enviar quase simultaneamente.
#
# IMPORTANTE: essa solução funciona enquanto o app rodar em um
# único processo (ex: `python app.py`, ou gunicorn/uwsgi com
# --workers 1 --threads N). Se no futuro você escalar para
# múltiplos processos, a fila em memória deixa de ser compartilhada
# entre eles e será necessário um mecanismo externo (Redis, lock
# no banco, Celery, etc).

fila = queue.Queue()


def _worker():
    while True:
        job = fila.get()
        try:
            if job["tipo"] == "enviar":
                id_planilha = search()
                job["resultado"] = {"id_planilha": id_planilha}

            elif job["tipo"] == "resultado":
                insert(**job["dados"])
                job["resultado"] = {"status": "ok"}

            else:
                job["erro"] = f"Tipo de job desconhecido: {job['tipo']}"

        except Exception as e:
            job["erro"] = str(e)

        finally:
            job["evento"].set()
            fila.task_done()


_worker_thread = threading.Thread(target=_worker, daemon=True)
_worker_thread.start()


def executar_na_fila(tipo, dados=None, timeout=30):
    """
    Enfileira um job e bloqueia a requisição HTTP atual até que
    o worker processe esse job especificamente (respeitando a
    ordem FIFO de chegada). Levanta exceção se der erro ou timeout.
    """
    job = {"tipo": tipo, "dados": dados, "evento": threading.Event()}
    fila.put(job)

    concluido = job["evento"].wait(timeout=timeout)
    if not concluido:
        raise TimeoutError(f"Job '{tipo}' não foi processado a tempo (timeout={timeout}s)")

    if "erro" in job:
        raise RuntimeError(job["erro"])

    return job["resultado"]


# =========================================================
# Rotas
# =========================================================

@app.route("/resultado", methods=["POST"])
def receber():
    dados = request.get_json()
    print(f"Dados {dados}")

    try:
        payload = dict(
            id_planilha=dados["id_planilha"],
            departamento=dados["departamento"],
            email=dados["emails"],
            senha_pc=dados["senha_pc"],
            ip=dados["ip"],
            dns=dados["dns"],
            desktop=dados["desktop"],
            usuario=dados["usuario"],
            processador=dados["configuracoes"]["processador"],
            ram=dados["configuracoes"]["memoria_ram"],
            disco=dados["configuracoes"]["disco"],
            disco_livre=dados["configuracoes"]["disco_livre"],
            kernel=dados["kernel"],
        )
    except KeyError as e:
        return jsonify({"erro": f"Campo ausente no payload: {e}"}), 400

    try:
        executar_na_fila("resultado", payload)
    except TimeoutError as e:
        return jsonify({"erro": str(e)}), 504
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

    return jsonify(dados), 200


@app.route("/enviar")
def enviar():
    try:
        resultado = executar_na_fila("enviar")
    except TimeoutError as e:
        return jsonify({"erro": str(e)}), 504
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

    return jsonify(resultado), 200


@app.route("/versao")
def versao_server():
    caminho_versao = Path(pasta_ti) / "version.txt"
    versao = caminho_versao.read_text().split("=")[1].strip()
    return (versao), 200


@app.route("/update")
def update():
    resposta = versao_server()
    dados = resposta[0]

    caminho_arquivo = Path(pasta_ti) / dados

    arq = None
    for arq in caminho_arquivo.glob("*.zip"):
        print("raiz ", caminho_arquivo)
        print("arquivoZip: ", arq)

    if arq is None:
        return jsonify({"erro": f"Nenhum .zip encontrado em {caminho_arquivo}"}), 404

    return send_file(
        str(arq),
        as_attachment=True,
        download_name="arquivosTI.zip",
        mimetype="application/octet-stream",
    )


@app.route("/arquivos")
def verificar_arquivos_exe():
    resposta = versao_server()
    dados = resposta[0]

    caminho_arquivo = Path(pasta_ti) / dados

    lista = [arq.name for arq in caminho_arquivo.glob("*.exe")]
    return jsonify(lista), 200


if __name__ == "__main__":
    # threaded=True é o padrão do Flask dev server, mantém as requisições
    # concorrentes normalmente — só o acesso à planilha fica serializado
    # pela fila acima.
    app.run(host="0.0.0.0", port=5000, threaded=True)