import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")
supabase = create_client(url, key)

tables = ["msi_alugados", "leads", "desocupacoes", "metas_mensais", "okrs"]

print("--- Contagem de Registros no Supabase ---")
for t in tables:
    try:
        res = supabase.table(t).select("mes, ano", count="exact").execute()
        count = len(res.data)
        print(f"\nTabela: {t} | Total de linhas com dados: {count}")
        if count > 0:
            # Mostrar os primeiros 5 para ver o formato
            import pandas as pd
            df = pd.DataFrame(res.data)
            print("Amostra de períodos encontrados:")
            print(df.drop_duplicates().head(10))
    except Exception as e:
        print(f"Erro na tabela {t}: {e}")
