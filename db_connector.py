from sqlalchemy import create_engine
import pandas as pd

# Substitua com sua conexão real
SUPABASE_DB_URL = "postgresql://postgres:SUA_SENHA@db.xxx.supabase.co:5432/postgres"

engine = create_engine(SUPABASE_DB_URL)

def salvar_dataframe(df, tabela):
    df.to_sql(tabela, engine, if_exists="append", index=False)

def ler_tabela(tabela):
    return pd.read_sql(f"SELECT * FROM {tabela}", engine)
