import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math
import json
import os
from datetime import datetime

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="Shadow Sim Pro | Phasscode", layout="wide")

# --- FUNÇÕES DE NÚCLEO ---

def carregar_cidades():
    """Carrega os dados geográficos do arquivo JSON local com tratamento de caminho."""
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_json = os.path.join(diretorio_atual, "data", "localidades.json")
    
    if os.path.exists(caminho_json):
        try:
            with open(caminho_json, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Erro ao ler o arquivo JSON: {e}")
            return {}
    return {}

def calcular_posicoes(lat, altura, dia_ano, hora):
    """Calcula a física da sombra e a posição do sol (Azimute e Altitude)."""
    # Declinação Solar (Cooper, 1969)
    delta = 23.45 * math.sin(math.radians(360/365 * (dia_ano - 81)))
    # Ângulo Horário (15 graus por hora)
    h_ang = (hora - 12) * 15
    lat_rad, delta_rad, h_rad = map(math.radians, [lat, delta, h_ang])
    
    # Altitude Solar (Ângulo acima do horizonte)
    sin_alpha = (math.sin(lat_rad) * math.sin(delta_rad) + 
                 math.cos(lat_rad) * math.cos(delta_rad) * math.cos(h_rad))
    
    # Se o sol está abaixo do horizonte ou rente a ele (0.001), não há sombra calculável
    if sin_alpha <= 0.001: 
        return None 
    
    alpha_rad = math.asin(sin_alpha)
    comprimento_sombra = altura / math.tan(alpha_rad)
    
    # Azimute Solar
    arg_cos = (math.sin(delta_rad) - math.sin(lat_rad) * math.sin(alpha_rad)) / (math.cos(lat_rad) * math.cos(alpha_rad))
    arg_cos = max(min(arg_cos, 1), -1) # Clamping para evitar erro de float
    gamma_deg = math.degrees(math.acos(arg_cos))
    
    if h_ang > 0: 
        gamma_deg = 360 - gamma_deg
    
    azim_sol = gamma_deg
    azim_sombra = (gamma_deg + 180) % 360 # Sombra aponta para o lado oposto ao sol
    
    return azim_sol, azim_sombra, comprimento_sombra, math.degrees(alpha_rad)

# --- BARRA LATERAL (CONTROLES) ---

st.sidebar.title("🏙️ Parâmetros do Projeto")
data_json = carregar_cidades()

if data_json:
    try:
        # Seleção Dinâmica de UF e Cidade
        uf_sel = st.sidebar.selectbox("Estado (UF)", sorted(data_json.keys()))
        mapa_cidades = {c['nome']: c for c in data_json[uf_sel]['cidades']}
        nome_cidade_sel = st.sidebar.selectbox("Cidade", sorted(mapa_cidades.keys()))
        
        cidade_info = mapa_cidades[nome_cidade_sel]
        lat = cidade_info['latitude']
        st.sidebar.success(f"📍 Latitude: {lat}")
    except Exception:
        lat, nome_cidade_sel = -8.06, "Recife (Padrão)"
        st.sidebar.warning("Usando localização padrão devido a erro na leitura.")
else:
    lat, nome_cidade_sel = -8.06, "Recife (Padrão)"
    st.sidebar.error("Arquivo 'localidades.json' não encontrado na pasta /data.")

altura_obj = st.sidebar.number_input("Altura da Estrutura (m)", value=30.0, min_value=1.0)

st.sidebar.divider()
meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
         "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
mes_nome = st.sidebar.selectbox("Mês de Análise", meses, index=5)
mes_num = meses.index(mes_nome) + 1

# Slider para movimento durante o dia (4h às 20h para captar sol do verão)
hora_simulada = st.sidebar.slider("Horário da Simulação", 4.0, 20.0, 12.0, step=0.25, format="%g h")

# --- PROCESSAMENTO DOS DADOS ---

# Definimos o dia 21 como padrão para análise sazonal
dia_ano = datetime(2026, mes_num, 21).timetuple().tm_yday
pos_atual = calcular_posicoes(lat, altura_obj, dia_ano, hora_simulada)

# Varredura completa do dia para o rastro do sol e para a tabela
relatorio_dados = []
for h in np.arange(4, 20.25, 0.25):
    res = calcular_posicoes(lat, altura_obj, dia_ano, h)
    if res:
        # REGRA: Só aparece na tabela se a sombra não for "astronômica" (limite 1000x altura)
        if res[2] < (altura_obj * 1000):
            relatorio_dados.append({
                "Hora": f"{int(h):02d}:{(int((h%1)*60)):02d}", 
                "Sombra (m)": res[2], 
                "Direção (°)": res[1], 
                "Az_Sol": res[0], 
                "Alt_Sol": res[3]
            })

df_rel = pd.DataFrame(relatorio_dados)

# --- INTERFACE PRINCIPAL ---

st.title(f"☀️ Monitor Solar: {nome_cidade_sel}")
st.markdown(f"Simulando projeção para o dia **21 de {mes_nome}**")

col1, col2 = st.columns([2, 1])

with col1:
    fig = go.Figure()

    # 1. Rastro da Trajetória do Sol (Linha dourada pontilhada)
    if not df_rel.empty:
        fig.add_trace(go.Scatterpolar(
            r=90 - df_rel["Alt_Sol"], 
            theta=df_rel["Az_Sol"], 
            mode='lines', 
            name='Trajetória do Sol',
            line=dict(color='gold', dash='dot', width=2)
        ))

    # 2. Representação da Sombra e do Sol Atual
    if pos_atual:
        az_sol, az_sombra, dist_sombra, alt_sol = pos_atual
        
        # Desenhar a sombra saindo do centro (0,0)
        # Ela aparece no gráfico mesmo se for longa (o Plotly gerencia a escala)
        fig.add_trace(go.Scatterpolar(
            r=[0, dist_sombra], 
            theta=[az_sombra, az_sombra],
            mode='lines+markers', 
            name='Sombra Projetada',
            line=dict(color='black', width=6),
            marker=dict(size=10, symbol='triangle-up')
        ))
        
        # Desenhar o Sol no céu
        fig.add_trace(go.Scatterpolar(
            r=[90 - alt_sol], 
            theta=[az_sol], 
            mode='markers', 
            name='Sol',
            marker=dict(size=18, symbol='star', color='orange', line=dict(color='yellow', width=2))
        ))
    else:
        st.warning(f"🌙 No horário de {int(hora_simulada):02d}:{(int((hora_simulada%1)*60)):02d}, o sol está abaixo do horizonte.")

    # Configuração da Bússola e Estética Polar
    fig.update_layout(
        polar=dict(
            angularaxis=dict(
                direction="clockwise", 
                rotation=90, 
                tickvals=[0, 90, 180, 270], 
                ticktext=['Norte (0°)', 'Leste (90°)', 'Sul (180°)', 'Oeste (270°)']
            ),
            radialaxis=dict(visible=True, title="Metros")
        ),
        height=750, 
        template="plotly_white",
        margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📋 Relatório Detalhado")
    if pos_atual:
        st.metric("Comprimento da Sombra", f"{pos_atual[2]:.2f} m")
        st.metric("Ângulo de Orientação", f"{pos_atual[1]:.1f}°")
    
    st.markdown("---")
    st.write(f"**Tabela de Projeções ({mes_nome})**")
    if not df_rel.empty:
        # Exibe a tabela formatada com os dados filtrados pela regra de 1000x
        st.dataframe(
            df_rel[["Hora", "Sombra (m)", "Direção (°)"]].style.format({
                "Sombra (m)": "{:.2f}",
                "Direção (°)": "{:.1f}"
            }), 
            height=500, 
            use_container_width=True
        )
    else:
        st.info("Nenhum dado solar disponível para este período.")

st.divider()
st.caption("Desenvolvido por Phasscode | Simulação Solar e Impacto Urbanístico")