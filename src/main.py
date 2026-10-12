
"""Orquestador del proceso ETL Airbnb."""
from extraccion import Extraccion
from transformacion import Transformacion
from carga import Carga

def main():
    extractor = Extraccion()
    try:
        datos = extractor.extraer_todo()
        limpios = Transformacion().transformar(datos)
        destino = Carga().cargar(limpios)
        print(f"Proceso ETL terminado. Base SQLite: {destino}")
        for nombre, df in limpios.items():
            print(f"{nombre}: {len(df)} filas, {len(df.columns)} columnas")
    finally:
        extractor.cerrar()

if __name__ == "__main__":
    main()
