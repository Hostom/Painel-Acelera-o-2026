import pandas as pd
import glob

pattern = r"C:\Users\Adim\Desktop\squads\OKRS\*Painel*2026*.xlsx"
file_path = glob.glob(pattern)[0]

xl = pd.ExcelFile(file_path)

for sheet in xl.sheet_names:
    if "MSI" in sheet.upper() or "LEAD" in sheet.upper() or "META" in sheet.upper():
        print(f"\n--- Aba: {sheet} ---")
        # Tentar ler com diferentes pulares de linha para achar o cabeçalho
        for s in range(5):
            df = pd.read_excel(xl, sheet_name=sheet, nrows=1, skiprows=s)
            cols = [str(c).strip() for c in df.columns]
            if "Ano" in cols or "Mês" in cols or "Meses" in cols:
                print(f"Cabeçalho encontrado no skiprows={s}")
                print(cols)
                break
