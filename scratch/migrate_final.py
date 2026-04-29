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

def migrate_all():
    xl = pd.ExcelFile(file_path)
    
    # 1. MSI (Contratos)
    print("Migrando MSI (Alugados)...")
    df_msi = pd.read_excel(xl, sheet_name="MSI (Alugados)", skiprows=1)
    df_msi.columns = [str(c).strip() for c in df_msi.columns]
    df_msi = df_msi[df_msi["Ano"] == 2026].dropna(subset=["Código do Imóvel"])
    
    for _, row in df_msi.iterrows():
        try:
            b_id = supabase.table("bairros").upsert({"nome": str(row["Bairro"]).strip()}, on_conflict="nome").execute().data[0]["id"]
            c_id = supabase.table("corretores").upsert({"nome": str(row["Corretor"]).strip()}, on_conflict="nome").execute().data[0]["id"]
            t_id = supabase.table("tipos_imovel").upsert({"nome": str(row["Tipo de imóvel"]).strip()}, on_conflict="nome").execute().data[0]["id"]
            
            supabase.table("msi_alugados").insert({
                "codigo_imovel": str(row["Código do Imóvel"]),
                "dia": int(row["Dia"]) if pd.notnull(row["Dia"]) else 1,
                "mes": str(row["Mês"]),
                "ano": 2026,
                "locador": str(row["Locador"]),
                "locatario": str(row["Locatário"]),
                "bairro_id": b_id,
                "tipo_imovel_id": t_id,
                "valor_aluguel": float(row["Valor do aluguel"]),
                "taxa_adm_percent": float(row["% Taxa de adm"]) if pd.notnull(row["% Taxa de adm"]) else 0.10,
                "corretor_id": c_id
            }).execute()
        except Exception as e: print(f"Erro MSI: {e}")

    # 2. Leads (Funil)
    print("Migrando Leads...")
    df_leads = pd.read_excel(xl, sheet_name="Leads", skiprows=1)
    df_leads.columns = [str(c).strip() for c in df_leads.columns]
    # Filtrar por ano e garantir que tenha um nome
    df_leads = df_leads[df_leads["Ano"] == 2026].dropna(subset=["Nome"])
    
    for _, row in df_leads.iterrows():
        try:
            b_id = supabase.table("bairros").upsert({"nome": str(row["Bairro 01"]).strip()}, on_conflict="nome").execute().data[0]["id"]
            c_id = supabase.table("corretores").upsert({"nome": str(row["Corretor"]).strip()}, on_conflict="nome").execute().data[0]["id"]
            
            supabase.table("leads").insert({
                "nome": str(row["Nome"]),
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
    print("Migrando Metas...")
    df_metas = pd.read_excel(xl, sheet_name="Metas", skiprows=2)
    # A aba Metas tem nomes de colunas repetidos no Excel, o pandas renomeia para .1, .2
    # MSI Quantidade é o 5º campo (índice 5), MSI VGL é o 2º (índice 2)
    for _, row in df_metas.iterrows():
        m_nome = str(row.iloc[1]).strip() # Coluna 'Meses'
        if m_nome in ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]:
            try:
                supabase.table("metas_mensais").upsert({
                    "mes": m_nome,
                    "ano": 2026,
                    "meta_vgl_1": float(row.iloc[2]) if pd.notnull(row.iloc[2]) else 0,
                    "meta_qtd_1": int(row.iloc[5]) if pd.notnull(row.iloc[5]) else 0,
                    "meta_capt_1": int(row.iloc[8]) if pd.notnull(row.iloc[8]) else 0,
                }, on_conflict="mes,ano").execute()
            except Exception as e: print(f"Erro Metas: {e}")

    print("--- Migração 2026 Concluída com Sucesso! ---")

if __name__ == "__main__":
    migrate_all()
