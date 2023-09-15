#=====================================
#Bibliotecas
#=====================================
import pandas as pd
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
from datetime import datetime

st.set_page_config(page_title="Visão Entregadores", page_icon="", layout="wide")


#=====================================
#Funções
#=====================================
def clean_code(df):
    """ Esta função tem a responsabilidade de limpar o dataframe
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaçoes das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável munérica)
        Input: Dataframe
        Output: Dataframe
    """
    #remover espaço da string
    df.loc[:, "ID"] = df.loc[:, "ID"].str.strip()
    df.loc[:, "Delivery_person_ID"] = df.loc[:, "Delivery_person_ID"].str.strip()
    df.loc[:, "Weatherconditions"] = df.loc[:, "Weatherconditions"].str.strip()
    df.loc[:, "Road_traffic_density"] = df.loc[:, "Road_traffic_density"].str.strip()
    df.loc[:, "Type_of_order"] = df.loc[:, "Type_of_order"].str.strip()
    df.loc[:, "Type_of_vehicle"] = df.loc[:, "Type_of_vehicle"].str.strip()
    df.loc[:, "Festival"] = df.loc[:, "Festival"].str.strip()
    df.loc[:, "City"] = df.loc[:, "City"].str.strip()

      # Excluir as linhas com a idade dos entregadores vazia
    # ( Conceitos de seleção condicional )
    linhas_vazias = df["Delivery_person_Age"] != "NaN "
    df = df.loc[linhas_vazias]

    linhas_vazias = df["City"] != "NaN"
    df = df.loc[linhas_vazias]

    linhas_vazias = df["Road_traffic_density"] != "NaN"
    df = df.loc[linhas_vazias]

    linhas_vazias = df["Festival"] != "NaN"
    df = df.loc[linhas_vazias]

    # Conversao de texto/categoria/string para numeros inteiros
    df["Delivery_person_Age"] = df["Delivery_person_Age"].astype(int)

    # Conversao de texto/categoria/strings para numeros decimais
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )

    # Conversao de texto para data
    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )

    linhas_vazias = df['multiple_deliveries'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )

    # Comando para resetar o index números
    df = df.reset_index( drop=True )
    #for i in range( len( df ) ):
     # df.loc[i, 'Time_taken(min)'] = re.findall( r'\d+', df.loc[i, 'Time_taken(min)'] )

    df["Time_taken(min)"] = df["Time_taken(min)"].apply( lambda x: x.split("(min) ")[1])
    df["Time_taken(min)"] = df["Time_taken(min)"].astype( int )

    return df
#___________________________________________________________

def  top_delivers(df1, top_asc):
    df2 = df1.loc[:, ["Delivery_person_ID", "City", "Time_taken(min)"]].groupby(["City", "Delivery_person_ID"]).mean().sort_values(["City", "Time_taken(min)"], ascending=top_asc).reset_index()
    df_aux01 = df2.loc[df2["City"] == "Metropolitian", :].head(10)
    df_aux02 = df2.loc[df2["City"] == "Semi-Urban", :].head(10)
    df_aux03 = df2.loc[df2["City"] == "Urban", :].head(10)
    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop = True)
    return df3

#___________________________________________________________


#---------------------------------------------------Início da Estrutua lógica do código------------------------------------------------------------------------------
#=====================================
#Dataset
#=====================================
df = pd.read_csv("train.csv")

#=====================================
#Limpanda os dados
#=====================================
df1 = clean_code(df)


#=====================================
#Barra Lateral
#=====================================

#image_path = "C:/Users/henri/Documents/Repos/FTC/Ciclo_6/logo.png"
image = Image.open("logo.png")
st.sidebar.image(image, width=230)

#Seleção data
st.sidebar.markdown("# Curry Company")
st.sidebar.markdown("## Fastest Delivery in Town")
st.sidebar.markdown("""---""")
st.sidebar.markdown("## Selecione uma data limite")

#Seleção data
date_slider = st.sidebar.slider("Até qual valor?", 
                  value = datetime(2022, 4, 13),
                  min_value = datetime(2022, 2, 11),
                  max_value = datetime(2022, 4, 6),
                 format = "DD-MM-YYYY")

st.sidebar.markdown("""---""")

#Seleção trânsito
traffic_options = st.sidebar.multiselect("Quais as condições do trânsito",
                      ["Low", "Medium", "High", "Jam"],
                      default = "Low")


st.sidebar.markdown("""---""")


#Seleção clima
weather_conditions = st.sidebar.multiselect("Quais as condições do clima",
                     ["conditions Cloudy", "conditions Fog", "conditions Sandstorms", "conditions Stormy", "conditions Sunny", "conditions Windy"],
                      default = "conditions Sunny")


st.sidebar.markdown("""---""")

st.sidebar.markdown("Feito por mim")


#Filtro de data
linhas_selecionadas = df1["Order_Date"] <= date_slider
df1 = df1.loc[linhas_selecionadas, :]


#Filtro de trânsito
linhas_selecionadas = df1["Road_traffic_density"].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de Clima
linhas_selecionadas = df1["Weatherconditions"].isin(weather_conditions)
df1 = df1.loc[linhas_selecionadas, :]

#=====================================
#Layout Streamlit 
#Visão Entregadores
#=====================================
st.header('MarketPlace - Visão Entregadores')
tab1, tab2, tab3 = st.tabs(["Visão Gerencial", "", ""])
with tab1:
    with st.container():
        st.title("Overall Metrics")
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        
        with col1:
            #maior idade dos entregadores
            maior_idade = df1.loc[:, "Delivery_person_Age"].max()
            col1.metric("Maior Iade", maior_idade)
        
        with col2:
            #menor idade dos entregadores
            menor_idade = df1.loc[:, "Delivery_person_Age"].min()
            col2.metric("Menor Idade", menor_idade)
        
        with col3:
            #melhor condição do veículo
            melhor_veiculo = df1.loc[:, "Vehicle_condition"].max()
            col3.metric("Melhor Condição", melhor_veiculo)
        
        with col4:
            #pior condição do veículo
            pior_veiculo = df1.loc[:, "Vehicle_condition"].min()
            col4.metric("Pior Condição", pior_veiculo)
    
    with st.container():
        st.markdown("""---""")
        st.title("Avaliações")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Avaliações médias por Entregador")
            df_avg = df1.loc[:, ["Delivery_person_ID", "Delivery_person_Ratings"]].groupby("Delivery_person_ID").mean().reset_index()
            st.dataframe(df_avg)
        
        with col2:
            st.markdown("##### Avaliação Média por Trânsito")
            df_avg_std_traf = df1.loc[:, ["Delivery_person_Ratings", "Road_traffic_density"]].groupby("Road_traffic_density").agg({"Delivery_person_Ratings": ["mean", "std"]})
            df_avg_std_traf.columns = ["delivery_mean", "delivery_std"]
            st.dataframe(df_avg_std_traf.reset_index())
            
            
            st.markdown("##### Avaliação Média por Clima")
            df_avg_std_wheat = df1.loc[:, ["Delivery_person_Ratings", "Weatherconditions"]].groupby("Weatherconditions").agg({"Delivery_person_Ratings": ["mean", "std"]})
            df_avg_std_wheat.columns = ["delivery_mean", "delivery_std"]
            st.dataframe(df_avg_std_wheat.reset_index())
    
    with st.container():
        st.markdown("""---""")
        st.title("Velocidade de Entrega")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### Top Entregadores mais rápidos")
            df3 = top_delivers(df1, top_asc=True)
            st.dataframe(df3)
        
        with col2:
            st.markdown("##### Top Entregadores mais lentos")
            df3 = top_delivers(df1, top_asc=False)
            st.dataframe(df3)
