"""
Use case da automação COMEX STAT.

Responsabilidades:
- Montar o payload de consulta à API (_build_filtro)
- Transformar o DataFrame bruto para o formato esperado pelo Power BI (_transformar)
- Orquestrar o fluxo completo para uma categoria (processar)

Este módulo não contém nenhum I/O. Os adaptadores de infraestrutura (HTTP e Excel)
são injetados como parâmetros em processar(), tornando o módulo 100% testável
sem depender de rede, sistema de arquivos ou bibliotecas externas de I/O.
"""
from collections.abc import Callable

import pandas as pd

from modulos.config import API_PERIODO, CATEGORIAS

# Mapeamento de número de mês para o formato textual usado no Power BI
_MESES_PT = {
    "1":  "01. Janeiro",   "2":  "02. Fevereiro", "3":  "03. Março",
    "4":  "04. Abril",     "5":  "05. Maio",       "6":  "06. Junho",
    "7":  "07. Julho",     "8":  "08. Agosto",     "9":  "09. Setembro",
    "10": "10. Outubro",   "11": "11. Novembro",   "12": "12. Dezembro",
}

# Schema de colunas que a API deve retornar — cada entrada representa um campo de detalhamento.
# Alterar aqui exige atualizar também _COLUNAS_RENAME e _transformar.
_DETAIL_DATABASE = [
    {"id": "noNcmpt",       "text": "NCM",          "parentId": "coNcm",       "parent": "Código NCM",          "group": "sh",   "groupText": "SH"},
    {"id": "noIsicClasspt", "text": "ISIC Classe",  "parentId": "coIsicClass", "parent": "Código ISIC Classe",  "group": "isic", "groupText": "ISIC"},
    {"id": "noCgceN3pt",    "text": "CGCE Nível 3", "parentId": "coCgceN3",    "parent": "Código CGCE Nível 3", "group": "cgce", "groupText": "CGCE"},
    {"id": "noCuciItempt",  "text": "CUCI Item",    "parentId": "coCuciItem",  "parent": "Código CUCI Item",    "group": "cuci", "groupText": "CUCI"},
    {"id": "noPaispt",      "text": "País",          "group": "gerais", "groupText": "Gerais"},
    {"id": "noUf",          "text": "UF do Produto", "group": "gerais", "groupText": "Gerais"},
    {"id": "noVia",         "text": "Via",           "group": "gerais", "groupText": "Gerais"},
    {"id": "noUrf",         "text": "URF",           "group": "gerais", "groupText": "Gerais"},
]

# Mapeamento dos nomes internos da API para os nomes de negócio exibidos no Power BI.
# A ordem das colunas no Excel é controlada por _transformar, não por este dicionário.
_COLUNAS_RENAME = {
    "coNcm":         "Código NCM",
    "noNcmpt":       "Descrição NCM",
    "coIsicClass":   "Código ISIC Classe",
    "noIsicClasspt": "Descrição ISIC Classe",
    "coCgceN3":      "Código CGCE Nível 3",
    "noCgceN3pt":    "Descrição CGCE Nível 3",
    "coCuciItem":    "Código CUCI Item",
    "noCuciItempt":  "Descrição CUCI Item",
    "noPaispt":      "Países",
    "noUf":          "UF do Produto",
    "noVia":         "Via",
    "noUrf":         "URF",
}


def processar(
    categoria: str,
    *,
    consultar: Callable[[dict], pd.DataFrame],
    salvar: Callable[[pd.DataFrame, str], str],
) -> str:
    """
    Executa o pipeline completo para uma categoria: consulta → transforma → salva.

    Os adaptadores de I/O são recebidos por injeção de dependência (keyword-only)
    para manter este módulo desacoplado da infraestrutura e facilitar testes.
    Em produção, app.py injeta repositorio.consultar e repositorio.salvar.
    Em testes, lambdas ou funções mock são passadas diretamente.

    Args:
        categoria: Chave em CATEGORIAS (ex: "bovino", "frango").
        consultar: Função que recebe o filtro dict e retorna um DataFrame com os dados da API.
        salvar:    Função que recebe o DataFrame transformado e o destino e retorna o caminho salvo.

    Returns:
        Caminho absoluto do arquivo .xlsx gerado.

    Raises:
        ValueError: Se a categoria não existir em CATEGORIAS.
        ValueError: Se a API retornar 0 registros para a categoria no período configurado.
    """
    if categoria not in CATEGORIAS:
        raise ValueError(f"Categoria desconhecida: '{categoria}'. Válidas: {list(CATEGORIAS)}")

    cfg = CATEGORIAS[categoria]

    # Monta o payload e delega a chamada HTTP ao adaptador injetado
    filtro = _build_filtro(cfg["ncms"], API_PERIODO)
    df = consultar(filtro)

    # DataFrame vazio indica que a API não retornou dados — não faz sentido salvar um arquivo vazio
    if df.empty:
        raise ValueError(f"API retornou zero registros para '{categoria}' no período {API_PERIODO}")

    df = _transformar(df)
    return salvar(df, cfg["destino"])


def _build_filtro(ncms: list, periodo: dict) -> dict:
    """
    Monta o payload JSON que a API COMEX STAT espera como query param 'filter'.

    Os campos typeForm=1 e typeOrder=2 são valores fixos da API que controlam
    o formato e a ordenação da resposta — não há documentação pública sobre outros valores.
    metricStatistic, metricFreight, metricInsurance e metricCIF são desabilitados
    porque só FOB e KG são necessários para o Power BI.

    Args:
        ncms:    Lista de códigos NCM (strings de 8 dígitos).
        periodo: Dict com chaves 'from' e 'to' no formato 'YYYY-MM'.

    Returns:
        Dict pronto para ser serializado com json.dumps e enviado à API.
    """
    ano_inicio, mes_inicio = periodo["from"].split("-")
    ano_fim,    mes_fim    = periodo["to"].split("-")
    return {
        "yearStart": ano_inicio,
        "yearEnd":   ano_fim,
        "typeForm":  1,   # formato geral de exportação
        "typeOrder": 2,   # ordenação por valor
        "filterList": [{"id": "noNcmpt", "text": "NCM", "route": "/pt/product/ncm",
                        "type": "2", "group": "sh", "groupText": "SH",
                        "hint": "fieldsForm.general.noNcm.description",
                        "placeholder": "NCM"}],
        "filterArray":    [{"item": ncms, "idInput": "noNcmpt"}],
        "rangeFilter":    [],
        "detailDatabase": _DETAIL_DATABASE,
        "monthDetail":     True,   # detalha por mês (não só por ano)
        "metricFOB":       True,
        "metricKG":        True,
        "metricStatistic": False,
        "metricFreight":   False,
        "metricInsurance": False,
        "metricCIF":       False,
        "monthStart":  mes_inicio,
        "monthEnd":    mes_fim,
        "formQueue":   "general",
        "langDefault": "pt",
    }


def _transformar(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma o DataFrame bruto da API para o formato esperado pelo Power BI.

    Operações aplicadas:
    1. Formata o mês numérico para texto localizado ("04" → "04. Abril")
    2. Cria colunas de métrica com o ano no nome ("2026 - Valor US$ FOB")
    3. Renomeia todos os campos internos da API para nomes de negócio
    4. Converte Código NCM, FOB e KG para Int64 (sem decimais no Excel)
    5. Seleciona e ordena as 15 colunas finais — esta ordem é um contrato com o Power BI

    Args:
        df: DataFrame com as colunas brutas retornadas pela API.

    Returns:
        DataFrame com 15 colunas ordenadas, pronto para gravação em Excel.
        Retorna df vazio sem processamento se df.empty.
    """
    if df.empty:
        return df

    # O ano vem do próprio dado — garante que o nome da coluna reflita o período real consultado
    ano = df["coAno"].iloc[0]
    col_fob = f"{ano} - Valor US$ FOB"
    col_kg  = f"{ano} - Quilograma Líquido"

    df = df.copy()

    # Converte o mês numérico (string) para o formato textual usado como filtro no Power BI
    df["Mês"]   = df["coMes"].astype(int).astype(str).map(_MESES_PT)

    # Converte métricas para inteiro — a API retorna strings; Int64 preserva nulos sem virar float
    df[col_fob] = pd.to_numeric(df["vlFob"],     errors="coerce").astype("Int64")
    df[col_kg]  = pd.to_numeric(df["kgLiquido"], errors="coerce").astype("Int64")

    # Renomeia todas as colunas da API para os nomes de negócio antes de selecionar
    df = df.rename(columns=_COLUNAS_RENAME)

    # NCM vem como string com zeros à esquerda ("02102000") — converte para inteiro para facilitar filtros no BI
    df["Código NCM"] = pd.to_numeric(df["Código NCM"], errors="coerce").astype("Int64")

    # Seleciona e ordena as 15 colunas finais — qualquer alteração aqui quebra os visuais do Power BI
    return df[[
        "Mês",
        "Código ISIC Classe", "Descrição ISIC Classe",
        "Código CGCE Nível 3", "Descrição CGCE Nível 3",
        "Código CUCI Item", "Descrição CUCI Item",
        "Países", "UF do Produto", "Via", "URF",
        "Código NCM", "Descrição NCM", col_fob, col_kg,
    ]]
