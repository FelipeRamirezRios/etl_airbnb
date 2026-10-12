
"""Carga los DataFrames transformados en SQLite y archivos XLSX."""

import sqlite3
from pathlib import Path

import pandas as pd
from log_config import configurar_logger


class Carga:
    """Carga resultados transformados a SQLite y exporta archivos Excel."""

    # Excel admite 1.048.576 filas por hoja, incluida la cabecera.
    # Se usa un millón para mantener un margen de seguridad.
    MAX_FILAS_EXCEL = 1_000_000

    def __init__(
        self,
        sqlite_path="data/exports/airbnb_analitica.sqlite",
        excel_dir="data/exports",
        log_dir="logs"
    ):
        self.sqlite_path = Path(sqlite_path)
        self.excel_dir = Path(excel_dir)

        self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        self.excel_dir.mkdir(parents=True, exist_ok=True)

        self.logger = configurar_logger("carga", log_dir)

    @staticmethod
    def _nombre_tabla(nombre):
        return nombre.lower().replace(" ", "_")

    def _exportar_excel(self, df, archivo, nombre):
        """Exporta un DataFrame a Excel, dividiéndolo en hojas si es necesario."""

        total = len(df)

        if total == 0:
            df.to_excel(archivo, index=False, engine="openpyxl")
            self.logger.info(
                "Excel exportado: %s (0 filas)", archivo
            )
            return

        with pd.ExcelWriter(archivo, engine="openpyxl") as writer:
            for inicio in range(0, total, self.MAX_FILAS_EXCEL):
                fin = min(inicio + self.MAX_FILAS_EXCEL, total)
                numero_hoja = inicio // self.MAX_FILAS_EXCEL + 1

                nombre_hoja = (
                    "Datos" if total <= self.MAX_FILAS_EXCEL
                    else f"Datos_{numero_hoja}"
                )

                df.iloc[inicio:fin].to_excel(
                    writer,
                    sheet_name=nombre_hoja,
                    index=False
                )

                self.logger.info(
                    "%s: exportada hoja %s; filas=%s",
                    nombre,
                    nombre_hoja,
                    fin - inicio
                )

        self.logger.info(
            "Excel exportado: %s (%s filas en total)", archivo, total
        )

    def cargar(self, datos):
        """Guarda cada DataFrame en SQLite, verifica conteos y exporta Excel."""

        with sqlite3.connect(self.sqlite_path) as conn:
            for nombre, df in datos.items():
                tabla = self._nombre_tabla(nombre)

                # Carga en SQLite.
                df.to_sql(
                    tabla,
                    conn,
                    if_exists="replace",
                    index=False
                )

                # Verifica la cantidad de registros cargados.
                consulta = f'SELECT COUNT(*) AS n FROM "{tabla}"'
                verificado = pd.read_sql_query(
                    consulta, conn
                )["n"].iloc[0]

                if int(verificado) != len(df):
                    self.logger.error(
                        "Verificación fallida en %s: esperado=%s, cargado=%s",
                        tabla,
                        len(df),
                        verificado
                    )
                    raise RuntimeError(
                        f"Conteo incorrecto para {tabla}"
                    )

                self.logger.info(
                    "SQLite: tabla=%s; filas verificadas=%s",
                    tabla,
                    verificado
                )

                # Exporta a Excel, creando varias hojas cuando sea necesario.
                archivo = self.excel_dir / f"{tabla}.xlsx"
                self._exportar_excel(df, archivo, nombre)

        return str(self.sqlite_path)
