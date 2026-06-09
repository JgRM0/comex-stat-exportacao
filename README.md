# Automação COMEX STAT

Extrai dados de exportação brasileira da [API pública COMEX STAT](https://api-comexstat.mdic.gov.br/) (MDIC), transforma os resultados e grava arquivos `.xlsx` prontos para consumo no Power BI.

## O que o projeto faz

Para cada categoria de produto configurada (bovinos, frangos, grãos, suínos), o projeto:

1. Consulta a API COMEX STAT com os NCMs da categoria e o período (janeiro até o mês atual do ano corrente)
2. Transforma os dados: mapeamento de colunas, localização dos meses em português e conversão de tipos
3. Grava um arquivo `.xlsx` com 15 colunas no caminho configurado

A API é pública e não requer autenticação. O bypass do Cloudflare é feito via impersonação de TLS com `curl_cffi`.

## Estrutura de arquivos

```
automacao-comex/
├── app.py                  # Ponto de entrada — logging, loop, injeção de dependências
├── requirements.txt        # Dependências de execução
├── modulos/
│   ├── config.py           # Única fonte de verdade (URLs, NCMs, caminhos, período)
│   ├── motor.py            # Lógica de negócio pura — sem I/O, 100% testável
│   └── repositorio.py      # Adaptadores de infraestrutura (API + Excel)
└── tests/
    └── test_motor.py       # 11 testes unitários (motor.py)
```

## Instalação

Requer Python 3.10+ e pip.

```bash
pip install -r requirements.txt
```

## Configuração

### Modo teste (padrão)

Por padrão, `MODO_TESTE = True` em `modulos/config.py`. Neste modo, os arquivos são salvos em `temp/saida/{Categoria}/` — sem acesso a rede ou caminhos externos.

```bash
py app.py
```

### Modo produção

1. Defina a variável de ambiente com o caminho de destino dos arquivos Excel:

```bash
# Windows
set COMEX_DESTINO_PROD=\\servidor\compartilhamento\pasta-destino

# Linux/macOS
export COMEX_DESTINO_PROD=/mnt/dados/exportacao
```

2. Altere a flag em `modulos/config.py`:

```python
MODO_TESTE = False
```

3. Execute:

```bash
py app.py
```

O script valida o acesso ao destino antes de iniciar qualquer consulta à API.

## Executando os testes

Os testes não requerem rede — testam apenas as funções puras de `motor.py` via injeção de dependências:

```bash
pip install pytest
py -m pytest tests/ -v
```

## Como estender

### Adicionar uma categoria de produto

Edite apenas `modulos/config.py`, seção `CATEGORIAS`:

```python
"nova_categoria": {
    "destino": os.path.join(_BASE, "NomeDaPasta"),
    "ncms": ["01234567", "89012345"],
},
```

Nenhuma outra alteração é necessária em `motor.py`, `repositorio.py` ou `app.py`.

### Adicionar uma fonte de dados alternativa

Implemente um novo adaptador em `modulos/repositorio.py` com a mesma assinatura de `consultar(filtro) -> pd.DataFrame` e injete-o em `app.py` no lugar de `repositorio.consultar`.

### Mudar o período consultado

Altere `API_PERIODO` em `modulos/config.py`:

```python
API_PERIODO = {
    "from": "2025-01",
    "to":   "2025-12",
}
```

### Adicionar uma coluna de detalhamento

1. `modulos/motor.py → _DETAIL_DATABASE`: adicionar o novo campo da API
2. `modulos/motor.py → _COLUNAS_RENAME`: mapear o nome interno da API para o nome Excel
3. `modulos/motor.py → _transformar()`: incluir a coluna em `colunas_saida`
4. `tests/test_motor.py → _COLUNAS_ESPERADAS`: atualizar a lista esperada

## Arquitetura

O projeto segue Clean Architecture com injeção de dependências:

```
app.py  ─── motor.processar(consultar=..., salvar=...)
                ├── _build_filtro()     [pura]
                ├── consultar(filtro)   [adaptador: curl_cffi → API]
                ├── _transformar(df)    [pura]
                └── salvar(df, dest)    [adaptador: openpyxl → .xlsx]
```

`motor.py` não conhece `repositorio.py` — os adaptadores são injetados por `app.py`. Isso permite testar toda a lógica de negócio sem rede e sem disco.

## Dependências

| Pacote | Versão | Uso |
|--------|--------|-----|
| `curl_cffi` | 0.15.0 | Requisições HTTP com impersonação TLS (Chrome120) para bypass do Cloudflare |
| `pandas` | 3.0.2 | Transformação de dados |
| `openpyxl` | 3.1.5 | Escrita de arquivos `.xlsx` |
