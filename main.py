from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pyodbc
import pandas as pd
import edasoftdevelopers as  EDA
 

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Datos de conexion
server = "localhost"
database = "softDevelopersDW"
username = "erlin"
password = "Castillo2002"

# Conexion a la base de datos
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

query = ""

## Metodo para conectar a la base de datos
def get_db_connection():
    try:
        cnx = pyodbc.connect(connection_string)
        return cnx
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Endpoint que redirige al inicio(root) de la API
@app.get("/")
def read_root():
    return {"Bienvenido a la API del proyecto SoftDevelopers"}


## Endpoint ue retorna la cantidad de proyectos entregados por anio
@app.get("/projectsperyear")
def read_customers():
    try:
    
    	# Llamar a la base de datos
        cnx = get_db_connection()
        cursor = cnx.cursor()
    	
        # Preparar la consulta a la base de datos
        query = f"SELECT d.Year AS [Anio], Count(p.[project key]) AS [CantidadProjectos] FROM Fact_Payment AS f FULL JOIN Dim_Customer AS c ON f.[customer key] = c.[customer key] LEFT JOIN Dim_Project AS p ON f.[project key] = p.[project key] LEFT JOIN Dim_Date AS d ON f.[payment date key] = d.[Date Key] WHERE d.Year IS NOT NULL AND d.Year <> 0 AND p.[project state] = 'Entregado' Group by d.Year Order by Year ASC"
        
        # Ejecutar la consulta
        cursor.execute(query)
        rows = cursor.fetchall()
        projects = []
        
        # Recorrer los resultados y guardarlos en una lista
        for row in rows:
            project = {
        		"Anio": row[0],
        		"CantidadProyectos": row[1]
        	}
            projects.append(project)
        
        # Cerrar el cursor y la conexion para liberar recursos
        cursor.close()
        cnx.close()
        return {"project": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Endpoint que retorna el margen de ganancia por mes en un rango dado por el usuario
@app.get("/profitmarginthismonth/{month}/{month1}")
def read_profit_margin(month: int, month1: int):
    try:

        # Llamar a la base de datos
        cnx = get_db_connection()
        cursor = cnx.cursor()

        query = f"SELECT d.Month AS [Mes], d.[Month Name] AS [NombreMes], SUM(p.[project profit margin]) AS [MargenGanancia] FROM Fact_Payment AS f FULL JOIN Dim_Customer AS c ON f.[customer key] = c.[customer key] LEFT JOIN Dim_Project AS p ON f.[project key] = p.[project key] LEFT JOIN Dim_Date AS d ON f.[payment date key] = d.[Date Key] WHERE d.Month BETWEEN {month} AND {month1} AND p.[project state] = 'Entregado' GROUP BY d.Month, d.[Month Name] Order by d.Month"
        cursor.execute(query)
        rows = cursor.fetchall()
        margins = []

        # Recorrer los resultados y guardarlos en una lista
        for row in rows:
            margin = {
        		"Mes": row[1],
        		"MargenGanancia": row[2]
        	}
            margins.append(margin)
        
        # Cerrar el cursor y la conexion para liberar recursos
        cursor.close()
        cnx.close()
        return {"margins": margins}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint que llama a una funcion del EDA y retorna la descripcion estadistica en formato de diccionario
@app.get("/edaresults")
def get_eda_results():
    try:
        cnx = get_db_connection()
        query = "SELECT f.[payment amount] AS [pagoProyecto], p.[project profit margin] AS [margenGanancia] FROM Fact_Payment as F LEFT JOIN Dim_Project as P ON F.[project key] = P.[project key]"  # Reemplaza esta consulta con la consulta de tu EDA
        df = pd.read_sql(query, cnx)
        
        # Realiza tu análisis de EDA con Pandas aquí
        summary = EDA.basicDesc().to_dict(orient='split')  # Usando el formato 'split' para facilitar la reconstrucción en el cliente
        
        return JSONResponse(content=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Endpoint que retorna un histograma del EDA
@app.get("/plot/histogram")
def read_histogram():
    try:
        file_path = EDA.histogramPaymentAmount()
        
        return FileResponse(file_path, media_type='image/png', filename='histogram_payment_amount.png')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Endpoint que retorna un boxplot del EDA
@app.get("/plot/boxplot")
def read_boxplot():
    try:
        file_path = EDA.boxplotMarginPercentage()
        return FileResponse(file_path, media_type='image/png', filename='boxplot_margin_percentage.png')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint que retorna un boxplot del EDA luego de aplicar la winzorizacion
@app.get("/plot/boxplots_before_winsorization")
def read_boxplots_before_winsorization():
    try:
        file_path = EDA.boxplotsBeforeWinsorization()
        return FileResponse(file_path, media_type='image/png', filename='boxplots_before_winsorization.png')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Endpoint que retorna un diagrama de dispersion del EDA
@app.get("/plot/scatter_plot")
def read_scatter_plot():
    try:
        file_path = EDA.scatterPlot()
        return FileResponse(file_path, media_type='image/png', filename='scatter_plot.png')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Endpoint que retorna un jointplot del EDA
@app.get("/plot/joint_plot")
def read_joint_plot():
    try:
        file_path = EDA.jointplot()
        return FileResponse(file_path, media_type='image/png', filename='joint_plot.png')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Endpoint que retorna un pairplot del EDA
@app.get("/plot/pair_plot")
def read_pair_plot():
    try:
        file_path = EDA.pairplot()
        return FileResponse(file_path, media_type='image/png', filename='pair_plot.png')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Endpoint que retorna un mapa de calor del EDA que muestra la covarianza entre variables numericas
@app.get("/plot/covariance_heatmap")
def read_covariance_heatmap():
    try:
        file_path = EDA.covarianza()
        return FileResponse(file_path, media_type='image/png', filename='covariance_heatmap.png')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))