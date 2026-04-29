import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")
supabase = create_client(url, key)

print("--- Teste de Inserção Forçada na MSI ---")
data = {
    "codigo_imovel": "TESTE01",
    "ano": 2026,
    "mes": "Janeiro",
    "locatario": "CLIENTE TESTE",
    "valor_aluguel": 1500.00
}

try:
    res = supabase.table("msi_alugados").insert(data).execute()
    print("Resposta do Supabase:")
    print(res.data)
    if len(res.data) > 0:
        print("CONTRATO SALVO COM SUCESSO NO BANCO!")
    else:
        print("ALERTA: O banco retornou sucesso mas a lista de dados está vazia!")
except Exception as e:
    print(f"ERRO NA INSERÇÃO: {e}")
