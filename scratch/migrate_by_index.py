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

def migrate_by_index():
    # Aba 3: Histórico (Geralmente onde ficam os contratos consolidados)
    print("Analisando Aba Index 3 (Histórico)...")
    df_hist = pd.read_excel(xl, sheet_name=3, skiprows=1)
    df_hist.columns = [str(c).strip() for c in df_hist.columns]
    
    if "Ano" in df_hist.columns:
        df_2026 = df_hist[df_hist["Ano"] == 2026]
        print(f"Encontrados {len(df_2026)} registros de 2026 na aba Histórico.")
        for _, row in df_2026.iterrows():
            try:
                b_id = supabase.table("bairros").upsert({"nome": str(row.get("Bairro", "Geral")).strip()}, on_conflict="nome").execute().data[0]["id"]
                supabase.table("msi_alugados").insert({
                    "codigo_imovel": str(row.get("Código do Imóvel", "N/A")),
                    "dia": int(row["Dia"]) if "Dia" in df_hist.columns and pd.notnull(row["Dia"]) else 1,
                    "mes": str(row.get("Mês", "Janeiro")),
                    "ano": 2026,
                    "locatario": str(row.get("Locatário", "N/A")),
                    "valor_aluguel": float(row.get("Valor do aluguel", 0)) if pd.notnull(row.get("Valor do aluguel")) else 0,
                    "bairro_id": b_id
                }).execute()
            except: pass

    # Aba 5: Leads
    print("Analisando Aba Index 5 (Leads)...")
    df_leads = pd.read_excel(xl, sheet_name=5, skiprows=1)
    df_leads.columns = [str(c).strip() for c in df_leads.columns]
    if "Ano" in df_leads.columns:
        df_2026_leads = df_leads[df_leads["Ano"] == 2026]
        print(f"Encontrados {len(df_2026_leads)} leads de 2026.")
        for _, row in df_2026_leads.iterrows():
            try:
                b_id = supabase.table("bairros").upsert({"nome": str(row.get("Bairro 01", "Geral")).strip()}, on_conflict="nome").execute().data[0]["id"]
                supabase.table("leads").insert({
                    "nome": str(row.get("Nome", row.get("Lead", "N/A"))),
                    "mes": str(row.get("Mês", "Janeiro")),
                    "ano": 2026,
                    "bairro_id": b_id,
                    "lead_semana": "S1"
                }).execute()
            except: pass

    print("--- MIGRAÇÃO POR ÍNDICE CONCLUÍDA ---")

if __name__ == "__main__":
    migrate_by_index()
