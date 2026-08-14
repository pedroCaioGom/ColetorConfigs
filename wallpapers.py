from pathlib import Path
import shutil
from pathlib import Path
from ctypes import c_uint, c_wchar_p, POINTER
from comtypes import (
    GUID,
    IUnknown,
    HRESULT,
    COMMETHOD,
)
from comtypes.client import CreateObject
from pathlib import Path
import subprocess
import ctypes
import sys


CLSID_DESKTOP_WALLPAPER = GUID(
    "{C2CF3110-460E-4FC1-B9D0-8A1C0C9CC4BD}"
)

IID_IDESKTOP_WALLPAPER = GUID(
    "{B92B56A9-8B55-4E14-9A89-0199BBB6F93B}"
)


class IDesktopWallpaper(IUnknown):
    _iid_ = IID_IDESKTOP_WALLPAPER

    _methods_ = [
        COMMETHOD(
            [],
            HRESULT,
            "SetWallpaper",
            (["in"], c_wchar_p, "monitorID"),
            (["in"], c_wchar_p, "wallpaper"),
        ),

        COMMETHOD(
            [],
            HRESULT,
            "GetWallpaper",
            (["in"], c_wchar_p, "monitorID"),
            (["out"], POINTER(c_wchar_p), "wallpaper"),
        ),

        COMMETHOD(
            [],
            HRESULT,
            "GetMonitorDevicePathAt",
            (["in"], c_uint, "monitorIndex"),
            (["out"], POINTER(c_wchar_p), "monitorID"),
        ),

        COMMETHOD(
            [],
            HRESULT,
            "GetMonitorDevicePathCount",
            (["out"], POINTER(c_uint), "count"),
        ),
    ]


def wallpaper_tela_principal(caminho_pasta: str):

    pasta = Path(caminho_pasta)

    if not pasta.exists():
        raise FileNotFoundError(
            f"Pasta não encontrada: {caminho_pasta}"
        )

    extensoes = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
    }

    imagens = sorted(
        [
            arquivo.resolve()
            for arquivo in pasta.iterdir()
            if arquivo.is_file()
            and arquivo.suffix.lower() in extensoes
        ],
        key=lambda x: x.name
    )

    if not imagens:
        raise FileNotFoundError(
            f"Nenhum wallpaper encontrado em: {caminho_pasta}"
        )

    wallpaper = CreateObject(
        CLSID_DESKTOP_WALLPAPER,
        interface=IDesktopWallpaper
    )

    quantidade_monitores = (
        wallpaper.GetMonitorDevicePathCount()
    )

    print(
        f"Monitores encontrados: {quantidade_monitores}"
    )

    print(
        f"Wallpapers encontrados: {len(imagens)}"
    )

    # ======================================
    # APENAS UMA IMAGEM
    # ======================================

    if len(imagens) == 1:

        imagem = str(imagens[0])

        # monitorID = None significa todos os monitores
        wallpaper.SetWallpaper(
            None,
            imagem
        )

        print(
            f"Wallpaper aplicado em todos os monitores: "
            f"{imagens[0].name}"
        )

        return

    # ======================================
    # MAIS DE UMA IMAGEM
    # ======================================

    for indice in range(quantidade_monitores):

        monitor = (
            wallpaper.GetMonitorDevicePathAt(indice)
        )

        imagem = imagens[
            indice % len(imagens)
        ]

        wallpaper.SetWallpaper(
            monitor,
            str(imagem)
        )

        print(
            f"Monitor {indice + 1}: "
            f"{imagem.name}"
        )