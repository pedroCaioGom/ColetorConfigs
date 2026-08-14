from src.envio import verificacao_e_envio
import requests
import subprocess

def tarefa_semanal():
    comando = [
        "schtasks",
        "/create",
        "/tn", "InventarioTI Semanal",
        "/tr", 
    ]

def receber_api():
    url = "http://127.0.0.1:5000/enviar"
    resposta = requests.get(url)

    dados = resposta.json()

    id_planilha = dados["id_planilha"]
    print(id_planilha)

    return dados

def enviar_api():
    url = "http://127.0.0.1:5000/resultado"
    resposta = requests.post(url, json=verificacao_e_envio())

    print(f"resposta {resposta.status_code}")
    print(f"resposta json {resposta.json()}")


if __name__ == "__main__":
    enviar_api()