
"""Configuración compartida de logs para el proyecto ETL Airbnb."""
import logging
from datetime import datetime
from pathlib import Path

def configurar_logger(nombre: str, directorio: str = "logs") -> logging.Logger:
    """Crea un logger con archivo único por ejecución y salida en consola."""
    log_dir = Path(directorio)
    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger = logging.getLogger(nombre)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    fh = logging.FileHandler(log_dir / f"log_{stamp}.txt", encoding="utf-8")
    fh.setFormatter(formatter)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(sh)
    logger.propagate = False
    return logger
