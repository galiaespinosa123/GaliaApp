import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import google.generativeai as genai

# ----------------- CONFIGURACIÓN GEMINI -----------------
api_key = "AIzaSyCPyb9KQcsRe87k_T9WJmLTHtIt340pHHw"  # <-- ¡Reemplaza con tu clave!
genai.configure(api_key=api_key)
modelo = genai.GenerativeModel("gemini-2.0-flash")

# ----------------- CONFIG DE LA PÁGINA -----------------
st.set_page_config(page_title="Análisis Financiero de Riesgos", layout="wide")
st.markdown("""
    <style>
        body {
            background-color: #FFFFFF;
            color: black;
            font-family: Arial, sans-serif;
        }
        .stApp {
            background-color: #000000;
            padding: 20px;
            border-radius: 10px;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: black;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Analista de Riesgos Financieros")

# ----------------- INPUT DEL USUARIO -----------------
symbols = st.text_input("📌 Ingresa los símbolos bursátiles separados por comas (ejemplo: AAPL, MSFT, TSLA):")

if symbols:
    tickers = [s.strip().upper() for s in symbols.split(",")]

    try:
        for symbol in tickers:
            st.subheader(f"🏢 Descripción de {symbol}")
            info = yf.Ticker(symbol).info
            descripcion = info.get("longBusinessSummary", "No se encontró descripción.")

            # ----------------- TRADUCCIÓN DE DESCRIPCIÓN -----------------
            prompt_traduccion = f"Traduce al español la siguiente descripción: {descripcion}"
            try:
                respuesta_traduccion = modelo.generate_content(prompt_traduccion)
                traduccion = respuesta_traduccion.text
            except Exception as e:
                st.warning(f"Error al traducir con Gemini: {e}")
                traduccion = descripcion

            st.markdown(traduccion)

            # ----------------- RESUMEN SIMPLIFICADO -----------------
            prompt_resumen = f"Resume esta descripción en español: {traduccion}"
            try:
                respuesta_resumen = modelo.generate_content(prompt_resumen)
                st.success(respuesta_resumen.text)
            except Exception as e:
                st.warning(f"Error al resumir con Gemini: {e}")

        # ----------------- GRÁFICOS -----------------
        st.subheader("📈 Análisis Gráfico")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📉 Datos Históricos")
            precios_historicos = {}
            for symbol in tickers:
                data = yf.download(symbol, period="5y").dropna()
                if not data.empty:
                    precios_historicos[symbol] = data["Close"]
            if precios_historicos:
                df_historicos = pd.DataFrame(precios_historicos)
                if not df_historicos.empty:
                    fig_hist = go.Figure()
                    for symbol in df_historicos.columns:
                        fig_hist.add_trace(go.Scatter(x=df_historicos.index, y=df_historicos[symbol], mode='lines', name=symbol))
                    fig_hist.update_layout(title="Precios Históricos", xaxis_title="Fecha", yaxis_title="Precio", template="plotly_dark")
                    st.plotly_chart(fig_hist, use_container_width=True)

        with col2:
            st.subheader("📊 Comparación con Índices")
            indices = ["SPY", "QQQ", "DJI"]
            precios_indices = yf.download(indices, period="5y")
            if "Close" in precios_indices:
                precios_indices = precios_indices["Close"].dropna()
                if not precios_indices.empty:
                    fig_indices = go.Figure()
                    for ticker in precios_indices.columns:
                        fig_indices.add_trace(go.Scatter(x=precios_indices.index, y=precios_indices[ticker], mode='lines', name=ticker))
                    fig_indices.update_layout(title="Comparación con Índices", xaxis_title="Fecha", yaxis_title="Precio", template="plotly_dark")
                    st.plotly_chart(fig_indices, use_container_width=True)

        # ----------------- ANÁLISIS AVANZADO -----------------
        st.subheader("📋 Análisis Financiero Avanzado (Gemini)")
        instrucciones = """
        Eres un analista financiero experto. Analiza los siguientes datos financieros de los índices SPY, QQQ y DJI y proporciona un análisis estructurado que incluya:
        1️⃣ **Resumen ejecutivo**: Situación actual del mercado.
        2️⃣ **Contexto macroeconómico**: Factores globales que afectan el mercado.
        3️⃣ **Análisis técnico**: Patrones de tendencias basados en los datos.
        4️⃣ **Evaluación y gestión de riesgos**: Posibles riesgos.
        5️⃣ **Escenarios posibles**: Explicación de escenarios (sin recomendaciones).

        Datos clave:
        """
        if not precios_indices.empty:
            datos_relevantes = precios_indices.describe().to_string()
            prompt_analisis = instrucciones + datos_relevantes
            try:
                respuesta_analisis = modelo.generate_content(prompt_analisis)
                st.info(respuesta_analisis.text)
            except Exception as e:
                st.warning(f"Error en análisis avanzado con Gemini: {e}")
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")