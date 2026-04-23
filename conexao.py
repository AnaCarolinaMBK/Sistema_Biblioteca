import pyodbc

conexao = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=TBS0676758W11-1\\SQLEXPRESS;'
    'DATABASE=Biblioteca_Renovada;'
    'Trusted_Connection=yes;'
)

cursor = conexao.cursor()

print("Conectado ao banco Biblioteca_Renovada!")