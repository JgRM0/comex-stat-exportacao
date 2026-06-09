# Architecture

**Pattern:** Clean Architecture — separação entre use case (motor), infraestrutura (repositorio) e orquestração (app)

## High-Level Structure

```
app.py  ──────────────────────────────────────────────────
  composition root: injeta repositorio em motor            
  ↓                    ↓                                   
motor.processar(   repositorio.consultar / .salvar         
  consultar=...,     ↓                   ↓                 
  salvar=...,      curl_cffi (API)    openpyxl (Excel)     
)                                                          
  ↓                                                        
motor._build_filtro  →  motor._transformar                 
(pure)                   (pure)                            
```

## Camadas

### Use Case / Domain — `modulos/motor.py`

Zero dependências de I/O. Importa apenas `pandas` e `config`.

- `processar(categoria, *, consultar, salvar)` — orquestrador do caso de uso; recebe os adaptadores por injeção
- `_build_filtro(ncms, periodo)` — monta o payload da API (pura)
- `_transformar(df)` — renomeia, converte tipos, ordena colunas (pura)
- `_DETAIL_DATABASE`, `_COLUNAS_RENAME`, `_MESES_PT` — constantes de domínio

### Infrastructure / Adapters — `modulos/repositorio.py`

Todo o I/O do sistema. Importa `curl_cffi`, `openpyxl`, `pandas` e `config`.

- `consultar(filtro)` — GET na API COMEX STAT com retry 429
- `salvar(df, destino)` — escreve `.xlsx` via openpyxl
- `_session` — singleton `curl_cffi.Session`

### Composition Root — `app.py`

Conecta as camadas. Injeta `repositorio.consultar` e `repositorio.salvar` em `motor.processar`.
Zero lógica de negócio. Responsável por logging, validação de caminho de produção e loop de categorias.

### Configuration — `modulos/config.py`

Folha sem dependências internas. Única fonte de verdade para URLs, NCMs, caminhos e período.

## Dependency Rule

```
app.py  →  motor.py   (use case)
app.py  →  repositorio.py  (infrastructure)
motor.py  ←→  config.py    (configuration — não é infraestrutura)
repositorio.py  →  config.py
motor.py  ✗  repositorio.py   (use case NÃO conhece infraestrutura)
```

## Data Flow

```
app.py
  ├── valida destino de produção (modo produção)
  └── para cada categoria:
        motor.processar(categoria, consultar=..., salvar=...)
          ├── _build_filtro(ncms, API_PERIODO)  → dict payload
          ├── consultar(filtro)                 → GET /general → pd.DataFrame
          ├── valida df não vazio
          ├── _transformar(df)                  → rename + tipos + ordem
          └── salvar(df, destino)               → .xlsx
```

## Mapeamento de colunas (API → Excel)

| API (`coNcm`, `noPaispt` …)     | Excel (`Código NCM`, `Países` …) |
|---------------------------------|----------------------------------|
| `coAno` / `coMes`               | `Mês` (formato "01. Janeiro")    |
| `coNcm`                         | `Código NCM` (Int64)             |
| `noNcmpt`                       | `Descrição NCM`                  |
| `coIsicClass` / `noIsicClasspt` | `Código/Descrição ISIC Classe`   |
| `coCgceN3` / `noCgceN3pt`       | `Código/Descrição CGCE Nível 3`  |
| `coCuciItem` / `noCuciItempt`   | `Código/Descrição CUCI Item`     |
| `noPaispt`                      | `Países`                         |
| `noUf` / `noVia` / `noUrf`      | `UF do Produto` / `Via` / `URF`  |
| `vlFob` / `kgLiquido`           | `{ano} - Valor US$ FOB / KG`     |

## Code Organization

**Approach:** Layer-based (config / use-case / infrastructure / composition-root)

```
modulos/config.py       — parametrização (folha, sem dependências internas)
modulos/motor.py        — use case + domain (sem I/O, 100% testável em isolamento)
modulos/repositorio.py  — infrastructure adapters (API + Excel)
app.py                  — composition root (injeta dependências, logging, loop)
temp/                   — sandbox (vazio em produção)
```

**Module boundaries:**
- `motor.py` não importa `repositorio` — dependências são injetadas pelo caller
- `repositorio.py` não importa `motor` — adaptadores são agnósticos ao domínio
- `app.py` importa ambos e faz a composição
- `config.py` é folha — sem dependências internas
