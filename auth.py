from supabase import create_client, Client

# 🔐 Substitua pelos dados reais do seu projeto Supabase
SUPABASE_URL = "db.fdwljwzievxxaanpfgvb.supabase.co"
SUPABASE_KEY = "Wps060713@@@"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def login(email, senha):
    result = supabase.auth.sign_in_with_password({
        "email": email,
        "password": senha
    })
    return result

def registrar(email, senha):
    result = supabase.auth.sign_up({
        "email": email,
        "password": senha
    })
    return result
