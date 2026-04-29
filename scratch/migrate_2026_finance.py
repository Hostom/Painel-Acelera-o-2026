import pandas as pd
import glob
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")
supabase = create_client(url, key)

pattern = r"C:\Users\Adim\Desktop\squads\OKRS\*Painel*2026*.xlsx"
file_path = glob.glob(pattern)[0]

xl = pd.ExcelFile(file_path)

def migrate_2026_finance():
    print("Iniciando carga financeira de 2026...")
    df_leads = pd.read_excel(xl, sheet_name=5, skiprows=1)
    df_leads.columns = [str(c).strip() for c in df_leads.columns]
    
    df_2026 = df_leads[df_leads["Ano"] == 2026]
    # Pegar todos que tem Valor (sendo alugado ou não, para teste, depois filtro)
    df_with_value = df_2026[df_2026["Valor"].notnull()]
    
    print(f"Total de registros com valor em 2026: {len(df_with_value)}")
    
    for _, row in df_with_value.iterrows():
        try:
            val = float(row.get("Valor", 0))
            if val <= 0: continue
            
            data = {
                "codigo_imovel": str(row.get("Tipo de imóvel", "N/A")),
                "mes": str(row.get("Mês", "Janeiro")),
                "ano": 2026,
                "locatario": str(row.get("Nome", "N/A")),
                "valor_aluguel": val
            }
            res = supabase.table("msi_alugados").insert(data).execute()
            if len(res.data) > 0:
                print(f"SALVO: {data['locatario']} - R$ {val}")
        except Exception as e:
            print(f"Erro ao salvar {row.get('Nome')}: {e}")

if __name__ == "__main__":
    migrate_2026_finance()
