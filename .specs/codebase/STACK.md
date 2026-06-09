# Tech Stack

**Analyzed:** 2026-06-08

## Core

- Language: Python 3.14 (64-bit)
- Runtime: CPython 3.14
- Package manager: pip

## Data Layer

- HTTP Client: curl-cffi 0.15.0 — impersona TLS do Chrome para bypass do Cloudflare
- Data Manipulation: pandas (versão do ambiente)
- Excel Output: openpyxl (engine do pandas para .xlsx)

## External API

- COMEX STAT: `https://api-comexstat.mdic.gov.br/general` (GET com query param `filter`)
- Resposta: JSON `{ data: { list: [...] } }`
- Proteção: Cloudflare — contornado via `curl_cffi` com `impersonate="chrome120"`

## Output

- Formato: `.xlsx` compatível com Power BI
- Destino produção: configurado via variável de ambiente `COMEX_DESTINO_PROD` (ex: `\\servidor\pasta\{Categoria}\`)
- Destino teste: `temp\saida\{Categoria}\`

## Testing

- Unit: pytest 9.0.3 — `tests/test_motor.py` (7 testes)
- Manual / smoke: `temp/teste_curl_cffi.py`, `temp/validar_saida.py`

## Development Tools

- IDE: VS Code
