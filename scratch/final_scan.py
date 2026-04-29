import pandas as pd
import glob

pattern = r"C:\Users\Adim\Desktop\squads\OKRS\*Painel*2026*.xlsx"
file_path = glob.glob(pattern)[0]

xl = pd.ExcelFile(file_path)
print(f"Lista exata de abas: {xl.sheet_names}")

# Ver as últimas linhas da MSI
print("\n--- Analisando o FINAL da aba MSI (Alugados) ---")
df_msi = pd.read_excel(xl, sheet_name="MSI (Alugados)", skiprows=1)
print(df_msi.tail(10)[["Ano", "Mês", "Código do Imóvel"]])
