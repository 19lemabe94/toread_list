import streamlit as st
import pandas as pd
import os
from datetime import date

# 1. Configuração da página
st.set_page_config(page_title="To Read List", page_icon="⛾", layout="centered")

# 2. Injeção de CSS customizado
st.markdown("""
    <style>
    h1 {
        text-align: center;
        font-weight: 400;
        padding-bottom: 20px;
    }
    button[data-baseweb="tab"] p {
        font-size: 18px !important;
        font-weight: 500;
    }
    div[data-testid="stMetricValue"] > div {
        justify-content: center;
    }
    div[data-testid="stMetricLabel"] > div {
        justify-content: center;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: transparent;
        text-align: right;
        font-size: 14px;
        padding: 12px 20px;
        z-index: 999;
    }
    .footer a {
        color: #888;
        text-decoration: none;
        font-weight: bold;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        justify-content: flex-end; 
    }
    .footer a:hover {
        color: #222;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>⛾ To Read List</h1>", unsafe_allow_html=True)

# --- Funções e Carregamento de Dados ---
def carregar(ficheiro, colunas):
    return pd.read_csv(ficheiro) if os.path.exists(ficheiro) else pd.DataFrame(columns=colunas)

df_diario = carregar("diario.csv", ["Data", "Livro", "Páginas"])
df_wishlist = carregar("wishlist.csv", ["Livro", "Status"])
df_livros = carregar("livros.csv", ["Livro", "Status"])

if "Status" not in df_wishlist.columns:
    df_wishlist["Status"] = "Pendente"

if df_livros.empty and not df_diario.empty:
    livros_unicos = df_diario["Livro"].unique()
    df_livros = pd.DataFrame({"Livro": livros_unicos, "Status": ["Em Progresso"] * len(livros_unicos)})
    df_livros.to_csv("livros.csv", index=False)

aba_diario, aba_livros, aba_wishlist = st.tabs([
    ":material/calendar_add_on: Diário", 
    ":material/book_5: Meus Livros", 
    ":material/person_heart: Wishlist"
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
        st.markdown(f"### :material/event: {total_paginas} páginas")

    with st.form("form_leitura", clear_on_submit=True, border=False):
        col1, col2, col3, col4 = st.columns([3, 3, 2, 2], vertical_alignment="bottom")
        
        # Puxa os livros em progresso E os livros pendentes da wishlist
        livros_ativos = df_livros[df_livros["Status"] == "Em Progresso"]["Livro"].tolist()
        livros_desejados = df_wishlist[df_wishlist["Status"] == "Pendente"]["Livro"].tolist()
        
        # Junta as duas listas evitando duplicatas
        lista_opcoes = livros_ativos + [l for l in livros_desejados if l not in livros_ativos]
        opcoes = [""] + lista_opcoes if lista_opcoes else [""]
        
        with col1:
            livro_selecionado = st.selectbox("Em Progresso / Wishlist", opcoes)
        with col2:
            livro_novo = st.text_input("Ou registre um novo")
        with col3:
            paginas = st.number_input("Páginas lidas", min_value=1, step=1)
        with col4:
            salvar = st.form_submit_button("Salvar")
        
        if salvar:
            livro_final = livro_novo if livro_novo.strip() else livro_selecionado
            
            if livro_final:
                # 1. Se o livro estava na Wishlist, remove de lá (sincronização)
                if livro_final in df_wishlist["Livro"].values:
                    df_wishlist = df_wishlist[df_wishlist["Livro"] != livro_final]
                    df_wishlist.to_csv("wishlist.csv", index=False)

                # 2. Se o livro não está na biblioteca, adiciona como "Em Progresso"
                if livro_final not in df_livros["Livro"].values:
                    novo_l = pd.DataFrame([{"Livro": livro_final, "Status": "Em Progresso"}])
                    df_livros = pd.concat([df_livros, novo_l], ignore_index=True)
                    df_livros.to_csv("livros.csv", index=False)
                
                # 3. Salva a leitura no Diário
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

# --- ABA 2: MEUS LIVROS ---
with aba_livros:
    total_paginas_geral = df_diario["Páginas"].sum() if not df_diario.empty else 0
    total_livros_lidos = len(df_livros[df_livros["Status"] == "Lido"]) if not df_livros.empty else 0
    
    m1, m2 = st.columns(2)
    m1.metric(":material/done_outline: Livros Lidos", total_livros_lidos)
    m2.metric(" :material/auto_stories: Páginas Totais Lidas", total_paginas_geral)
    
    if not df_livros.empty:
        st.write("---") 
        hl1, hl2, hl3, hl4 = st.columns([5, 2, 1, 1], vertical_alignment="bottom")
        hl1.write("**Livro**")
        hl2.write("**Progresso**")
        hl3.write("**Lido**")
        hl4.write("**Excluir**")
        
        for i, row in df_livros.iterrows():
            l1, l2, l3, l4 = st.columns([5, 2, 1, 1], vertical_alignment="center")
            
            pags_livro = df_diario[df_diario["Livro"] == row["Livro"]]["Páginas"].sum()
            
            if row["Status"] == "Lido":
                l1.write(f"~~{row['Livro']}~~")
            else:
                l1.write(row["Livro"])
                
            l2.write(f"{pags_livro} págs")
            
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

# --- 3. Inserção do Rodapé HTML ---
st.markdown("""
    <div class="footer">
        <a href="https://github.com/19lemabe94" target="_blank">
            <svg height="16" width="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
            </svg>
            Created by Leo Bezerra
        </a>
    </div>
""", unsafe_allow_html=True)