import pandas as pd
import glob

pattern = r"C:\Users\Adim\Desktop\squads\OKRS\*Painel*2026*.xlsx"
file_path = glob.glob(pattern)[0]

xl = pd.ExcelFile(file_path)
df = pd.read_excel(xl, sheet_name="MSI (Alugados)", skiprows=1)

print("--- Amostra da coluna Ano ---")
print(df["Ano"].unique())
print("\nTipos encontrados na coluna Ano:")
print(df["Ano"].apply(type).unique())
