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

def migrate_contracts_from_leads():
    print("Extraindo contratos de 2026 da aba de Leads...")
    df_leads = pd.read_excel(xl, sheet_name=5, skiprows=1)
    df_leads.columns = [str(c).strip() for c in df_leads.columns]
    
    # Filtrar apenas 2026 e que foram ALUGADOS
    df_2026 = df_leads[df_leads["Ano"] == 2026]
    # A coluna de 'Alugado' costuma ter um 'X' ou data ou nome
    df_alugados = df_2026[df_2026["Alugado"].notnull()]
    
    print(f"Encontrados {len(df_alugados)} possíveis contratos em 2026 na aba de Leads.")
    
    for _, row in df_alugados.iterrows():
        try:
            b_id = supabase.table("bairros").upsert({"nome": str(row.get("Bairro 01", "Geral")).strip()}, on_conflict="nome").execute().data[0]["id"]
            c_id = supabase.table("corretores").upsert({"nome": str(row.get("Corretor", "Geral")).strip()}, on_conflict="nome").execute().data[0]["id"]
            
            val = float(row.get("Valor", 0)) if pd.notnull(row.get("Valor")) else 0
            if val == 0: continue # Se não tem valor, não é contrato financeiro
            
            data = {
                "codigo_imovel": str(row.get("Tipo de imóvel", "N/A")), # No leads às vezes o código tá aqui ou numa nota
                "dia": int(row["Dia"]) if pd.notnull(row["Dia"]) else 1,
                "mes": str(row["Mês"]),
                "ano": 2026,
                "locatario": str(row.get("Nome", "N/A")),
                "valor_aluguel": val,
                "bairro_id": b_id,
                "corretor_id": c_id,
                "taxa_adm_percent": 0.10
            }
            supabase.table("msi_alugados").insert(data).execute()
            print(f"Contrato migrado: {data['locatario']} - R$ {val}")
        except Exception as e:
            pass

    print("--- MIGRAÇÃO DE CONTRATOS 2026 FINALIZADA ---")

if __name__ == "__main__":
    migrate_contracts_from_leads()
