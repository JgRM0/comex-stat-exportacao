# Code Conventions

## Naming Conventions

**Files:**
- `snake_case.py` para todos os módulos
- Exemplos: `motor.py`, `config.py`, `validar_saida.py`

**Funções públicas:**
- `snake_case` sem prefixo
- Exemplos: `processar`, `_consultar`, `_transformar`, `_salvar`

**Funções privadas de módulo:**
- Prefixo `_` para indicar uso interno
- Exemplos: `_consultar`, `_build_filtro`, `_transformar`, `_salvar`

**Constantes de módulo:**
- `UPPER_SNAKE_CASE` para constantes exportadas (visíveis fora)
- `_UPPER_SNAKE_CASE` para constantes privadas de módulo
- Exemplos: `CATEGORIAS`, `API_URL`, `MODO_TESTE` / `_DETAIL_DATABASE`, `_COLUNAS_RENAME`, `_MESES_PT`

**Variáveis locais:**
- `snake_case`; nomes descritivos mesmo em escopos curtos
- Exemplos: `filtro_str`, `col_fob`, `col_kg`, `ano_inicio`, `mes_fim`

## Import Ordering

```python
# 1. stdlib
import json
import os
import time

# 2. terceiros
import pandas as pd
from curl_cffi import requests as cr

# 3. internos
from modulos.config import API_URL, API_PERIODO, CATEGORIAS, NOME_ARQUIVO
```

## File Structure (motor.py como referência)

```
1. Imports
2. Constantes privadas de módulo (_MESES_PT, _DETAIL_DATABASE, _COLUNAS_RENAME)
3. Singleton de sessão (_session)
4. Função pública (processar)
5. Funções privadas na ordem do fluxo (_build_filtro → _consultar → _transformar → _salvar)
```

## Type Annotations

Usadas em assinaturas de funções públicas e privadas:
```python
def processar(categoria: str) -> str:
def _consultar(ncms: list) -> pd.DataFrame:
def _transformar(df: pd.DataFrame) -> pd.DataFrame:
def _salvar(df: pd.DataFrame, destino: str) -> str:
```
Sem anotações em variáveis locais simples.

## Error Handling

- `ValueError` para entradas inválidas de contrato (`categoria` desconhecida)
- `RuntimeError` para falhas de infraestrutura (rate limit esgotado)
- `raise_for_status()` para erros HTTP não-429
- `app.py` captura `Exception` genericamente no loop para isolar falhas por categoria

## Logging

Padrão do `CLAUDE.md` — exclusivamente em `app.py`:
```python
log.info(f"[{categoria.upper()}] Consultando API...")
log.error(f"[{categoria.upper()}] Erro: {e}")
```
- Arquivo diário: `log_YYYY-MM-DD.txt` na raiz
- `motor.py` não loga — erros propagam como exceções

## Comments

Nenhum comentário desnecessário. O único comentário presente documenta a razão não-óbvia do `MODO_TESTE`:
```python
# Mude para False quando quiser salvar nos caminhos reais de produção
MODO_TESTE = True
```
