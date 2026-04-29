import pandas as pd
import glob
from supabase import create_client
import os
from dotenv import load_dotenv

# Carregar envs
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")
supabase = create_client(url, key)

pattern = r"C:\Users\Adim\Desktop\squads\OKRS\*Painel*2026*.xlsx"
file_path = glob.glob(pattern)[0]

def migrate_msi():
    print(f"--- Migrando MSI de {file_path} ---")
    # Pular 2 linhas (comum em planilhas de gestão)
    df = pd.read_excel(file_path, sheet_name="MSI", skiprows=2)
    
    # Limpar nomes de colunas (remover quebras de linha e espaços)
    df.columns = [str(c).replace("\n", " ").strip() for c in df.columns]
    
    # Filtrar apenas 2026 e linhas com dados
    df = df[df["Ano"] == 2026].dropna(subset=["Código do Imóvel"])
    
    print(f"Encontrados {len(df)} contratos em 2026.")
    
    for _, row in df.iterrows():
        try:
            # Resolver Bairro (inserir se não existir)
            bairro_nome = str(row["Bairro"]).strip()
            res_b = supabase.table("bairros").upsert({"nome": bairro_nome}, on_conflict="nome").execute()
            bairro_id = res_b.data[0]["id"]
            
            # Resolver Corretor
            corretor_nome = str(row["Corretor"]).strip()
            res_c = supabase.table("corretores").upsert({"nome": corretor_nome}, on_conflict="nome").execute()
            corretor_id = res_c.data[0]["id"]
            
            # Resolver Tipo Imóvel
            tipo_nome = str(row["Tipo de Imóvel"]).strip()
            res_t = supabase.table("tipos_imovel").upsert({"nome": tipo_nome}, on_conflict="nome").execute()
            tipo_id = res_t.data[0]["id"]
            
            data = {
                "codigo_imovel": str(row["Código do Imóvel"]),
                "dia": int(row["Dia"]) if pd.notnull(row["Dia"]) else 1,
                "mes": str(row["Mês"]),
                "ano": 2026,
                "locador": str(row["Locador"]),
                "locatario": str(row["Locatário"]),
                "bairro_id": bairro_id,
                "tipo_imovel_id": tipo_id,
                "valor_aluguel": float(row["Valor do Aluguel"]),
                "taxa_adm_percent": float(row["% Taxa de Administração"]) if pd.notnull(row["% Taxa de Administração"]) else 0.10,
                "corretor_id": corretor_id
            }
            
            supabase.table("msi_alugados").insert(data).execute()
            print(f"Inserido: {data['codigo_imovel']} - {data['locatario']}")
            
        except Exception as e:
            print(f"Erro ao inserir linha: {e}")

if __name__ == "__main__":
    migrate_msi()
