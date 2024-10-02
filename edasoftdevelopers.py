import os
import pandas as pd
from fastapi import HTTPException
import numpy as np
import matplotlib.pyplot as plt
import pyodbc
import pyodbc
import seaborn as sns

# Datos de conexion
server = "localhost"
database = "softDevelopersDW"
username = "erlin"
password = "Castillo2002"

# Conexion a la base de datos
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

def get_db_connection():
    try:
        cnx = pyodbc.connect(connection_string)
        return cnx
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Realizar la consulta a la base de datos
cnx = get_db_connection()
querie = "SELECT * FROM Fact_Payment AS f FULL JOIN Dim_Customer AS c ON f.[customer key] = c.[customer key] LEFT JOIN Dim_Project AS p ON f.[project key] = p.[project key] LEFT JOIN Dim_Date AS d ON f.[payment date key] = d.[Date Key]"
data = pd.read_sql(querie, cnx)

# Cerrar la conexion a la base de datos para liberar recursos
cnx.close()

# Eliminar columnas no necesarias
df = data.drop(['payment date key','payment key', 'customer key', 'project key', '_SourceCustomerKey', '_SourceProjectKey', 'Lineage Key', '_Source Key', 'Valid From', 'Valid To', 'Date Key', 'Day Suffix', 'Weekday', 'Weekday Name Short',
       'Weekday Name FirstLetter',
       'Week Of Year', 'Month Name Short',
       'Month Name FirstLetter', 'Day Of Year', 'Week Of Month', 'Quarter', 'Quarter Name', 'MMYYYY',
       'Month Year', 'Is Weekend', 'Is Holiday', 'Holiday Name', 'Special Day',
       'First Date Of Year', 'Last Date Of Year', 'First Date Of Quater',
       'Last Date Of Quater', 'First Date Of Month', 'Last Date Of Month', 'First Date Of Week', 'Last Date Of Week'], axis=1)

def basicDesc():
    return df.describe()

# Eliminando los registros duplicados
df = df.drop_duplicates()

# Eliminando los valores nulos
df = df.dropna()

# Eliminar valores nulos representados por 'N/A'
df.replace('N/A', pd.NA, inplace=True)
df.dropna(inplace=True)

# Anadir la columna que representa los porcentajes de margen de los pagos de los proyectos
df['profit margin percentage'] = ((df['project profit margin'] / df['payment amount']) * 100).round(2)


## Funcion que crea un histograma de el monto de los pagos y lo guarda en formato imagen
def histogramPaymentAmount():
    # Visualizacion basica de los datos
    sns.set_style('darkgrid')
    plt.figure(figsize=(10, 6))

    # Crear un histograma con la variable de pago de proyecto
    g = sns.histplot(data = df, x = 'payment amount')

    # Titulos del grafico
    g.set_title('Histogram of Payment amount')
    g.set_xlabel('Total paid per project')

    # Guardar el gráfico en la carpeta 'plots'
    if not os.path.exists('plots'):
        os.makedirs('plots')
    file_path = os.path.join('plots', 'histogram_payment_amount.png')
    plt.savefig(file_path)
    plt.close()  # Cerrar la figura para liberar memoria

    return file_path


## Funcion que crea un boxplot del porcentaje de margen de ganancia y lo guarda en formato imagen
def boxplotMarginPercentage():
    # Le damos estilo al grafico
    sns.set_style('darkgrid')

    # Inicializamos plt para poder almacenar la imagen
    plt.figure(figsize=(10, 6))
    g = sns.boxplot(data=df, x='profit margin percentage')

    g.set_title('Box Plot of Profit Margin Percentage')
    g.set_xlabel('Profit Margin Percentage')

    # Guardar el gráfico en la carpeta 'plots'
    if not os.path.exists('plots'):
        os.makedirs('plots')
    file_path = os.path.join('plots', 'boxplot_margin_percentage.png')
    plt.savefig(file_path)
    plt.close()  # Cerrar la figura para liberar memoria
    return file_path

# Calcular los percentiles
seventy_fifth = df['profit margin percentage'].quantile(0.75)
twenty_fifth = df['profit margin percentage'].quantile(0.25)

# Obtener el rango intercuartilico (IQR)
iqr = seventy_fifth - twenty_fifth

# Establecer los limites inferiores y superiores
upper = seventy_fifth + (1.5 * iqr)
lower = twenty_fifth - (1.5 * iqr)

# Obtener los datos que se encuentran fuera del rango
outliers = df[(df['profit margin percentage'] < lower) | (df['profit margin percentage'] > upper)]


# Winzorizar los Outliers encontrados
from scipy.stats.mstats import winsorize

df_winsorized = df.copy()
df_winsorized['profit margin percentage'] = winsorize(df_winsorized['profit margin percentage'], limits = [0.05, 0.05], inplace = True)


## Funcion que crea un boxplot del porcentaje de margen de ganancia antes y despues 
## de winzorizar y lo guarda en formato imagen
def boxplotsBeforeWinsorization():
    # Create a fig and axis for a 2x1 grid
    fig, axes = plt.subplots(2, 1, figsize = (6, 4))

    #  Create a box plot before and after winsorization
    sns.boxplot(data = df, x = 'profit margin percentage', ax = axes[0])
    sns.boxplot(data = df_winsorized, x = 'profit margin percentage', ax = axes[1])

    # Add labels and titles to each plot
    axes[0].set_title('Box plot before winsorization')
    axes[1].set_title('Box plot after winsorization')

    plt.tight_layout()

    # Guardar el gráfico en la carpeta 'plots'
    if not os.path.exists('plots'):
        os.makedirs('plots')
    file_path = os.path.join('plots', 'boxplots_before_winsorization.png')
    plt.savefig(file_path)
    plt.close()  # Cerrar la figura para liberar memoria
    return file_path


## Funcion que crea un diagrama de dispersion del porcentaje de margen de ganancia 
## y el monto de pago y lo guarda en formato imagen
def scatterPlot():
    sns.set_style('darkgrid')
    plt.figure(figsize=(10, 6))
    sns.relplot(kind="scatter", x='payment amount', y='profit margin percentage', data=df_winsorized)

    # Guardar el gráfico en la carpeta 'plots'
    if not os.path.exists('plots'):
        os.makedirs('plots')
    file_path = os.path.join('plots', 'scatter_plot.png')
    plt.savefig(file_path)
    plt.close()  # Cerrar la figura para liberar memoria
    return file_path


## Funcion que crea un jointplot del porcentaje de margen de ganancia y lo guarda en formato imagen
def jointplot():
    # Programando un Jointplot
    sns.set_style('darkgrid')
    plt.figure(figsize=(10, 6))
    sns.jointplot(x='payment amount', y='profit margin percentage', data=df_winsorized, hue="project state")

    if not os.path.exists('plots'):
        os.makedirs('plots')
    file_path = os.path.join('plots', 'joint_plot.png')
    plt.savefig(file_path)
    plt.close()  # Cerrar la figura para liberar memoria
    return file_path


## Funcion que crea un pairplot y lo guarda en formato imagen
def pairplot():
    # Pairplot para ver si hay relacion entre las variables
    sns.set_style('darkgrid')
    plt.figure(figsize=(10, 6))
    sns.pairplot(data=df_winsorized, hue="project state", corner=True, kind="scatter")

    if not os.path.exists('plots'):
        os.makedirs('plots')
    file_path = os.path.join('plots', 'pair_plot.png')
    plt.savefig(file_path)
    plt.close()  # Cerrar la figura para liberar memoria
    return file_path

# Mapa de color para revisar si existe correlacion entre las variables
from sklearn.preprocessing import StandardScaler

# Normalizacion de variables
scaler = StandardScaler()
scaled = scaler.fit_transform(
    df_winsorized[["payment amount", "project profit margin", "profit margin percentage"]]
)
scaled;

# Encontrar la matriz traspuesta
scaled.T;

# Calcular la covarianza de las variables
cov_matrix = np.cov(scaled.T)


## Funcion que crea un mapa de calor del porcentaje de margen de ganancia, monto del pago
## y el margen de ganancia y lo guarda en formato imagen
def covarianza():
    # Visualizar la matriz de covarianza con un mapa de calor
    plt.figure(figsize=(10, 4))
    sns.set(font_scale=1.5)
    sns.heatmap(
        data=cov_matrix,
        annot=True,
        cbar=True,
        square=True,
        fmt=".5f",
        xticklabels=["payment amount", "project profit margin", "profit margin percentage"],
        yticklabels=["payment amount", "project profit margin", "profit margin percentage"],
        annot_kws={"size": 15}
    )

    if not os.path.exists('plots'):
        os.makedirs('plots')
    file_path = os.path.join('plots', 'covariance_heatmap.png')
    plt.savefig(file_path)
    plt.close()  # Cerrar la figura para liberar memoria
    return file_path
