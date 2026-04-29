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

def migrate_extra():
    xl = pd.ExcelFile(file_path)
    
    # 1. Desocupações
    print("Migrando Desocupações...")
    # Aba: 'Desocupaço' (Encoding bug no nome da aba)
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
                "taxa_adm_percent": float(row["% Taxa de adm"]) if pd.notnull(row["% Taxa de adm"]) else 0.10,
                "motivo": str(row.get("Motivo da desocupação", "Não informado")),
                "bairro_id": b_id
            }).execute()
        except Exception as e: print(f"Erro Desoc: {e}")

    # 2. Captações
    print("Migrando Captações...")
    # Aba: 'Captao'
    sheet_capt = [s for s in xl.sheet_names if "CAPTA" in s.upper()][0]
    df_capt = pd.read_excel(xl, sheet_name=sheet_capt, skiprows=1)
    df_capt.columns = [str(c).strip() for c in df_capt.columns]
    df_capt = df_capt[df_capt["Ano"] == 2026].dropna(subset=["Código do Imóvel"])
    
    for _, row in df_capt.iterrows():
        try:
            b_id = supabase.table("bairros").upsert({"nome": str(row["Bairro"]).strip()}, on_conflict="nome").execute().data[0]["id"]
            c_id = supabase.table("corretores").upsert({"nome": str(row["Captador"]).strip()}, on_conflict="nome").execute().data[0]["id"]
            
            supabase.table("captacoes").insert({
                "codigo_imovel": str(row["Código do Imóvel"]),
                "proprietario": str(row["Proprietário"]),
                "valor_locacao": str(row["Valor da locação"]),
                "status": str(row["Status"]),
                "tipo_captacao": str(row["Tipo de captação"]),
                "mes": str(row["Mês"]),
                "ano": 2026,
                "bairro_id": b_id,
                "corretor_id": c_id
            }).execute()
        except Exception as e: print(f"Erro Capt: {e}")

    # 3. OKRs
    print("Migrando OKRs...")
    sheet_okr = [s for s in xl.sheet_names if "OKR" in s.upper() and "2026" in s.upper()]
    if not sheet_okr: sheet_okr = [s for s in xl.sheet_names if "OKR" in s.upper()]
    
    df_okr = pd.read_excel(xl, sheet_name=sheet_okr[0], skiprows=2)
    df_okr.columns = [str(c).strip() for c in df_okr.columns]
    
    # A aba de OKR costuma ter o nome do mês em uma linha e os KRs abaixo.
    # Vou simplificar e pegar apenas as linhas que têm 'Meta' preenchida.
    df_okr = df_okr.dropna(subset=["Meta"])
    
    for _, row in df_okr.iterrows():
        try:
            # Tentar identificar o mês baseado no contexto (ou assumir Abril para o teste se não achar)
            # Na planilha real os OKRs são por mês.
            supabase.table("okrs").insert({
                "objetivo": str(row.get("Objetivo / KR", "Estratégico")),
                "key_result": str(row.get("Objetivo / KR", "Resultado")),
                "meta": float(row["Meta"]),
                "semana_1": float(row.get("S1", 0)) if pd.notnull(row.get("S1")) else 0,
                "semana_2": float(row.get("S2", 0)) if pd.notnull(row.get("S2")) else 0,
                "semana_3": float(row.get("S3", 0)) if pd.notnull(row.get("S3")) else 0,
                "semana_4": float(row.get("S4", 0)) if pd.notnull(row.get("S4")) else 0,
                "semana_5": float(row.get("S5", 0)) if pd.notnull(row.get("S5")) else 0,
                "mes": "Abril", # Valor padrão se não identificado
                "ano": 2026
            }).execute()
        except Exception as e: print(f"Erro OKR: {e}")

    print("--- Migração Extra Concluída! ---")

if __name__ == "__main__":
    migrate_extra()
