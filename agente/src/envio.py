import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from .coletor import coletar_dados_completos


def __padronizar_para_api(id_planilha) -> dict:
    dados = coletar_dados_completos()

    return {
        "id_planilha": id_planilha,
        "desktop": dados.get("nome_desktop", ""),
        "usuario": dados.get("nome_usuario", ""),
        "ip": dados.get("ip", ""),
        "mascara": dados.get("mascara", ""),
        "dns": " | ".join(dados.get("dns", [])),
        "configuracoes": {
            "processador": dados.get("configuracoes", {}).get("processador", ""),
            "memoria_ram": dados.get("configuracoes", {}).get("memoria_ram", ""),
            "disco": dados.get("configuracoes", {}).get("disco", ""),
            "disco_livre": dados.get("configuracoes", {}).get("disco_livre", "")
        },
        "emails": " | ".join(dados.get("emails_outlook", [])),
        "kernel": " ".join(dados.get("kernel", []))
    }


def verificacao_e_envio():
    import os, json
    from main import receber_api

    local__appdata = Path(os.getenv("LOCALAPPDATA"))
    pasta = local__appdata / "InventarioTI"
    arquivo = pasta / "id_planilha.json"

    if not pasta.exists():
        pasta.mkdir()

    if not arquivo.is_file():
        print("Arquivo não existe ou não encontrado!\n Criando!")

        id_planilha = receber_api()

        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(id_planilha, f, ensure_ascii=False)

        
    with open(arquivo, "r", encoding="utf-8") as f:
        dados = json.load(f)

    id_planilha = dados["id_planilha"]
    saida = __padronizar_para_api(id_planilha)
    return saida