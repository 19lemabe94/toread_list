import streamlit as st
import pandas as pd
import os
from datetime import date

st.set_page_config(page_title="To Read List", page_icon="⛾", layout="wide")
st.title("⛾ To Read List")

def carregar(ficheiro, colunas):
    return pd.read_csv(ficheiro) if os.path.exists(ficheiro) else pd.DataFrame(columns=colunas)

# Carrega as 3 bases de dados
df_diario = carregar("diario.csv", ["Data", "Livro", "Páginas"])
df_wishlist = carregar("wishlist.csv", ["Livro", "Status"])
df_livros = carregar("livros.csv", ["Livro", "Status"])

if "Status" not in df_wishlist.columns:
    df_wishlist["Status"] = "Pendente"

# Segurança: Se a base de livros estiver vazia (primeira vez rodando essa versão), 
# ele cria a lista automaticamente puxando do histórico do diário
if df_livros.empty and not df_diario.empty:
    livros_unicos = df_diario["Livro"].unique()
    df_livros = pd.DataFrame({"Livro": livros_unicos, "Status": ["Em Progresso"] * len(livros_unicos)})
    df_livros.to_csv("livros.csv", index=False)

# Criação das 3 abas
aba_diario, aba_livros, aba_wishlist = st.tabs([
    ":material/menu_book: Diário", 
    ":material/auto_stories: Meus Livros", 
    ":material/shopping_cart_checkout: Wishlist"
])

# --- ABA 1: DIÁRIO ---
with aba_diario:
    col_data, col_contador = st.columns([1, 3], vertical_alignment="center")
    with col_data:
        data_selecionada = st.date_input("Navegar para a data:", value=date.today())
        data_str = data_selecionada.strftime("%d/%m/%Y")
    
    df_do_dia = df_diario[df_diario["Data"] == data_str]
    total_paginas = df_do_dia["Páginas"].sum() if not df_do_dia.empty else 0
    
    with col_contador:
        st.markdown(f"### :material/today: {total_paginas} páginas")

    with st.form("form_leitura", clear_on_submit=True, border=False):
        # Layout ajustado para ter caixa de seleção E caixa de texto novo
        col1, col2, col3, col4 = st.columns([3, 3, 2, 2], vertical_alignment="bottom")
        
        # Filtra apenas os livros que ainda não foram marcados como lidos
        livros_ativos = df_livros[df_livros["Status"] == "Em Progresso"]["Livro"].tolist()
        opcoes = [""] + livros_ativos if livros_ativos else [""]
        
        with col1:
            livro_selecionado = st.selectbox("Livros em Progresso", opcoes)
        with col2:
            livro_novo = st.text_input("Ou registre um novo livro")
        with col3:
            paginas = st.number_input("Páginas lidas", min_value=1, step=1)
        with col4:
            salvar = st.form_submit_button("Salvar")
        
        if salvar:
            # Prioriza o livro novo. Se estiver vazio, usa o selecionado na lista
            livro_final = livro_novo if livro_novo.strip() else livro_selecionado
            
            if livro_final:
                # Se for um livro inédito, adiciona à aba Meus Livros automaticamente
                if livro_final not in df_livros["Livro"].values:
                    novo_l = pd.DataFrame([{"Livro": livro_final, "Status": "Em Progresso"}])
                    df_livros = pd.concat([df_livros, novo_l], ignore_index=True)
                    df_livros.to_csv("livros.csv", index=False)
                
                # Salva o registro no diário
                novo_d = pd.DataFrame([{"Data": data_str, "Livro": livro_final, "Páginas": paginas}])
                df_diario = pd.concat([df_diario, novo_d], ignore_index=True)
                df_diario.to_csv("diario.csv", index=False)
                st.rerun()

    if not df_do_dia.empty:
        st.write("---") 
        hc2, hc3, hc4 = st.columns([5, 2, 2], vertical_alignment="bottom")
        hc2.write("**Livro**")
        hc3.write("**Páginas**")
        hc4.write("**Excluir**")
        
        for i, row in df_do_dia.iterrows():
            c2, c3, c4 = st.columns([5, 2, 2], vertical_alignment="center")
            c2.write(row["Livro"])
            c3.write(row["Páginas"])
            if c4.button(":material/delete:", key=f"del_diario_{i}"):
                df_diario = df_diario.drop(i)
                df_diario.to_csv("diario.csv", index=False)
                st.rerun()

# --- ABA 2: MEUS LIVROS (PROGRESSO) ---
with aba_livros:
    # Contadores globais
    total_paginas_geral = df_diario["Páginas"].sum() if not df_diario.empty else 0
    total_livros_lidos = len(df_livros[df_livros["Status"] == "Lido"]) if not df_livros.empty else 0
    
    m1, m2 = st.columns(2)
    m1.metric(":material/check_circle: Livros Lidos", total_livros_lidos)
    m2.metric(":material/menu_book: Páginas Totais Lidas", total_paginas_geral)
    
    if not df_livros.empty:
        st.write("---") 
        hl1, hl2, hl3, hl4 = st.columns([5, 2, 1, 1], vertical_alignment="bottom")
        hl1.write("**Livro**")
        hl2.write("**Progresso**")
        hl3.write("**Lido**")
        hl4.write("**Excluir**")
        
        for i, row in df_livros.iterrows():
            l1, l2, l3, l4 = st.columns([5, 2, 1, 1], vertical_alignment="center")
            
            # Soma todas as páginas registradas para este livro específico no Diário
            pags_livro = df_diario[df_diario["Livro"] == row["Livro"]]["Páginas"].sum()
            
            if row["Status"] == "Lido":
                l1.write(f"~~{row['Livro']}~~")
            else:
                l1.write(row["Livro"])
                
            l2.write(f"{pags_livro} págs")
            
            # Botão de marcar como lido
            icone_lido = ":material/check_box:" if row["Status"] == "Lido" else ":material/check_box_outline_blank:"
            if l3.button(icone_lido, key=f"check_livro_{i}"):
                df_livros.at[i, "Status"] = "Em Progresso" if row["Status"] == "Lido" else "Lido"
                df_livros.to_csv("livros.csv", index=False)
                st.rerun()
            
            if l4.button(":material/delete:", key=f"del_livro_{i}"):
                df_livros = df_livros.drop(i)
                df_livros.to_csv("livros.csv", index=False)
                st.rerun()
    else:
        st.info("Nenhum livro registrado ainda. Ao salvar uma leitura no Diário, o livro aparecerá aqui!")

# --- ABA 3: WISHLIST ---
with aba_wishlist:
    with st.form("form_wishlist", clear_on_submit=True, border=False):
        colA, colB = st.columns([8, 2], vertical_alignment="bottom")
        with colA:
            novo_desejo = st.text_input("Novo livro")
        with colB:
            adicionar = st.form_submit_button(":material/add: Adicionar")
        
        if adicionar and novo_desejo:
            novo = pd.DataFrame([{"Livro": novo_desejo, "Status": "Pendente"}])
            df_wishlist = pd.concat([df_wishlist, novo], ignore_index=True)
            df_wishlist.to_csv("wishlist.csv", index=False)
            st.rerun()

    if not df_wishlist.empty:
        st.write("---") 
        hw1, hw2, hw3 = st.columns([7, 1, 1], vertical_alignment="bottom")
        hw1.write("**Livro**")
        hw2.write("**Lido**")
        hw3.write("**Excluir**")
        
        for i, row in df_wishlist.iterrows():
            w1, w2, w3 = st.columns([7, 1, 1], vertical_alignment="center")
            
            if row["Status"] == "Lido":
                w1.write(f"~~{row['Livro']}~~")
            else:
                w1.write(row["Livro"])
            
            icone = ":material/check_box:" if row["Status"] == "Lido" else ":material/check_box_outline_blank:"
            if w2.button(icone, key=f"check_wish_{i}"):
                df_wishlist.at[i, "Status"] = "Pendente" if row["Status"] == "Lido" else "Lido"
                df_wishlist.to_csv("wishlist.csv", index=False)
                st.rerun()
            
            if w3.button(":material/delete:", key=f"del_wish_{i}"):
                df_wishlist = df_wishlist.drop(i)
                df_wishlist.to_csv("wishlist.csv", index=False)
                st.rerun()