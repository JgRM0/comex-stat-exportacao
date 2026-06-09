# Testing Infrastructure

## Test Frameworks

**Unit:** pytest 9.0.3
**E2E:** N/A
**Coverage:** N/A

## Test Organization

```
tests/
└── test_motor.py    # 11 testes: _transformar (7), _build_filtro (1), processar (3)
```

Nenhum script manual em `temp/` — foram removidos na reorganização de 2026-06-09.

## Testing Patterns

### Unit Tests

**Approach:** Testes de função pura e injeção de dependências — sem mocks externos, sem I/O, sem rede
**Location:** `tests/test_motor.py`
**Pattern:** DataFrame sintético ou lambda como entrada → assert sobre saída

#### `_transformar` (7 testes)

- `test_ordem_e_nomes_de_colunas` — contrato com o Power BI (ordem exata das 15 colunas)
- `test_mes_formatado` — mapeamento de número para texto localizado
- `test_ncm_convertido_para_inteiro` — tipo Int64, sem zeros à esquerda
- `test_metricas_convertidas_para_inteiro` — vlFob/kgLiquido como Int64
- `test_nome_coluna_metrica_usa_ano` — nome dinâmico da coluna reflete o ano dos dados
- `test_rename_completo_de_colunas_api` — nenhum nome interno da API vaza para o Excel
- `test_dataframe_vazio_retorna_vazio` — guard de retorno antecipado

#### `_build_filtro` (1 teste)

- `test_build_filtro_estrutura` — payload contém NCMs, período, métricas e detailDatabase

#### `processar` (3 testes)

- `test_processar_levanta_categoria_invalida` — ValueError para categoria desconhecida
- `test_processar_levanta_se_api_retorna_vazio` — ValueError se API retorna 0 registros
- `test_processar_transforma_e_salva` — integração pura: consultar/salvar injetados via lambda

## Test Execution

```
py -m pytest tests/ -v
```

## Test Coverage Matrix

| Camada | Tipo de Teste | Cobertura atual |
|--------|---------------|-----------------|
| `config.py` — parâmetros | Nenhum | Baixo risco — dados estáticos |
| `motor._build_filtro` | pytest (1 teste) | Estrutura e campos obrigatórios |
| `motor._transformar` | pytest (7 testes) | Alta — todos os contratos cobertos |
| `motor.processar` | pytest (3 testes) | Validações + pipeline ponta a ponta via injeção |
| `repositorio.consultar` | Manual (sem script dedicado) | Smoke test via `py app.py` em `MODO_TESTE=True` |
| `repositorio.salvar` | Manual | Verificado ao rodar `app.py` |
| `app.py` — orquestração | Nenhum | 0% |

## Gate Check Commands

| Gate | Quando usar | Comando |
|------|-------------|---------|
| Unit | Após qualquer mudança em `motor.py` | `py -m pytest tests/ -v` |
| Smoke completo | Após mudança em `config.py` ou `repositorio.py` | `py app.py` (MODO_TESTE=True) |
| Produção | Antes de deploy real | Definir `COMEX_DESTINO_PROD`, mudar `MODO_TESTE=False`, rodar `py app.py`, verificar arquivos no destino |
