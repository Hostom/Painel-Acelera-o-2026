import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")
supabase = create_client(url, key)

print("--- Raio-X Tabela MSI ---")
try:
    res = supabase.table("msi_alugados").select("*").execute()
    print(f"Total de registros encontrados: {len(res.data)}")
    if len(res.data) > 0:
        print("Primeiro registro encontrado:")
        print(res.data[0])
except Exception as e:
    print(f"Erro: {e}")
