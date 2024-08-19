import pandas as pd

def read_excel_table(file_path, sheet_name, start_cells, column_count):
    """
    Lee una tabla desde un archivo Excel.
    
    :param file_path: Ruta del archivo Excel.
    :param sheet_name: Nombre de la hoja donde se encuentra la tabla.
    :param start_cells: Lista con las celdas donde se encuentran los encabezados (ejemplo: ['C2', 'D2', 'E2']).
    :param column_count: Cantidad de columnas a leer.
    :return: Lista de diccionarios con los datos de la tabla.
    """
    
    # Leer el archivo Excel
    df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl', header=None)
    #print(df.head())  # Depuración para ver qué datos se están leyendo
    # Extraer las filas y columnas de las celdas especificadas
    column_headers = []
    column_indices = []

    for cell in start_cells:
        row, col = int(cell[1:]) - 1, ord(cell[0].upper()) - ord('A')
        column_headers.append(df.iloc[row, col])
        column_indices.append(col)

    # Leer la tabla completa desde la fila siguiente a los encabezados
    df_data = df.iloc[int(start_cells[0][1:]):, column_indices[:column_count]]
    df_data.columns = column_headers[:column_count]

    #print(df_data.head())  # Depuración para ver los datos procesados
    # Convertir los datos a una lista de diccionarios
    rows = df_data.dropna().to_dict('records')

    return rows
