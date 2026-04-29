import pandas as pd
import glob

pattern = r"C:\Users\Adim\Desktop\squads\OKRS\*Painel*2026*.xlsx"
file_path = glob.glob(pattern)[0]

xl = pd.ExcelFile(file_path)

for sheet in ["HISTRICO DE LOCAO ", "FDL 2026"]:
    try:
        print(f"\n--- Analisando Aba: {sheet} ---")
        df = pd.read_excel(xl, sheet_name=sheet, nrows=10)
        print(df.columns.tolist())
        print(df.head(5))
    except:
        print(f"Aba {sheet} não encontrada ou erro na leitura.")
