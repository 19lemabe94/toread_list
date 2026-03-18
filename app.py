import streamlit as st
import pandas as pd
import os
from datetime import date

st.set_page_config(page_title="To Read List", page_icon="⛾", layout="wide")
st.title("⛾ To Read List")

def carregar(ficheiro, colunas):
    return pd.read_csv(ficheiro) if os.path.exists(ficheiro) else pd.DataFrame(columns=colunas)

df_diario = carregar("diario.csv", ["Data", "Livro", "Páginas"])
df_wishlist = carregar("wishlist.csv", ["Livro", "Status"])

if "Status" not in df_wishlist.columns:
    df_wishlist["Status"] = "Pendente"

aba_diario, aba_wishlist = st.tabs([":material/menu_book: Diário", ":material/shopping_cart_checkout: Wishlist"])

# --- ABA 1: DIÁRIO ---
with aba_diario:
    # Navegação de Data e Contador no topo
    col_data, col_contador = st.columns([1, 3], vertical_alignment="center")
    with col_data:
        data_selecionada = st.date_input("Navegar para a data:", value=date.today())
        data_str = data_selecionada.strftime("%d/%m/%Y")
    
    # Filtrar os dados apenas para a data selecionada
    df_do_dia = df_diario[df_diario["Data"] == data_str]
    total_paginas = df_do_dia["Páginas"].sum() if not df_do_dia.empty else 0
    
    with col_contador:
        st.markdown(f"###  :material/calendar_check: {total_paginas} páginas")

    # Formulário de entrada
    with st.form("form_leitura", clear_on_submit=True, border=False):
        # A data já foi escolhida no calendário acima, pedimos apenas o livro e as páginas
        col1, col2, col3 = st.columns([5, 2, 2], vertical_alignment="bottom")
        
        with col1:
            livro = st.text_input("Livro")
        with col2:
            paginas = st.number_input("Páginas lidas", min_value=1, step=1)
        with col3:
            salvar = st.form_submit_button("Salvar")
        
        if salvar and livro:
            novo = pd.DataFrame([{"Data": data_str, "Livro": livro, "Páginas": paginas}])
            df_diario = pd.concat([df_diario, novo], ignore_index=True)
            df_diario.to_csv("diario.csv", index=False)
            st.rerun()

    # Lista de leituras do dia selecionado
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

# --- ABA 2: WISHLIST ---
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