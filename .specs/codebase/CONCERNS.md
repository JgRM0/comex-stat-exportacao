# Codebase Concerns

**Analysis Date:** 2026-06-08  
**Last updated:** 2026-06-09

## Tech Debt

**Atualização anual da fonte do Power BI:**

- Issue: Em 1º de janeiro, `_ANO` muda, o arquivo de saída muda de nome (`H_EXPORTACAO_GERAL_2027.xlsx`) e o Power BI perde a referência até ser atualizado manualmente.
- Files: `modulos/config.py:18`
- ✅ **Mitigado:** `app.py` emite `log.warning` em modo produção no mês 1, lembrando de atualizar a fonte do Power BI.
- Decisão: Não alterar o esquema do Excel (nome de arquivo fixo + coluna Ano) para evitar interferência nos dashboards de destino. Aceitar o aviso anual como processo.

## Resolvido

| Concern | Fix | Data |
|---------|-----|------|
| `chrome120` hardcoded em `motor.py` | Movido para `config.CHROME_IMPERSONATE` | 2026-06-08 |
| DataFrame vazio sobrescrevia arquivo silenciosamente | `processar()` lança `ValueError` se API retornar 0 registros | 2026-06-08 |
| Destino de produção inacessível só falha no `_salvar` | `app.py` verifica `os.path.isdir(_base)` antes do loop (modo produção) | 2026-06-08 |
| `_transformar` sem nenhum teste | `tests/test_motor.py` — 7 testes cobrindo mapeamento, tipos, ordem e meses | 2026-06-08 |
| Contrato implícito com Power BI via ordem de colunas | `test_ordem_e_nomes_de_colunas` verifica as 15 colunas a cada `pytest` | 2026-06-09 |
| `curl_cffi` sem versão pinada — risco de upgrade silencioso | `requirements.txt` com versões fixas de todas as dependências | 2026-06-09 |

---

**Risco residual — `curl_cffi` de nicho:** Se o Cloudflare mudar o fingerprinting TLS, as chamadas falharão com 403. Mitigation atual: `CHROME_IMPERSONATE` em `config.py` permite trocar o perfil sem tocar em `motor.py`. Fallback documentado: `undetected_chromedriver` ou sessão manual com cookies de browser.

---

_Concerns audit: 2026-06-09_
_Update as issues are fixed or new ones discovered_
