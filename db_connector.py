{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 from sqlalchemy import create_engine\
import pandas as pd\
\
# \uc0\u55357 \u56592  Insira sua string de conex\'e3o abaixo\
SUPABASE_DB_URL = "postgresql://postgres:SUA_SENHA_AQUI@db.fdwljwzievxxaanpfgvb.supabase.co:5432/postgres"\
\
# Cria o motor de conex\'e3o\
engine = create_engine(SUPABASE_DB_URL)\
\
# Fun\'e7\'f5es utilit\'e1rias\
def salvar_dataframe(df, tabela):\
    df.to_sql(tabela, engine, if_exists="append", index=False)\
\
def ler_tabela(tabela):\
    return pd.read_sql(f"SELECT * FROM \{tabela\}", engine)}