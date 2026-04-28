import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_ANON_KEY", "")

if not url or not key:
    print("AVISO: SUPABASE_URL ou SUPABASE_ANON_KEY não encontradas!")
    supabase = None
else:
    # Conexão leve com o Supabase
    supabase: Client = create_client(url, key)
