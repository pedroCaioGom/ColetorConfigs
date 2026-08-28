from flask import Flask, request, jsonify, send_file
from insert_sheet import insert, search
from pathlib import Path
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

pasta_ti = os.getenv("pasta_version")

@app.route("/resultado", methods=["POST"])
def receber():
    dados = request.get_json()
    print(f"Dados {dados}")
    insert(
        id_planilha=dados["id_planilha"],
        email=dados["emails"],
        ip=dados["ip"],
        dns=dados["dns"],
        desktop=dados["desktop"],
        usuario=dados["usuario"],
        processador=dados["configuracoes"]["processador"],
        ram=dados["configuracoes"]["memoria_ram"],
        disco=dados["configuracoes"]["disco"],
        disco_livre=dados["configuracoes"]["disco_livre"],
        kernel=dados["kernel"]
    )
    return dados


@app.route("/enviar")
def enviar():
    id_planilha = search()
    return jsonify({
        "id_planilha": id_planilha
    }), 200


@app.route("/versao")
def versao_server():

    caminho_versao = Path(pasta_ti) / "version"

    versao = caminho_versao.read_text().split("=")[1]
    
    return (versao), 200


@app.route("/update")
def update():
    resposta = versao_server()
    
    dados = resposta[0]
   
    caminho_arquivo = (
        Path(pasta_ti) / dados
    )
    
    for arq in caminho_arquivo.glob("*.zip"):
        print("raiz ",caminho_arquivo)
        print("arquivoZip: ", arq)
    
    return send_file(
        str(arq),
        as_attachment=True,
        download_name="arquivosTI.zip",
        mimetype="application/octet-stream"
    )

@app.route("/arquivos")
def verificar_arquivos_exe():
    resposta = versao_server()
    
    dados = resposta[0]
   
    caminho_arquivo = (
        Path(pasta_ti) / dados
    )

    lista = []
    for arq in caminho_arquivo.glob("*.exe"):
        lista.append(arq.name)

    return lista


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)