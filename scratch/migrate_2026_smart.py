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

def migrate_2026_smart():
    xl = pd.ExcelFile(file_path)
    
    # 1. LEADS E CONTRATOS (FDL 2026)
    print("Migrando FDL 2026 com busca dinâmica...")
    sheet_fdl = "FDL 2026"
    df_fdl = None
    
    # Tentar achar o cabeçalho correto entre as linhas 0 e 15
    for s in range(15):
        temp_df = pd.read_excel(xl, sheet_name=sheet_fdl, skiprows=s)
        cols = [str(c).strip() for c in temp_df.columns]
        if "Nome" in cols or "Lead" in cols:
            print(f"Cabeçalho FDL 2026 encontrado no skiprows={s}")
            df_fdl = temp_df
            df_fdl.columns = cols
            break
            
    if df_fdl is not None:
        # Renomear colunas para padrão
        col_name = "Nome" if "Nome" in df_fdl.columns else "Lead"
        df_fdl = df_fdl.dropna(subset=[col_name])
        
        for _, row in df_fdl.iterrows():
            try:
                b_id = supabase.table("bairros").upsert({"nome": str(row.get("Bairro 01", "Geral")).strip()}, on_conflict="nome").execute().data[0]["id"]
                c_id = supabase.table("corretores").upsert({"nome": str(row.get("Corretor", "Geral")).strip()}, on_conflict="nome").execute().data[0]["id"]
                
                supabase.table("leads").insert({
                    "nome": str(row[col_name]),
                    "telefone": str(row.get("Telefone", "")),
                    "dia": int(row["Dia"]) if "Dia" in df_fdl.columns and pd.notnull(row["Dia"]) else 1,
                    "mes": str(row.get("Mês", "Janeiro")),
                    "ano": 2026,
                    "lead_semana": "S1",
                    "bairro_id": b_id,
                    "corretor_id": c_id,
                    "midia": str(row.get("Mídia", "N/A"))
                }).execute()
                
                if pd.notnull(row.get("Alugado")):
                    supabase.table("msi_alugados").insert({
                        "codigo_imovel": str(row.get("Cód. Imóvel", "N/A")),
                        "mes": str(row.get("Mês", "Janeiro")),
                        "ano": 2026,
                        "locatario": str(row[col_name]),
                        "bairro_id": b_id,
                        "valor_aluguel": float(row.get("Valor", 0)) if pd.notnull(row.get("Valor")) else 0,
                        "corretor_id": c_id
                    }).execute()
                print(f"Sucesso: {row[col_name]}")
            except Exception as e: pass

    # 2. DESOCUPAÇÕES
    print("Migrando Desocupações...")
    sheet_desoc = [s for s in xl.sheet_names if "DESOC" in s.upper()][0]
    df_desoc = pd.read_excel(xl, sheet_name=sheet_desoc, skiprows=1)
    df_desoc.columns = [str(c).strip() for c in df_desoc.columns]
    df_desoc = df_desoc[df_desoc["Ano"] == 2026].dropna(subset=["Locatário"])
    for _, row in df_desoc.iterrows():
        try:
            b_id = supabase.table("bairros").upsert({"nome": str(row["Bairro"]).strip()}, on_conflict="nome").execute().data[0]["id"]
            supabase.table("desocupacoes").insert({
                "codigo_sistema": str(row.get("Código do sistema", "N/A")),
                "mes": str(row["Mês"]), "ano": 2026,
                "locatario": str(row["Locatário"]),
                "valor_aluguel": float(row["Valor do aluguel"]),
                "bairro_id": b_id
            }).execute()
        except: pass

    print("--- MIGRAÇÃO 2026 CONCLUÍDA! ---")

if __name__ == "__main__":
    migrate_2026_smart()
