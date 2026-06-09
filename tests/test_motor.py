"""Testes para motor — _transformar, _build_filtro e processar (use case)."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import pytest
from modulos.motor import _transformar, _build_filtro, processar

_LINHA_BASE = {
    "coAno": "2026", "coMes": "04",
    "coNcm": "02102000", "noNcmpt": "Carnes de bovinos salgadas",
    "coIsicClass": "1010", "noIsicClasspt": "Processamento de carne",
    "coCgceN3": "324",     "noCgceN3pt": "Alimentos elaborados",
    "coCuciItem": "01681", "noCuciItempt": "Carne de bovinos",
    "noPaispt": "Angola",  "noUf": "São Paulo",
    "noVia": "MARITIMA",   "noUrf": "0817800 - PORTO DE SANTOS",
    "vlFob": "130824",     "kgLiquido": "22050",
}

_COLUNAS_ESPERADAS = [
    "Mês",
    "Código ISIC Classe", "Descrição ISIC Classe",
    "Código CGCE Nível 3", "Descrição CGCE Nível 3",
    "Código CUCI Item", "Descrição CUCI Item",
    "Países", "UF do Produto", "Via", "URF",
    "Código NCM", "Descrição NCM",
    "2026 - Valor US$ FOB", "2026 - Quilograma Líquido",
]


def _df(**overrides):
    return pd.DataFrame([{**_LINHA_BASE, **overrides}])


# ── _transformar ──────────────────────────────────────────────────────────────

def test_ordem_e_nomes_de_colunas():
    assert list(_transformar(_df()).columns) == _COLUNAS_ESPERADAS


def test_mes_formatado():
    assert _transformar(_df(coMes="01"))["Mês"].iloc[0] == "01. Janeiro"
    assert _transformar(_df(coMes="06"))["Mês"].iloc[0] == "06. Junho"
    assert _transformar(_df(coMes="12"))["Mês"].iloc[0] == "12. Dezembro"


def test_ncm_convertido_para_inteiro():
    df = _transformar(_df())
    assert df["Código NCM"].iloc[0] == 2102000
    assert str(df["Código NCM"].dtype) == "Int64"


def test_metricas_convertidas_para_inteiro():
    df = _transformar(_df())
    assert df["2026 - Valor US$ FOB"].iloc[0] == 130824
    assert df["2026 - Quilograma Líquido"].iloc[0] == 22050
    assert str(df["2026 - Valor US$ FOB"].dtype) == "Int64"


def test_nome_coluna_metrica_usa_ano():
    df = _transformar(_df(coAno="2025"))
    assert "2025 - Valor US$ FOB" in df.columns
    assert "2026 - Valor US$ FOB" not in df.columns


def test_rename_completo_de_colunas_api():
    nomes_api = {"coNcm", "noNcmpt", "coIsicClass", "noIsicClasspt",
                 "coCgceN3", "noCgceN3pt", "coCuciItem", "noCuciItempt",
                 "noPaispt", "noUf", "noVia", "noUrf", "vlFob", "kgLiquido"}
    assert nomes_api.isdisjoint(set(_transformar(_df()).columns))


def test_dataframe_vazio_retorna_vazio():
    assert _transformar(pd.DataFrame()).empty


# ── _build_filtro ─────────────────────────────────────────────────────────────

def test_build_filtro_estrutura():
    ncms = ["02102000", "02013000"]
    periodo = {"from": "2026-01", "to": "2026-06"}
    f = _build_filtro(ncms, periodo)
    assert f["yearStart"] == "2026"
    assert f["yearEnd"] == "2026"
    assert f["monthStart"] == "01"
    assert f["monthEnd"] == "06"
    assert f["filterArray"][0]["item"] == ncms
    assert f["metricFOB"] is True
    assert f["metricKG"] is True
    assert len(f["detailDatabase"]) == 8


# ── processar (use case) ──────────────────────────────────────────────────────

def test_processar_levanta_categoria_invalida():
    with pytest.raises(ValueError, match="Categoria desconhecida"):
        processar("invalida", consultar=lambda f: pd.DataFrame(), salvar=lambda df, d: "")


def test_processar_levanta_se_api_retorna_vazio():
    with pytest.raises(ValueError, match="zero registros"):
        processar("bovino", consultar=lambda f: pd.DataFrame(), salvar=lambda df, d: "")


def test_processar_transforma_e_salva():
    chamadas = []

    def mock_consultar(filtro):
        assert "yearStart" in filtro
        assert filtro["filterArray"][0]["item"]
        return pd.DataFrame([_LINHA_BASE])

    def mock_salvar(df, destino):
        chamadas.append(df)
        return destino

    processar("bovino", consultar=mock_consultar, salvar=mock_salvar)

    assert len(chamadas) == 1
    assert list(chamadas[0].columns) == _COLUNAS_ESPERADAS
