import streamlit as st
from PIL import Image

st.set_page_config(page_title="Home", page_icon="", layout="wide")

#image_path = "C:/Users/henri/Documents/Repos/FTC/Ciclo_6/"
image = Image.open("logo.png")
st.sidebar.image(image, width=230)

st.sidebar.markdown("# Curry Company")
st.sidebar.markdown("## Fastest Delivery in Town")
st.sidebar.markdown("""---""")

st.write("# Curry Company Growth Dashboard")
st.markdown(
    """ Grownth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregadores:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes.
    ### Ask for Help
    - Time de Data Science no Discord
    """)
