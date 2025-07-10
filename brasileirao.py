import streamlit as st
import pandas as pd
from mplsoccer import VerticalPitch
import json

# --- Título da Aplicação ---
st.set_page_config(layout="wide")
st.title("Brasileirão Série A 2024 - Análise de Chutes ⚽")
st.markdown("Use os filtros abaixo para visualizar os chutes a gol de cada time e jogador.")

# --- Carregamento de Dados (APENAS DO ARQUIVO LOCAL) ---
ARQUIVO_DADOS = "dados_brasileirao.json"

@st.cache_data
def carregar_dados(caminho_arquivo):
    """
    Função para carregar os dados do arquivo JSON.
    O decorador @st.cache_data garante que os dados sejam carregados apenas uma vez.
    """
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        df = pd.DataFrame(dados)
        # Converter colunas para tipo numérico, tratando erros
        df['coord_X'] = pd.to_numeric(df['coord_X'], errors='coerce')
        df['coord_Y'] = pd.to_numeric(df['coord_Y'], errors='coerce')
        df['xg'] = pd.to_numeric(df['xg'], errors='coerce')
        # Remover linhas onde a conversão falhou
        df.dropna(subset=['coord_X', 'coord_Y', 'xg'], inplace=True)
        return df
    except FileNotFoundError:
        st.error(f"Erro: Arquivo de dados '{caminho_arquivo}' não encontrado. Por favor, execute o script 'scraper.py' primeiro.")
        return pd.DataFrame() # Retorna um DataFrame vazio se o arquivo não existir

df = carregar_dados(ARQUIVO_DADOS)

if not df.empty:
    # --- Barra Lateral de Filtros ---
    st.sidebar.header("Filtros")
    
    times_disponiveis = sorted(df['time'].unique())
    time_selecionado = st.sidebar.selectbox('Selecione um time', times_disponiveis, index=None, placeholder="Todos os times")

    # Filtra o DataFrame baseado no time selecionado
    if time_selecionado:
        df_filtrado_time = df[df['time'] == time_selecionado]
    else:
        df_filtrado_time = df

    jogadores_disponiveis = sorted(df_filtrado_time['nome'].unique())
    jogador_selecionado = st.sidebar.selectbox('Selecione um jogador', jogadores_disponiveis, index=None, placeholder="Todos os jogadores")
    
    # Filtra o DataFrame final baseado no jogador
    if jogador_selecionado:
        df_final = df_filtrado_time[df_filtrado_time['nome'] == jogador_selecionado]
    else:
        df_final = df_filtrado_time

    # --- Exibição Principal ---
    col1, col2 = st.columns((1, 1.5))

    with col1:
        st.subheader("Estatísticas Gerais")
        total_chutes = len(df_final)
        total_gols = len(df_final[df_final['chute'] == 'goal'])
        total_xg = df_final['xg'].sum()
        
        st.metric("Total de Chutes", f"{total_chutes}")
        st.metric("Total de Gols", f"{total_gols}")
        st.metric("xG (Gols Esperados) Total", f"{total_xg:.2f}")

        st.subheader("Top 5 Finalizadores")
        st.dataframe(df_final.groupby('nome')['chute'].count().nlargest(5).reset_index(name='Chutes'))

    with col2:
        st.subheader("Mapa de Chutes")
        pitch = VerticalPitch(pitch_type='opta', half=True, pad_bottom=-20)
        fig, ax = pitch.draw(figsize=(10, 10))

        # Plota os chutes
        for _, chute in df_final.iterrows():
            pitch.scatter(
                x=100 - chute['coord_X'],
                y=100 - chute['coord_Y'],
                ax=ax,
                s=700 * chute['xg'],  # Tamanho da bola proporcional ao xG
                c='green' if chute['chute'] == 'goal' else 'white',
                edgecolors='black',
                alpha=1 if chute['chute'] == 'goal' else 0.7,
                zorder=2
            )
        
        st.pyplot(fig)