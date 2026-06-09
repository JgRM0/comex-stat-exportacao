"""
Ponto de entrada da automação COMEX STAT.

Responsabilidades:
- Configurar o logging (arquivo diário + console)
- Validar o ambiente antes de iniciar (modo produção)
- Iterar pelas categorias e invocar motor.processar com os adaptadores de I/O
- Registrar erros por categoria e emitir relatório final

Zero lógica de negócio — toda a transformação de dados está em motor.py.
"""
import logging
import os
import sys
import time
from datetime import datetime

from modulos import motor, repositorio
from modulos.config import CATEGORIAS, MODO_TESTE, NOME_ARQUIVO

# ── Logging ──────────────────────────────────────────────────────────────────

_pasta = os.path.dirname(os.path.abspath(__file__))
_log_path = os.path.join(_pasta, f"log_{datetime.now().strftime('%Y-%m-%d')}.txt")

# Grava simultaneamente em arquivo diário e no terminal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(_log_path, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger()

# ── Validação de ambiente ─────────────────────────────────────────────────────

log.info("=== Automação COMEX STAT iniciada ===")

if not MODO_TESTE:
    # Verifica se a unidade de rede está acessível antes de processar qualquer categoria.
    # Sem isso, o erro só apareceria no _salvar da última categoria, depois de toda a consulta.
    _base = os.path.commonpath([cfg["destino"] for cfg in CATEGORIAS.values()])
    if not os.path.isdir(_base):
        log.error(f"Destino de produção inacessível: {_base}")
        log.error("Verifique a conexão com a unidade de rede ou ative MODO_TESTE em config.py")
        sys.exit(1)

    # Em janeiro, o nome do arquivo muda de ano — o Power BI precisa ser atualizado manualmente
    if datetime.now().month == 1:
        log.warning(f"Início de ano detectado: atualize a fonte do Power BI para {NOME_ARQUIVO}")

# ── Loop principal ────────────────────────────────────────────────────────────

erros = []
for i, categoria in enumerate(CATEGORIAS):
    if i > 0:
        # Aguarda 10s entre categorias para reduzir a pressão sobre o rate limit do Cloudflare
        time.sleep(10)
    try:
        log.info(f"[{categoria.upper()}] Consultando API...")
        # Composition root: injeta os adaptadores de infraestrutura no use case
        caminho = motor.processar(
            categoria,
            consultar=repositorio.consultar,
            salvar=repositorio.salvar,
        )
        log.info(f"[{categoria.upper()}] Salvo em: {caminho}")
    except Exception as e:
        # Captura genérica intencional: isola falhas por categoria sem interromper as demais
        log.error(f"[{categoria.upper()}] Erro: {e}")
        erros.append(categoria)

# ── Relatório final ───────────────────────────────────────────────────────────

if erros:
    log.error(f"Categorias com falha: {erros}")
else:
    log.info("=== Todas as categorias concluídas com sucesso ===")
