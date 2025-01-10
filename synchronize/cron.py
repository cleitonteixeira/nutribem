import logging

from billings import views, organize

logger = logging.getLogger(__name__)

def run():
    views.SincRC()
    print("Sincronizando")
    logger.info("Sincronizado Requisicoes")

def refresh_requests():
    organize.refresh_requests()
    logger.info("Atualizando progresso das Requisicoes")
    