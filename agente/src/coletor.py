import json
import socket
import subprocess
from typing import Any

import psutil
import platform

try:
    import win32com.client
except ImportError:  # pragma: no cover - ambiente sem Outlook
    win32com = None


def executar_ps(comando):
    resultado = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            comando,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    if resultado.returncode != 0:
        return None

    return resultado.stdout.strip()


def coletar_versaoWindows():
    kernel = platform.system(), platform.release()
    
    return kernel

def nome_desktop():
    return socket.gethostname()


def usuario_ativo():
    comando = """
    $user = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    if ($user -and $user.Name) {
        $user.Name.Split('\\')[-1] | ConvertTo-Json -Compress
    } else {
        '""' | ConvertTo-Json -Compress
    }
    """

    try:
        saida = executar_ps(comando)
        usuario = json.loads(saida)

        if isinstance(usuario, str):
            return usuario

        return ""

    except Exception:
        return ""


def rede():
    for interface in psutil.net_if_addrs().values():
        ip = None
        mascara = None

        for endereco in interface:
            if endereco.family == socket.AF_INET:
                if endereco.address.startswith("127."):
                    continue

                ip = endereco.address
                mascara = endereco.netmask

        if ip:
            return ip, mascara

    return "", ""


def dns():
    comando = """
    (Get-DnsClientServerAddress -AddressFamily IPv4 |
    Where-Object {$_.ServerAddresses} |
    Select-Object -First 1 -ExpandProperty ServerAddresses |
    ConvertTo-Json -Compress)
    """

    try:
        servidores = json.loads(executar_ps(comando))

        if isinstance(servidores, list):
            return servidores

        return [servidores]

    except Exception:
        return []


def processador():
    comando = """
    (Get-CimInstance Win32_Processor).Name |
    ConvertTo-Json -Compress
    """

    try:
        return json.loads(executar_ps(comando)).strip()
    except Exception:
        return ""


def memoria_ram():
    comando = """
    $mem = Get-CimInstance Win32_PhysicalMemory

    $total = [math]::Round(($mem | Measure-Object Capacity -Sum).Sum /1GB)

    $vel = ($mem | Select-Object -First 1).Speed

    "$total GB $vel MHz" | ConvertTo-Json -Compress
    """

    try:
        return json.loads(executar_ps(comando))
    except Exception:
        return ""


def disco():
    comando = """
    $d = Get-CimInstance Win32_DiskDrive | Select-Object -First 1

    $tipo = if($d.MediaType -match "SSD"){ "SSD" }
            elseif($d.Model -match "SSD"){ "SSD" }
            else{ "SSD" }

    $tam = [math]::Round($d.Size/1GB)

    "$tipo $tam GB" | ConvertTo-Json -Compress
    """

    try:
        return json.loads(executar_ps(comando))
    except Exception:
        return ""


def espaco_livre_disco():
    comando = """
    $disco = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"

    $livre = [math]::Round($disco.FreeSpace / 1GB)

    "$livre GB" | ConvertTo-Json -Compress
    """

    try:
        return json.loads(executar_ps(comando))
    except Exception:
        return ""


def coletar_dados_brutos() -> dict[str, Any]:
    return {
        "nome_desktop": nome_desktop(),
        "nome_usuario": usuario_ativo(),
        "ip": rede()[0],
        "mascara": rede()[1],
        "dns": dns(),
        "configuracoes": {
            "processador": processador(),
            "memoria_ram": memoria_ram(),
            "disco": disco(),
            "disco_livre": espaco_livre_disco()
        },
    }


def obter_emails_outlook() -> list[str]:
    if win32com is None:
        return []

    emails: list[str] = []

    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")

        for conta in namespace.Accounts:
            email = str(conta.SmtpAddress or "").strip()

            if email and email not in emails:
                emails.append(email)

        return emails

    except Exception as erro:
        print(f"Não foi possível consultar o Outlook: {erro}")
        return []


def coletar_dados_completos() -> dict[str, Any]:
    dados = coletar_dados_brutos()
    dados["emails_outlook"] = obter_emails_outlook()
    dados["kernel"] = coletar_versaoWindows()
    return dados