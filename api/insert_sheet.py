from integrations.api_google import ApiGoogle
from dotenv import load_dotenv
import os


load_dotenv()

spreadsheet_id = "1Nau6hVRhjeF1dqI_vMeWk8FoJDgF78tsdTCTH8ykVs8"

api = ApiGoogle(
    service_account_file="service_account.json",
    spreadsheet_id=spreadsheet_id
)


"""
    email:str, 
    ip: str, 
    dns: str, 
    desktop: str, 
    usuario: str, 
    processador: str,
    ram: str,
    disco: str,
    kernel: str    
"""
def search() -> str:  
    i = 2

    worksheet = api.ler_planilha(range_name=f"inventario!A2:L500")
    
    for row in worksheet:
        if len(row)<=1:
            print(f"Id da linha: {row[0]}")
            id_linha = row[0]
            api.gravar_planilha(f"inventario!B{row[0]}", value_input_option="RAW", values=["-"])
            break
        i += 1

    return id_linha


def insert(
    id_planilha,
    departamento:str,
    email:str, 
    senha_pc:str,
    ip: str, 
    dns: str, 
    desktop: str, 
    usuario: str, 
    processador: str,
    ram: str,
    disco: str,
    disco_livre: str,
    kernel: str
):
    j = int(id_planilha)
    i = j + 1
    
    print(f"Linha atual {i}")
    range_name = f"inventario!B{i}:M{i}"

    saida = api.gravar_planilha(
    range_name=range_name, 
    value_input_option="RAW",
    values=[[departamento, email, senha_pc, ip, dns, desktop, usuario, processador, ram, disco, disco_livre, kernel]]
    )
    print(saida)


if __name__ == "__main__":
    a=insert(
        id_planilha=2,
        email="",
        ip="192.168.0.100",
        dns="192.168.0.1",
        desktop="TI",
        usuario="TI-05",
        processador="Ryzen",
        ram="8gb",
        disco="ssd 240gb",
        disco_livre="228gb",
        kernel="Win 11"
    )
    print(type(a))