
"""Limpieza y transformación de DataFrames de Airbnb."""
import re
import pandas as pd
from log_config import configurar_logger
import json

class Transformacion:
    """Aplica reglas de calidad a Listings, Reviews y Calendar."""
    def __init__(self, log_dir="logs"):
        self.logger = configurar_logger("transformacion", log_dir)

    @staticmethod
    def _normalizar_precio(valor):
        """Convierte valores tipo '$1,250.00' o '$1.250,00' a número cuando es posible."""
        if pd.isna(valor):
            return None
        if isinstance(valor, (int, float)):
            return float(valor)
        s = re.sub(r"[^0-9,.\-]", "", str(valor).strip())
        if not s:
            return None
        # Si hay punto y coma, se interpreta el último separador como decimal.
        if "," in s and "." in s:
            if s.rfind(",") > s.rfind("."):
                s = s.replace(".", "").replace(",", ".")
            else:
                s = s.replace(",", "")
        elif "," in s:
            # En estos datasets, coma suele ser separador de miles.
            parts = s.split(",")
            s = "".join(parts) if len(parts[-1]) == 3 else ".".join(parts)
        try:
            return float(s)
        except ValueError:
            return None

    def transformar(self, datos):
        """Devuelve DataFrames limpios y registra filas antes/después."""
        resultado = {}
        for nombre, original in datos.items():
            df = original.copy()
            antes = len(df)
            if df.empty:
                self.logger.warning("%s no contiene registros; se conserva vacío", nombre)
                resultado[nombre] = df
                continue

            # Normaliza nombres de columnas y campos anidados.
            df.columns = [str(c).strip() for c in df.columns]
            # Elimina duplicados exactos; no elimina filas solo por compartir un ID.
            
# Elimina duplicados exactos, incluidos los registros con listas o diccionarios.
            def convertir_comparable(valor):
                if isinstance(valor, (list, dict)):
                    return json.dumps(
                        valor,
                        ensure_ascii=False,
                        sort_keys=True,
                        default=str
                    )
                return valor

            df_comparable = df.apply(
                lambda columna: columna.map(convertir_comparable)
                )   

            mascara_duplicados = df_comparable.duplicated()
            duplicados = int(mascara_duplicados.sum())

            if duplicados > 0:
                df = df.loc[~mascara_duplicados].copy()
                self.logger.info(
                    "%s: eliminados %s duplicados exactos",
                    nombre,
                    duplicados
                )


            # Limpia cadenas vacías y espacios; conserva los nulos como valores faltantes.
            for col in df.select_dtypes(include=["object"]).columns:
                df[col] = df[col].map(
                    lambda x: x.strip() if isinstance(x, str) else x
                )
                df[col] = df[col].replace("", None)

            # Normaliza precio donde exista la columna.
            for col in df.columns:
                if col.lower() in {"price", "nightly_price", "precio"}:
                    df[col] = df[col].map(self._normalizar_precio)

            # Campos de fecha típicos de Calendar y Reviews.
            for col in df.columns:
                if col.lower() in {"date", "last_review", "review_date", "scraped_date"}:
                    parsed = pd.to_datetime(df[col], errors="coerce", utc=False)
                    # No convierte toda la columna si ningún valor parece fecha.
                    if parsed.notna().any():
                        df[col] = parsed.dt.strftime("%Y-%m-%d")
                        if col.lower() == "date":
                            fecha = pd.to_datetime(df[col], errors="coerce")
                            df["year"] = fecha.dt.year
                            df["month"] = fecha.dt.month
                            df["day"] = fecha.dt.day
                            df["quarter"] = fecha.dt.quarter

            # Variables derivadas de precios para Listings.
            price_cols = [c for c in df.columns if c.lower() in {"price", "nightly_price", "precio"}]
            if price_cols:
                pcol = price_cols[0]
                df["price_category"] = pd.cut(
                    pd.to_numeric(df[pcol], errors="coerce"),
                    bins=[-float("inf"), 100000, 250000, 500000, float("inf")],
                    labels=["Bajo", "Medio", "Alto", "Muy alto"],
                    include_lowest=True
                ).astype("string")

            # Desanida listas/diccionarios residuales para que SQLite/XLSX los acepte.
            for col in df.columns:
                if df[col].map(lambda x: isinstance(x, (list, dict))).any():
                    df[col] = df[col].map(
                        lambda x: " | ".join(map(str, x)) if isinstance(x, list)
                        else str(x) if isinstance(x, dict) else x
                    )

            # Revisa valores atípicos sin borrarlos automáticamente.
            for col in ["price", "minimum_nights", "availability_365"]:
                if col in df.columns:
                    numeric = pd.to_numeric(df[col], errors="coerce")
                    outliers = int(((numeric < numeric.quantile(.01)) |
                                    (numeric > numeric.quantile(.99))).sum()) if numeric.notna().any() else 0
                    if outliers:
                        self.logger.warning("%s.%s: %s posibles valores extremos (criterio percentiles 1-99); no se eliminan automáticamente",
                                            nombre, col, outliers)

            despues = len(df)
            self.logger.info("%s: filas antes=%s, después=%s; nulos totales=%s",
                             nombre, antes, despues, int(df.isna().sum().sum()))
            resultado[nombre] = df.reset_index(drop=True)
        return resultado
