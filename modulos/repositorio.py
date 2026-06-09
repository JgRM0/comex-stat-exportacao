"""
Adaptadores de infraestrutura da automação COMEX STAT.

Responsabilidades:
- consultar(): realiza a chamada HTTP à API com retry automático
- salvar():    persiste o DataFrame transformado como arquivo .xlsx

Este módulo encapsula todo o I/O do sistema. motor.py não importa este módulo
diretamente — os adaptadores são injetados via parâmetros em motor.processar(),
mantendo o use case desacoplado da infraestrutura.
"""
import json
import os
import time

import pandas as pd
from curl_cffi import requests as cr

from modulos.config import API_URL, CHROME_IMPERSONATE, NOME_ARQUIVO

# Sessão reutilizada entre todas as chamadas para evitar overhead de handshake TLS.
# impersonate replica o fingerprint TLS do Chrome — necessário para contornar o Cloudflare da API.
_session = cr.Session(impersonate=CHROME_IMPERSONATE)


def consultar(filtro: dict) -> pd.DataFrame:
    """
    Executa GET na API COMEX STAT e retorna os dados como DataFrame.

    A API espera o payload como query param 'filter' serializado em JSON.
    Implementa retry com back-off linear para tratar rate limiting (HTTP 429):
    - 1ª tentativa sem espera
    - 2ª tentativa após 30s
    - 3ª tentativa após 60s
    - Se a 3ª também falhar, lança RuntimeError

    Args:
        filtro: Payload da consulta, conforme montado por motor._build_filtro().

    Returns:
        DataFrame com uma linha por registro retornado pela API.
        Retorna DataFrame vazio se a API retornar lista vazia.

    Raises:
        RuntimeError: Rate limit persistente após 3 tentativas consecutivas.
        HTTPError:    Qualquer outro erro HTTP (4xx, 5xx).
    """
    # A API não aceita o dict diretamente — precisa ser uma string JSON no query param
    filtro_str = json.dumps(filtro, ensure_ascii=False)

    for tentativa in range(1, 4):
        resp = _session.get(API_URL, params={"filter": filtro_str}, timeout=60)

        if resp.status_code == 429:
            if tentativa < 3:
                # Back-off linear: 30s na 1ª falha, 60s na 2ª — reduz pressão sobre o rate limit
                time.sleep(30 * tentativa)
                continue
            raise RuntimeError("Rate limit persistente após 3 tentativas")

        # Lança HTTPError para qualquer outro status de erro (4xx, 5xx)
        resp.raise_for_status()

        # A API retorna { "data": { "list": [...] } } — extraímos apenas a lista de registros
        return pd.DataFrame(resp.json().get("data", {}).get("list", []))


def salvar(df: pd.DataFrame, destino: str) -> str:
    """
    Persiste o DataFrame como arquivo .xlsx no diretório informado.

    Cria o diretório de destino se não existir (include subdiretórios).
    O nome do arquivo é lido de config.NOME_ARQUIVO para manter centralização.

    Args:
        df:      DataFrame transformado por motor._transformar(), pronto para gravação.
        destino: Caminho absoluto da pasta de destino (vem de CATEGORIAS[categoria]["destino"]).

    Returns:
        Caminho absoluto do arquivo .xlsx gerado.
    """
    # exist_ok=True evita erro se o diretório já existir (execuções repetidas)
    os.makedirs(destino, exist_ok=True)
    caminho = os.path.join(destino, NOME_ARQUIVO)
    df.to_excel(caminho, index=False, engine="openpyxl")
    return caminho
