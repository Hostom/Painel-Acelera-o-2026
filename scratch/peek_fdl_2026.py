import pandas as pd
import glob

pattern = r"C:\Users\Adim\Desktop\squads\OKRS\*Painel*2026*.xlsx"
file_path = glob.glob(pattern)[0]

xl = pd.ExcelFile(file_path)
print(f"--- Visualizando estrutura real de FDL 2026 ---")
df = pd.read_excel(xl, sheet_name="FDL 2026", header=None, nrows=20)
print(df)
