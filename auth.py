{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 from supabase import create_client, Client\
import streamlit as st\
\
# Chaves do seu projeto Supabase\
SUPABASE_URL = "https://SEU_PROJETO.supabase.co"\
SUPABASE_KEY = "SUA_CHAVE_PUBLICA"\
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)\
\
# Fun\'e7\'e3o de login\
def login(email, senha):\
    result = supabase.auth.sign_in_with_password(\{\
        "email": email,\
        "password": senha\
    \})\
    return result\
\
# Fun\'e7\'e3o de registro\
def registrar(email, senha):\
    result = supabase.auth.sign_up(\{\
        "email": email,\
        "password": senha\
    \})\
    return result}