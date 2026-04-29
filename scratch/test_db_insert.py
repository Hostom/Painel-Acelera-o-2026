import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")
supabase = create_client(url, key)

print(f"Tentando inserir no banco: {url}")
try:
    data = {"nome": "TESTE CONEXAO", "ano": 2026, "mes": "Janeiro"}
    res = supabase.table("leads").insert(data).execute()
    print("Sucesso na inserção!")
    print(res.data)
except Exception as e:
    print(f"ERRO FATAL NA INSERÇÃO: {e}")
