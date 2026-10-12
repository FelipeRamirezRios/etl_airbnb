"ADVERTENCIA: A LA HORA DE EJECUTAR EL CODIGO TENGA EN CUENTA QUE NO ESTA DEL TODO OPTIMIZADO, VA A CONSUMIR MUCHA MEMORIA, EN MI CASO TENGO 32 GB (FOTOS EN EL PDF) Y SE ESTABA CONSUMIENDO AL MENOS UN 92% DE LA MEMORIA A LA HORA DE GENERAR EL ARCHIVO EN EXCEL DEL CALENDAR, SE DEMORO UNOS 10 MIN EN COMPLETAR EL EXPORTADO"
## Arquitectura

MongoDB (`AirbnbBogota`: `Listings`, `Reviews`, `Calendar`) → Python/pandas → limpieza y variables derivadas → SQLite + Excel. Los scripts generan logs en `logs/`.


## Requisitos

- MongoDB Community Server iniciado localmente.
- Python 3.14 (o una versión compatible con las librerías Python: 3.13.15).
- MongoDB Compass.
- Jupyter Notebook.
- Archivos fuente `listings.csv.gz`, `reviews.csv.gz` y `calendar.csv.gz` suministrados por el curso.

## 1. Crear base y colecciones

En MongoDB Compass, conectarse a `mongodb://localhost:27017/`, crear la base `AirbnbBogota` e importar los archivos como colecciones `Listings`, `Reviews` y `Calendar`.

Los nombres de las columnas deben coincidir con la primera fila de cada CSV. Verificar en Compass que las tres colecciones tengan documentos.

## 2. Instalar dependencias
(en caso que con py no de, hacer con python)
Desde la carpeta raíz:

```bash
py -m venv .venv
# Windows:
.venv\Scripts\activate
py -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Configurar MongoDB (si es necesario)

Valores por defecto: URI `mongodb://localhost:27017/`, base `AirbnbBogota`. Se pueden configurar variables de entorno:

```powershell
$env:MONGODB_URI="mongodb://localhost:27017/"
$env:MONGODB_DB="AirbnbBogota"
```

## 4. Ejecutar el ETL

Desde la carpeta raíz:

```bash
py src/main.py
```

Los resultados quedan en `data/exports/airbnb_analitica.sqlite` y los archivos `listings.xlsx`, `reviews.xlsx`, `calendar.xlsx`. Los logs se guardan en `logs/`.

## 5. Ejecutar el análisis exploratorio

```bash
jupyter notebook
```

Abrir `notebooks/exploracion_airbnb.ipynb` y ejecutar las celdas en orden. El notebook consulta MongoDB directamente y genera estadísticas y visualizaciones.

## Entregables

- `src/extraccion.py`: clase `Extraccion`.
- `src/transformacion.py`: clase `Transformacion`.
- `src/carga.py`: clase `Carga`.
- `notebooks/exploracion_airbnb.ipynb`: EDA reproducible.
- `requirements.txt`: dependencias.
- `logs/`: logs generados en ejecución.
