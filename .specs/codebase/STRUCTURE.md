# Project Structure

**Root:** `automacao-comex/`

## Directory Tree

```
Automacao Exportaçao_Comex/
├── app.py                          # Composition root — logging, loop, injeção de dependências
├── requirements.txt                # Dependências pinadas
├── log_YYYY-MM-DD.txt              # Gerado em runtime (um por dia)
├── modulos/
│   ├── __init__.py                 # Vazio
│   ├── config.py                   # Toda parametrização do projeto
│   ├── motor.py                    # Use case + domain (sem I/O)
│   └── repositorio.py              # Infrastructure adapters (API + Excel)
├── tests/
│   └── test_motor.py               # 11 testes: _transformar, _build_filtro, processar
└── temp/                           # Sandbox — vazio em produção
```

## Module Organization

### modulos/config.py

**Purpose:** Única fonte de verdade para toda parametrização
**Key symbols:**
- `MODO_TESTE` — flag que chaveia entre paths de teste e produção
- `API_URL` — endpoint da API COMEX STAT
- `API_PERIODO` — janela temporal da consulta (jan–mês atual do ano corrente)
- `CHROME_IMPERSONATE` — perfil TLS do curl_cffi (`"chrome120"`)
- `NOME_ARQUIVO` — nome do xlsx gerado (`H_EXPORTACAO_GERAL_{ano}.xlsx`)
- `CATEGORIAS` — dicionário com NCMs e pasta de destino de cada categoria

### modulos/motor.py

**Purpose:** Use case + domain logic — zero I/O, 100% testável sem dependências externas
**Key symbols:**
- `processar(categoria, *, consultar, salvar)` — ponto de entrada público; recebe adaptadores por injeção
- `_build_filtro(ncms, periodo)` — monta payload da API (pura)
- `_transformar(df)` — renomeia, converte tipos, ordena colunas (pura)
- `_DETAIL_DATABASE` — schema de colunas solicitadas à API
- `_COLUNAS_RENAME` — mapeamento API → Excel

### modulos/repositorio.py

**Purpose:** Infrastructure adapters — encapsula todo o I/O do sistema
**Key symbols:**
- `consultar(filtro)` — GET na API com retry 429; retorna pd.DataFrame
- `salvar(df, destino)` — grava .xlsx via openpyxl; retorna caminho
- `_session` — singleton `curl_cffi.Session`

### app.py

**Purpose:** Composition root — conecta motor e repositorio; zero lógica de negócio
**Responsibilities:** Logging, loop por categoria, injeção de dependências, validação de caminho, relatório final

### temp/

**Purpose:** Sandbox para scripts de diagnóstico — vazio em produção

## Where Things Live

**Adicionar nova categoria:**
- NCMs e destino: `modulos/config.py → CATEGORIAS`
- Nenhuma alteração em `motor.py`, `repositorio.py` ou `app.py`

**Mudar período consultado:**
- `modulos/config.py → API_PERIODO`

**Mudar para produção:**
- `modulos/config.py → MODO_TESTE = False`

**Adicionar nova coluna de detalhamento:**
- `modulos/motor.py → _DETAIL_DATABASE` (novo entry)
- `modulos/motor.py → _COLUNAS_RENAME` (mapeamento API → Excel)
- `modulos/motor.py → _transformar()` (coluna no `colunas_saida`)
- `tests/test_motor.py → _COLUNAS_ESPERADAS` (atualizar lista)

**Trocar biblioteca HTTP:**
- Somente `modulos/repositorio.py → consultar()`; nenhuma outra alteração
