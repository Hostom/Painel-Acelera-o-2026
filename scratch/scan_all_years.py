import pandas as pd
import glob

pattern = r"C:\Users\Adim\Desktop\squads\OKRS\*Painel*2026*.xlsx"
file_path = glob.glob(pattern)[0]

xl = pd.ExcelFile(file_path)

print("--- Varredura de Anos por Aba ---")
for sheet in xl.sheet_names:
    try:
        df = pd.read_excel(xl, sheet_name=sheet, skiprows=1)
        if "Ano" in df.columns:
            anos = df["Ano"].dropna().unique()
            if len(anos) > 0:
                print(f"Aba: {sheet} | Anos encontrados: {anos}")
    except:
        pass
