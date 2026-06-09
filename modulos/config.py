"""
Única fonte de verdade para toda parametrização da automação COMEX STAT.

Nenhum outro módulo deve definir URLs, caminhos, NCMs ou parâmetros fixos.
Para trocar de ambiente (teste ↔ produção), altere apenas MODO_TESTE.
Para adicionar uma categoria, adicione uma entrada em CATEGORIAS.
"""
import os
from datetime import datetime

# Capturados uma vez na inicialização — usados no período de consulta e no nome do arquivo
_ANO = datetime.now().year
_MES = datetime.now().month

# Mude para False para salvar no destino de produção configurado em COMEX_DESTINO_PROD
MODO_TESTE = True

# Endpoint público da API COMEX STAT (MDIC) — sem autenticação, protegido por Cloudflare
API_URL = "https://api-comexstat.mdic.gov.br/general"

# Perfil de TLS que o curl_cffi imita para contornar o Cloudflare.
# Chrome120 foi validado como funcional; se começarem a aparecer erros 403, atualizar aqui.
CHROME_IMPERSONATE = "chrome120"

# Janela temporal da consulta: sempre de janeiro até o mês atual do ano corrente.
# Em produção, atualiza automaticamente a cada execução mensal.
API_PERIODO = {
    "from": f"{_ANO}-01",
    "to":   f"{_ANO}-{_MES:02d}",
}

# Nome do arquivo gerado — inclui o ano para facilitar a identificação histórica no Power BI
NOME_ARQUIVO = f"H_EXPORTACAO_GERAL_{_ANO}.xlsx"

# Caminhos base para saída dos arquivos Excel
# Em produção, configure a variável de ambiente COMEX_DESTINO_PROD com o caminho de destino
_BASE_PROD  = os.environ.get("COMEX_DESTINO_PROD", "")
_BASE_TESTE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp", "saida")

# Seleciona o caminho ativo conforme o modo
_BASE = _BASE_TESTE if MODO_TESTE else _BASE_PROD

# Cada entrada define os NCMs consultados e a pasta de destino do arquivo Excel.
# Para adicionar uma nova categoria: inserir uma nova chave aqui — nenhum outro arquivo precisa ser alterado.
CATEGORIAS: dict[str, dict] = {
    "bovino": {
        "destino": os.path.join(_BASE, "Bovino"),
        "ncms": [
            "02102000", "02013000", "02061000", "02023000", "05040011", "02062910",
            "02062200", "02062100", "16025000", "02012020", "02012010", "02022010",
            "02022020", "02011000", "02012090", "02021000", "02022090", "02062990",
        ],
    },
    "frango": {
        "destino": os.path.join(_BASE, "Frango"),
        "ncms": [
            "01051110", "01051190", "01063900", "15019000", "16021000", "16023210",
            "16023220", "16023230", "16023290", "02071100", "02071200", "02071400",
            "02076000", "21042000", "21069090", "02109911", "02071210", "02071220",
            "02071300", "02109919", "02071429", "02071419", "16023200", "16023900",
            "02072400", "02072500", "02072600", "02072700", "16023100", "02074100",
            "02074300", "02074400", "02075100", "02075200", "02075300", "02075400",
            "02075500", "02074200", "02074500", "02073500", "02073400", "02073200",
            "02073300", "02073600", "02071411", "02071412", "02071413", "02071421",
            "02071422", "02071423", "02071424", "02071431", "02071432", "02071433",
            "02071434", "02071439", "21061000", "02109900", "21069030",
        ],
    },
    "graos": {
        "destino": os.path.join(_BASE, "Grãos"),
        "ncms": [
            "10019900", "10051000", "10059010", "10059090", "10071000", "10081090",
            "10089090", "11010010", "11010020", "11022000", "11029000", "11031100",
            "11031300", "11032000", "12011000", "12019000", "12081000", "23011010",
            "23011090", "23012010", "23021000", "23023010", "23024000", "23025000",
            "23040010", "23040090", "23063010", "23064100", "23069090", "23091000",
            "23099010", "23099020", "23099030", "23099090",
        ],
    },
    "suino": {
        "destino": os.path.join(_BASE, "Suíno"),
        "ncms": [
            "02031100", "02031200", "02031900", "02032100", "02032200", "02032900",
            "02063000", "02064100", "02064900", "02090011", "02090019", "02090021",
            "02090029", "02091011", "02091019", "02091021", "02091029", "02099000",
            "02101100", "02101200", "02101900", "05021011", "05021019", "05040013",
            "15011000", "15012000", "16024100", "16024200", "16024900", "41033000",
            "41063110", "41063190", "41063200", "41071010", "41071090", "41132000",
        ],
    },
}
