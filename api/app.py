from flask import Flask, request, jsonify
from api.insert_sheet import insert, search

app = Flask(__name__)

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


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)