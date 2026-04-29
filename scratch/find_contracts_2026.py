import pandas as pd
import glob

pattern = r"C:\Users\Adim\Desktop\squads\OKRS\*Painel*2026*.xlsx"
file_path = glob.glob(pattern)[0]

xl = pd.ExcelFile(file_path)

for idx in [1, 3]: # Analítico e Histórico
    print(f"\n--- Analisando Aba Index {idx} ---")
    df = pd.read_excel(xl, sheet_name=idx, nrows=10, skiprows=1)
    print(f"Colunas: {df.columns.tolist()}")
    # Tentar ver se tem 2026 em algum lugar dessas abas
    df_full = pd.read_excel(xl, sheet_name=idx, skiprows=1)
    if "Ano" in df_full.columns:
        print(f"Anos encontrados na aba {idx}: {df_full['Ano'].dropna().unique()}")
    else:
        # Se não tem coluna Ano, ver se tem data
        date_cols = [c for c in df_full.columns if "DATA" in str(c).upper() or "DIA" in str(c).upper()]
        print(f"Colunas de data encontradas: {date_cols}")
