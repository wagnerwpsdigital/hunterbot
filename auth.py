from supabase import create_client, Client

# 🔐 Substitua pelos dados reais do seu projeto Supabase
SUPABASE_URL = "https://fdwljwzievxxaanpfgvb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZkd2xqd3ppZXZ4eGFhbnBmZ3ZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDUyODE2NDksImV4cCI6MjA2MDg1NzY0OX0.znkl3rxvaMuqdyMSpNQcni847d3fqXcXzA-t4HNIMo4"
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
