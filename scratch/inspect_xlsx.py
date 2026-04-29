import pandas as pd
import os
import glob

# Procurar o arquivo usando padrão para evitar erro de encoding no nome
pattern = r"C:\Users\Adim\Desktop\squads\OKRS\*Painel*2026*.xlsx"
files = glob.glob(pattern)

if not files:
    print("Nenhum arquivo encontrado com o padrão!")
else:
    file_path = files[0]
    print(f"Abrindo arquivo: {file_path}")
    try:
        xl = pd.ExcelFile(file_path)
        print(f"Abas encontradas: {xl.sheet_names}")
        
        for sheet in xl.sheet_names:
            df = pd.read_excel(xl, sheet_name=sheet, nrows=2)
            print(f"\n--- Aba: {sheet} ---")
            print(df.columns.tolist())
    except Exception as e:
        print(f"Erro ao ler planilha: {e}")
