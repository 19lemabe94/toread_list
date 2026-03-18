import streamlit as st
import pandas as pd
import os
from datetime import date

# Layout "wide" ajuda a dar mais espaço para os campos na mesma linha
st.set_page_config(page_title="To Read List", page_icon="⛾", layout="wide")
st.title("⛾ To Read List")

def carregar(arquivo, colunas):
    return pd.read_csv(arquivo) if os.path.exists(arquivo) else pd.DataFrame(columns=colunas)

df_diario = carregar("diario.csv", ["Data", "Livro", "Páginas"])
df_wishlist = carregar("wishlist.csv", ["Livro"])

aba_diario, aba_wishlist = st.tabs([":material/menu_book: Diário", ":material/shopping_cart_checkout: Wishlist"])

# --- ABA 1: DIÁRIO ---
with aba_diario:
    # border=False remove a caixa em volta
    with st.form("form_leitura", clear_on_submit=True, border=False):
        # Divide a tela em 4 colunas proporcionais na mesma linha
        col1, col2, col3, col4 = st.columns([2, 4, 2, 2], vertical_alignment="bottom")
        
        with col1:
            data = st.date_input("Data", value=date.today())
        with col2:
            livro = st.text_input("Livro")
        with col3:
            paginas = st.number_input("Páginas lidas", min_value=1, step=1)
        with col4:
            salvar = st.form_submit_button("Salvar")
        
        if salvar and livro:
            novo = pd.DataFrame([{"Data": data.strftime("%d/%m/%Y"), "Livro": livro, "Páginas": paginas}])
            df_diario = pd.concat([df_diario, novo], ignore_index=True)
            df_diario.to_csv("diario.csv", index=False)
            st.rerun()

    st.dataframe(df_diario, use_container_width=True, hide_index=True)

# --- ABA 2: WISHLIST ---
with aba_wishlist:
    with st.form("form_wishlist", clear_on_submit=True, border=False):
        colA, colB = st.columns([8, 2], vertical_alignment="bottom")
        
        with colA:
            novo_desejo = st.text_input("Novo livro")
        with colB:
            adicionar = st.form_submit_button(":material/add: Adicionar")
        
        if adicionar and novo_desejo:
            novo = pd.DataFrame([{"Livro": novo_desejo}])
            df_wishlist = pd.concat([df_wishlist, novo], ignore_index=True)
            df_wishlist.to_csv("wishlist.csv", index=False)
            st.rerun()

    st.dataframe(df_wishlist, use_container_width=True, hide_index=True)