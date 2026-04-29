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

def get_sheet_name(xl, partial_name):
    """Encontra o nome real da aba mesmo com espaços ou encoding errado."""
    for name in xl.sheet_names:
        if partial_name.upper() in name.upper().strip():
            return name
    return None

def migrate_all():
    xl = pd.ExcelFile(file_path)
    
    # 1. MSI (Contratos)
    sheet_msi = get_sheet_name(xl, "MSI")
    if sheet_msi:
        print(f"Migrando MSI (Aba: {sheet_msi})...")
        df = pd.read_excel(xl, sheet_name=sheet_msi, skiprows=2)
        df.columns = [str(c).replace("\n", " ").strip() for c in df.columns]
        df = df[df["Ano"] == 2026].dropna(subset=["Código do Imóvel"])
        
        for _, row in df.iterrows():
            try:
                b_id = supabase.table("bairros").upsert({"nome": str(row["Bairro"]).strip()}, on_conflict="nome").execute().data[0]["id"]
                c_id = supabase.table("corretores").upsert({"nome": str(row["Corretor"]).strip()}, on_conflict="nome").execute().data[0]["id"]
                t_id = supabase.table("tipos_imovel").upsert({"nome": str(row["Tipo de Imóvel"]).strip()}, on_conflict="nome").execute().data[0]["id"]
                
                supabase.table("msi_alugados").insert({
                    "codigo_imovel": str(row["Código do Imóvel"]),
                    "dia": int(row["Dia"]) if pd.notnull(row["Dia"]) else 1,
                    "mes": str(row["Mês"]),
                    "ano": 2026,
                    "locador": str(row["Locador"]),
                    "locatario": str(row["Locatário"]),
                    "bairro_id": b_id,
                    "tipo_imovel_id": t_id,
                    "valor_aluguel": float(row["Valor do Aluguel"]),
                    "taxa_adm_percent": float(row["% Taxa de Administração"]) if pd.notnull(row["% Taxa de Administração"]) else 0.10,
                    "corretor_id": c_id
                }).execute()
            except Exception as e: print(f"Erro MSI: {e}")

    # 2. Leads (Funil)
    sheet_leads = get_sheet_name(xl, "LEADS")
    if sheet_leads:
        print(f"Migrando Leads (Aba: {sheet_leads})...")
        df = pd.read_excel(xl, sheet_name=sheet_leads, skiprows=1)
        df.columns = [str(c).replace("\n", " ").strip() for c in df.columns]
        df = df[df["Ano"] == 2026].dropna(subset=["Lead"])
        
        for _, row in df.iterrows():
            try:
                b_id = supabase.table("bairros").upsert({"nome": str(row["Bairro 01"]).strip()}, on_conflict="nome").execute().data[0]["id"]
                c_id = supabase.table("corretores").upsert({"nome": str(row["Corretor"]).strip()}, on_conflict="nome").execute().data[0]["id"]
                
                supabase.table("leads").insert({
                    "nome": str(row["Lead"]),
                    "telefone": str(row.get("Telefone", "")),
                    "dia": int(row["Dia"]) if pd.notnull(row["Dia"]) else 1,
                    "mes": str(row["Mês"]),
                    "ano": 2026,
                    "lead_semana": str(row.get("Lead", "")),
                    "interacao_semana": str(row.get("Interação", "")),
                    "visita_semana": str(row.get("Visita", "")),
                    "condicao_semana": str(row.get("Condição de locação", "")),
                    "alugado_semana": str(row.get("Alugado", "")),
                    "bairro_id": b_id,
                    "corretor_id": c_id,
                    "midia": str(row.get("Mídia", "N/A")),
                    "objecao": str(row.get("Objeção", ""))
                }).execute()
            except Exception as e: print(f"Erro Leads: {e}")

    # 3. Metas
    sheet_metas = get_sheet_name(xl, "METAS")
    if sheet_metas:
        print(f"Migrando Metas (Aba: {sheet_metas})...")
        df = pd.read_excel(xl, sheet_name=sheet_metas, skiprows=3)
        df.columns = [str(c).replace("\n", " ").strip() for c in df.columns]
        
        for _, row in df.iterrows():
            if pd.isnull(row["Meses"]): continue
            try:
                supabase.table("metas_mensais").upsert({
                    "mes": str(row["Meses"]),
                    "ano": 2026,
                    "meta_vgl_1": float(row["Meta 1 VGL"]) if pd.notnull(row["Meta 1 VGL"]) else 0,
                    "meta_qtd_1": int(row["Meta 1 Quantidade"]) if pd.notnull(row["Meta 1 Quantidade"]) else 0,
                    "meta_capt_1": int(row["Meta 1 Captação"]) if pd.notnull(row["Meta 1 Captação"]) else 0,
                }, on_conflict="mes,ano").execute()
            except Exception as e: print(f"Erro Metas: {e}")

    print("--- Migração Concluída ---")

if __name__ == "__main__":
    migrate_all()
