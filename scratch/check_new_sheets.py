import pandas as pd
import glob

pattern = r"C:\Users\Adim\Desktop\squads\OKRS\*Painel*2026*.xlsx"
file_path = glob.glob(pattern)[0]

xl = pd.ExcelFile(file_path)

for sheet in ["Histrico", "Analtico", "OKR 2026"]:
    try:
        print(f"\n--- Aba: {sheet} ---")
        df = pd.read_excel(xl, sheet_name=sheet, nrows=5)
        print(df.columns.tolist())
        print(df.head(2))
    except:
        pass
