import logging

from billings import views

logger = logging.getLogger(__name__)

def run():
    views.SincRC()
    print("Sincronizando")
    logger.info("Sincronizado")
    
