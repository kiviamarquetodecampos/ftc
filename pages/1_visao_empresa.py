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


st.set_page_config(page_title="Visão Empresa", page_icon="", layout="wide")


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

def order_metric(df1):
    """ Função que retorna o gráfico de barras 
    """
    cols = ["ID", "Order_Date"]
    df_aux = df1.loc[:, cols].groupby("Order_Date").count().reset_index()
    fig = px.bar(df_aux, x = "Order_Date", y = "ID")
    return fig
#___________________________________________________________

def traffic_order_share(df1):
    """ Função que retorna o gráfico de pizza
    """
    df_aux = df1.loc[:, ["ID", "Road_traffic_density"]].groupby("Road_traffic_density").count().reset_index()
    df_aux["entregas_perc"] = df_aux["ID"]/ df_aux["ID"].sum()
    fig = px.pie(df_aux, values = "entregas_perc", names = "Road_traffic_density")
    return fig
#___________________________________________________________

def traffic_order_city(df1):
    """ Função que retorna o gráfico de bolha
    """
    df_aux = df1.loc[:, ["ID", "City", "Road_traffic_density"]].groupby(["City", "Road_traffic_density"]).count().reset_index()
    fig = px.scatter(df_aux, x = "City", y = "Road_traffic_density", size = "ID")
    return fig
#___________________________________________________________

def order_by_week(df1):
    """ Função que retorna o gráfico de linha por semana
    """
    df1["week_of_year"] = df1["Order_Date"].dt.strftime("%u")
    df_aux = df1.loc[:, ["ID", "week_of_year"]].groupby("week_of_year").count().reset_index()
    fig = px.line(df_aux, x = "week_of_year", y = "ID")
    return fig

#___________________________________________________________

def order_share_by_week(df1):
    df_aux01 = df1.loc[:, ["ID", "week_of_year"]].groupby("week_of_year").count().reset_index()
    df_aux02 = df1.loc[:, ["Delivery_person_ID", "week_of_year"]].groupby("week_of_year").nunique().reset_index()
    df_aux = pd.merge(df_aux01, df_aux02, how = "inner")
    df_aux["order_by_delivery"] = df_aux["ID"]/df_aux["Delivery_person_ID"]
    fig = px.line(df_aux, x = "week_of_year", y = "order_by_delivery")
    return fig


#___________________________________________________________

def country_maps(df1):
    """ Função que desenha o mapa
    """
    df_aux = df1.loc[:, ["City", "Road_traffic_density", "Delivery_location_latitude", "Delivery_location_longitude"]].groupby(["City", "Road_traffic_density"]).median().reset_index()
    map = folium.Map()
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info["Delivery_location_latitude"], location_info["Delivery_location_longitude"]], popup = location_info[["City", "Road_traffic_density"]]).add_to(map)
    folium_static(map, width=1024, height=600)



#---------------------------------------------------Início da Estrutua lógica do código------------------------------------------------------------------------------

#=====================================
#Dataset
#=====================================
df = pd.read_csv("../train.csv")

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

st.sidebar.markdown("# Curry Company")
st.sidebar.markdown("## Fastest Delivery in Town")
st.sidebar.markdown("""---""")
st.sidebar.markdown("## Selecione uma data limite")

#Seleção data
date_slider = st.sidebar.slider("Até qual valor?", 
                  value = pd.datetime(2022, 4, 13),
                  min_value = pd.datetime(2022, 2, 11),
                  max_value = pd.datetime(2022, 4, 6),
                 format = "DD-MM-YYYY")

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect("Quais as condições do trânsito",
                      ["Low", "Medium", "High", "Jam"],
                      default = "Low")

st.sidebar.markdown("""---""")

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
#Visão Empresa
#=====================================

st.header('MarketPlace - Visão Empresa')
tab1, tab2, tab3 = st.tabs(["Visão Gerencial", "Visão Tática", "Visão Geográfica"])
with tab1:
    with st.container():
        #Order Metric
        st.markdown("### Orders by Day")
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)
    
    with st.container():    
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Traffic Order Share")
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.markdown("### Traffic Order City")
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width=True)


with tab2:
    with st.container():
        st.markdown("# Order by Week")
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
    
    with st.container():
        st.markdown("# Order Share by Week")
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
        
with tab3:
    st.header("Country Maps")
    country_maps(df1)
