
"Extracción de las colecciones Listings, Reviews y Calendar desde MongoDB."
import os
import pandas as pd
from pymongo import MongoClient
from log_config import configurar_logger

class Extraccion:
    "Conecta a MongoDB y convierte colecciones en DataFrames de pandas."
    def __init__(self, uri=None, nombre_bd=None, log_dir="logs"):
        self.uri = uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        self.nombre_bd = nombre_bd or os.getenv("MONGODB_DB", "AirbnbBogota")
        self.logger = configurar_logger("extraccion", log_dir)
        self.client = None
        self.db = None

    def conectar(self):
        "Abre la conexión y comprueba que el servidor responda."
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command("ping")
            self.db = self.client[self.nombre_bd]
            self.logger.info("Conexión exitosa a MongoDB; base=%s", self.nombre_bd)
            return self.db
        except Exception as exc:
            self.logger.exception("No fue posible conectar a MongoDB: %s", exc)
            raise

    def extraer_coleccion(self, nombre):
        "Lee todos los documentos de una colección y devuelve un DataFrame."
        if self.db is None:
            self.conectar()
        try:
            docs = list(self.db[nombre].find({}, {"_id": 0}))
            df = pd.json_normalize(docs, sep="_") if docs else pd.DataFrame()
            self.logger.info("Colección %s: %s registros extraídos", nombre, len(df))
            return df
        except Exception as exc:
            self.logger.exception("Error extrayendo %s: %s", nombre, exc)
            raise

    def extraer_todo(self):
        "Extrae las colecciones requeridas y devuelve un diccionario de DataFrames."
        if self.db is None:
            self.conectar()
        return {
            "Listings": self.extraer_coleccion("Listings"),
            "Reviews": self.extraer_coleccion("Reviews"),
            "Calendar": self.extraer_coleccion("Calendar"),
        }

    def cerrar(self):
        "Cierra la conexión si está abierta."
        if self.client is not None:
            self.client.close()
            self.logger.info("Conexión MongoDB cerrada")

if __name__ == "__main__":
    etl = Extraccion()
    try:
        datos = etl.extraer_todo()
        for nombre, df in datos.items():
            print(f"{nombre}: {df.shape[0]} filas, {df.shape[1]} columnas")
    finally:
        etl.cerrar()
