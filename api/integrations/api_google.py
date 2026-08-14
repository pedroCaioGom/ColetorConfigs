from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class ApiGoogle:
    def __init__(self, service_account_file: str, spreadsheet_id: str):
        self.service_account_file = service_account_file
        self.spreadsheet_id = spreadsheet_id

    def __conexao_api_google(self):
        try:
            creds = Credentials.from_service_account_file(
                self.service_account_file,
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            print("Conexao bem sucedida!")
            return creds
        except HttpError as err:
            print(f"Erro na API do Google: {err}")


    def ler_planilha(self, range_name: str):
        """
        Lê os valores de uma planilha do Google Sheets.
        Args:
            range_name (str): O intervalo a ser lido (por exemplo, "Sheet1!A1:C10").
        Returns:
            list: Uma lista de listas contendo os valores da planilha.
        exemplo de uso:

        """
        creds = self.__conexao_api_google()
        try:
            service = build(
                "sheets",
                "v4",
                credentials=creds
            )

            sheet = service.spreadsheets()

            result = (
                sheet
                .values()
                .get(spreadsheetId=self.spreadsheet_id, range=range_name)
                .execute()
            )

            
            values = result.get("values", [])
            print(f"{len(values)} range")
            return values
        except HttpError as e:
            print(f"Erro ao ler a planilha: {e}")
            return None

        
    def ler_multiplos_intervalos(self, range_names:list[str]):
        """
        Uso da função batchGet para ler múltiplos intervalos de uma planilha do Google Sheets.
        Args:
            range_names (list[str]): Uma lista de intervalos a serem lidos.
        Returns:
            list: Uma lista de dicionários contendo os valores dos intervalos especificados.

        exemplo de uso:

        range_names = ["c1:c500", "d1:d500"]
        resultado = lendo_multiplos_intervalos(spreadsheet_id=SPREADSHEET_ID,range_names=range_names)
        print(resultado)

        """
        creds = self.__conexao_api_google()
        try:
            service = build(
                "sheets",
                "v4",
                credentials=creds
            )

            sheet = service.spreadsheets()

            result = (
                sheet
                .values()
                .batchGet(spreadsheetId=self.spreadsheet_id, ranges=range_names)
                .execute()
            )

            values = result.get("valueRanges", [])
            print(f"{len(values)} ranges")
            return values
        except HttpError as e:
            print(f"Erro ao ler a planilha: {e}")
            return None


    def gravar_planilha(self, range_name: str, value_input_option: str, values:list[str]):
        """
        Uso da função update para inserir valores em uma planilha do Google Sheets.
        Args:
            range_name (str): A partir de qual linha vai ser inserido.
            value_input_option (str): RAW ou USER_ENTERED
            values (list[str]): Valores para inserir
        Returns:
            retorna uma lista das colunas que foram atualizadas

        exemplo de uso:

        email="pedro.caio@gomidecontabilidade.com.br"
        senha_pc="senha"
        ip="192.168.0.1"
        dns="0.0.0.0"

        gravar_planilha(
            spreadsheet_id=SPREADSHEET_ID, 
            range_name="inventario!B3",
            value_input_option="RAW",
            values=[[email, senha_pc, ip, dns]]
        )
        """

        creds = self.__conexao_api_google()
        try:
            service = build(
                "sheets",
                "v4",
                credentials=creds
            )

            body = {"values": values}

            sheet = service.spreadsheets()

            result = (
                sheet
                .values()
                .update(
                    spreadsheetId=self.spreadsheet_id, 
                    range=range_name, 
                    valueInputOption=value_input_option,
                    body=body
                    )
                .execute()
            )
            print(f"{result.get('updatedCells')} cells updated.")
            return result
        except HttpError as e:
            print(f"Erro ao preencher a planilha do google")
            return e


    def gravar_multiplos_intervalos(self, range_name: str, value_input_option: str, values:list[str]):
        """
        Uso da função update para inserir valores em uma planilha do Google Sheets.
        Args:
            range_name (str): A partir de qual linha vai ser inserido.
            value_input_option (str): RAW ou USER_ENTERED
            values (list[str]): Valores para inserir
        Returns:
            retorna uma lista das colunas que foram atualizadas

        exemplo de uso:

        gravar_multiplos_intervalos(
            spreadsheet_id=SPREADSHEET_ID,
            range_name="B4",
            value_input_option="USER_ENTERED",
            values=[["F", "B"], ["C", "D"]]
        )
        """
        creds = self.__conexao_api_google()
        try:
            service = build(
                "sheets",
                "v4",
                credentials=creds
            )
            data = {"range": range_name, "values": values}

            body = {"valueInputOption": value_input_option, "data": data}

            sheet = service.spreadsheets()

            result = (
                sheet
                .values()
                .batchUpdate(
                    spreadsheetId=self.spreadsheet_id,
                    body=body
                )
                .execute()
            )
            print(f"{(result.get('totalUpdatedCells'))} cells updated.")
            return result
        except HttpError as e:
            print(f"Erro ao inserir dados na planilha do Google!")
            return e