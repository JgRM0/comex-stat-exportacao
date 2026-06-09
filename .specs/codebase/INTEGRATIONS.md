# External Integrations

## API Principal

**Service:** COMEX STAT — Ministério do Desenvolvimento, Indústria, Comércio e Serviços (MDIC)
**Purpose:** Dados de exportação brasileira por NCM, país, UF, via, URF com classificações ISIC/CGCE/CUCI
**Implementation:** `modulos/motor.py → _consultar()`
**Base URL:** `https://api-comexstat.mdic.gov.br/general`
**Authentication:** Nenhuma — API pública protegida por Cloudflare

### Detalhe do endpoint

**Method:** GET  
**Query param:** `filter` (JSON URL-encoded)

**Formato do payload:**
```json
{
  "yearStart": "2026", "yearEnd": "2026",
  "monthStart": "01",  "monthEnd": "06",
  "typeForm": 1, "typeOrder": 2,
  "filterArray": [{"item": ["02102000", "..."], "idInput": "noNcmpt"}],
  "filterList": [...],
  "rangeFilter": [],
  "detailDatabase": [
    {"id": "noNcmpt", "parentId": "coNcm", "group": "sh", ...},
    {"id": "noIsicClasspt", "parentId": "coIsicClass", "group": "isic", ...},
    ...
  ],
  "monthDetail": true,
  "metricFOB": true, "metricKG": true,
  "formQueue": "general", "langDefault": "pt"
}
```

**Resposta:**
```json
{
  "data": {
    "list": [
      { "coAno": "2026", "coMes": "05", "coNcm": "02102000",
        "noNcmpt": "Carnes de bovinos...", "coIsicClass": "1010",
        "noIsicClasspt": "Processamento e conservação de carne",
        "coCgceN3": "324", "noCgceN3pt": "...",
        "coCuciItem": "01681", "noCuciItempt": "Carne de bovinos",
        "noPaispt": "Angola", "noUf": "São Paulo",
        "noVia": "MARITIMA", "noUrf": "0817800 - PORTO DE SANTOS",
        "vlFob": "130824", "kgLiquido": "22050" }
    ]
  }
}
```

### Limitações conhecidas

- **Cloudflare rate limiting:** Bloqueios temporários após múltiplas chamadas em janela curta (~5 min). Mitigado por `curl_cffi` com impersonação Chrome120 + sleep de 10s entre categorias em `app.py`.
- **Sem versionamento de API:** URL sem `/v1/` — mudanças de contrato sem aviso prévio.
- **Não há endpoint de health/status** documentado.

## Power BI (destino dos dados)

**Purpose:** Consumo dos arquivos `.xlsx` gerados para dashboards de tendência de mercado
**Connection:** Leitura de arquivo no caminho configurado em `COMEX_DESTINO_PROD`
**Sensitivity:** Qualquer mudança no nome, ordem ou tipo das colunas quebra os relatórios existentes

### Colunas que o Power BI espera (ordem obrigatória)

```
Mês | Código ISIC Classe | Descrição ISIC Classe |
Código CGCE Nível 3 | Descrição CGCE Nível 3 |
Código CUCI Item | Descrição CUCI Item |
Países | UF do Produto | Via | URF |
Código NCM | Descrição NCM |
{ano} - Valor US$ FOB | {ano} - Quilograma Líquido
```
