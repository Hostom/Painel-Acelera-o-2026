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

def migrate_2026():
    xl = pd.ExcelFile(file_path)
    
    # 1. LEADS E CONTRATOS (Da aba FDL 2026)
    print("Migrando Leads e Contratos de FDL 2026...")
    # Pular as primeiras linhas de cabeçalho
    df_fdl = pd.read_excel(xl, sheet_name="FDL 2026", skiprows=6)
    df_fdl.columns = [str(c).strip() for c in df_fdl.columns]
    
    # Filtrar onde tem nome de lead
    df_fdl = df_fdl.dropna(subset=["Nome"])
    
    for _, row in df_fdl.iterrows():
        try:
            # Resolver Bairro
            b_id = supabase.table("bairros").upsert({"nome": str(row.get("Bairro 01", "Geral")).strip()}, on_conflict="nome").execute().data[0]["id"]
            # Resolver Corretor
            c_id = supabase.table("corretores").upsert({"nome": str(row.get("Corretor", "Geral")).strip()}, on_conflict="nome").execute().data[0]["id"]
            
            # Inserir Lead
            supabase.table("leads").insert({
                "nome": str(row["Nome"]),
                "telefone": str(row.get("Telefone", "")),
                "dia": int(row["Dia"]) if pd.notnull(row["Dia"]) else 1,
                "mes": str(row["Mês"]),
                "ano": 2026,
                "lead_semana": "S1" if pd.notnull(row.get("Lead")) else "",
                "interacao_semana": "S1" if pd.notnull(row.get("Interação")) else "",
                "visita_semana": "S1" if pd.notnull(row.get("Visita")) else "",
                "condicao_semana": "S1" if pd.notnull(row.get("Condição de locação")) else "",
                "alugado_semana": "S1" if pd.notnull(row.get("Alugado")) else "",
                "bairro_id": b_id,
                "corretor_id": c_id,
                "midia": str(row.get("Mídia", "N/A")),
                "objecao": str(row.get("Objeção", ""))
            }).execute()
            
            # Se já está ALUGADO, inserir também no MSI_ALUGADOS para os cards financeiros
            if pd.notnull(row.get("Alugado")):
                supabase.table("msi_alugados").insert({
                    "codigo_imovel": str(row.get("Cód. Imóvel", "N/A")),
                    "dia": int(row["Dia"]) if pd.notnull(row["Dia"]) else 1,
                    "mes": str(row["Mês"]),
                    "ano": 2026,
                    "locatario": str(row["Nome"]),
                    "bairro_id": b_id,
                    "valor_aluguel": float(row.get("Valor", 0)) if pd.notnull(row.get("Valor")) else 0,
                    "corretor_id": c_id,
                    "taxa_adm_percent": 0.10
                }).execute()
                
        except Exception as e: print(f"Erro FDL: {e}")

    # 2. DESOCUPAÇÕES (De 2026)
    print("Migrando Desocupações 2026...")
    sheet_desoc = [s for s in xl.sheet_names if "DESOC" in s.upper()][0]
    df_desoc = pd.read_excel(xl, sheet_name=sheet_desoc, skiprows=1)
    df_desoc.columns = [str(c).strip() for c in df_desoc.columns]
    df_desoc = df_desoc[df_desoc["Ano"] == 2026].dropna(subset=["Locatário"])
    
    for _, row in df_desoc.iterrows():
        try:
            b_id = supabase.table("bairros").upsert({"nome": str(row["Bairro"]).strip()}, on_conflict="nome").execute().data[0]["id"]
            supabase.table("desocupacoes").insert({
                "codigo_sistema": str(row.get("Código do sistema", "N/A")),
                "mes": str(row["Mês"]),
                "ano": 2026,
                "locatario": str(row["Locatário"]),
                "valor_aluguel": float(row["Valor do aluguel"]),
                "taxa_adm_percent": 0.10,
                "motivo": str(row.get("Motivo da desocupação", "Mudança")),
                "bairro_id": b_id
            }).execute()
        except Exception as e: print(f"Erro Desoc: {e}")

    # 3. METAS (Valores fixos se não achar, ou da aba Metas)
    print("Sincronizando Metas 2026...")
    df_metas = pd.read_excel(xl, sheet_name="Metas", skiprows=2)
    for _, row in df_metas.iterrows():
        m_nome = str(row.iloc[1]).strip()
        if m_nome in ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]:
            try:
                supabase.table("metas_mensais").upsert({
                    "mes": m_nome, "ano": 2026,
                    "meta_vgl_1": float(row.iloc[2]) if pd.notnull(row.iloc[2]) else 0,
                    "meta_qtd_1": int(row.iloc[5]) if pd.notnull(row.iloc[5]) else 0,
                }, on_conflict="mes,ano").execute()
            except: pass

    print("--- MIGRAÇÃO 2026 FINALIZADA! ---")

if __name__ == "__main__":
    migrate_2026()
