import pyodbc

conexao = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=seuserver;'
    'DATABASE=Biblioteca_Renovada;'
    'Trusted_Connection=yes;'
)

cursor = conexao.cursor()

print("Conectado ao banco Biblioteca_Renovada!")
