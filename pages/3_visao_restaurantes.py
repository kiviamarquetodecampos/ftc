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
import numpy as np


st.set_page_config(page_title="Visão Restaurantes", page_icon="", layout="wide")

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

def distance(df1, fig):
    if fig == False:
        df1['distance'] = df1.loc[:, ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        avg_distance = np.round(df1['distance'].mean(),2)
        return avg_distance
    else:
        df1["distance"] = df1.loc[:, ["Restaurant_latitude", "Restaurant_longitude", "Delivery_location_latitude", "Delivery_location_longitude"]].apply(lambda x: haversine((x["Restaurant_latitude"], x["Restaurant_longitude"]), (x["Delivery_location_latitude"], x["Delivery_location_longitude"])), axis=1)
        avg_distance = df1.loc[:, ["City", "distance"]].groupby("City").mean().reset_index()
        fig = go.Figure(data=[go.Pie(labels=avg_distance["City"], values=avg_distance["distance"], pull=[0.01,0.1,0.01])])
        return fig

#___________________________________________________________

def avg_std_time_delivery(df1, festival, op):
    """ Está função calcula o tempo médio e o desvio padrão do tempo de entrega.
    Parâmetros:
    Input:
    - df: Dataframe com os dados necessários para para o cálculo
    op: Tipo de operação que precisa ser calculado
        "avg_time": Calcula o tempo médio
        "std_time": Calcula o desvio padrão do tempo.
     Output:
     -df: Dataframe com 2 colunas e uma linha
     """
    df_aux = df1.loc[:, ["Festival", "Time_taken(min)"]].groupby(["Festival"]).agg({"Time_taken(min)": ["mean", "std"]})
    df_aux.columns = ["avg_time", "std_time"]
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux["Festival"]== festival, op],2)
    return df_aux


#___________________________________________________________

def avg_std_time_graph(df1):
    df_aux = df1.loc[:, ["City", "Time_taken(min)"]].groupby("City").agg({"Time_taken(min)": ["mean", "std"]})
    df_aux.columns = ["avg_time", "std_time"]
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name = "Control", x=df_aux["City"], y=df_aux["avg_time"],error_y=dict(type="data",array=df_aux['std_time'] )))
    fig.update_layout(barmode="group")
    return fig

#___________________________________________________________


def avg_std_time_on_traffic(df1):
    df_aux = df1.loc[:, ["City", "Time_taken(min)", "Road_traffic_density"]].groupby(["City", "Road_traffic_density"]).agg({"Time_taken(min)": ["mean", "std"]})
    df_aux.columns = ["avg_time", "std_time"]
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=["City", "Road_traffic_density"],values="avg_time", color="std_time", color_continuous_scale="RdBu", color_continuous_midpoint=np.average(df_aux["std_time"]))
    return fig
        

#---------------------------------------------------Início da Estrutua lógica do código------------------------------------------------------------------------------
#=====================================
#Dataset
#=====================================
df = pd.read_csv("../Ciclo_6/train.csv")

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
                  value = pd.datetime(2022, 4, 13),
                  min_value = pd.datetime(2022, 2, 11),
                  max_value = pd.datetime(2022, 4, 6),
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
#Visão Restaurantes
#=====================================
st.header('MarketPlace - Visão Restaurantes')
tab1, tab2, tab3 = st.tabs(["Visão Gerencial", "", ""])
with tab1:
    with st.container():
        st.title ("Overall Metrics")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric("Entregadores", delivery_unique)
       
        with col2:
            avg_distance = distance(df1, fig = False)
            col2.metric("A distância média", avg_distance)
        
        with col3:
            df_aux = avg_std_time_delivery(df1, "Yes", "avg_time")
            col3.metric("Tempo Médio Entrega c/ Festival", df_aux)
        
        with col4:
            df_aux = avg_std_time_delivery(df1, "Yes", "std_time")
            col4.metric("Desvio Padrão c/ Festival", df_aux)
        
        with col5:
            df_aux = avg_std_time_delivery(df1, "No", "avg_time")
            col5.metric("Tempo Médio Entrega s/ Festival", df_aux)
        
        with col6:
            df_aux = avg_std_time_delivery(df1, "No", "std_time")
            col6.metric("Desvio Padrão s/ Festival", df_aux)
    
    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Tempo médio por cidade")    
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig)
        
        with col2:
            st.markdown("#### distribuição distância")
            df_aux = df1.loc[:, ["City", "Time_taken(min)", "Type_of_order"]].groupby(["City", "Type_of_order"]).agg({"Time_taken(min)": ["mean", "std"]})
            df_aux.columns = ["avg_time", "std_time"]
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux)

    with st.container():
        st.markdown("""---""")
        st.title("distribuição tempo")
         
        col1, col2 = st.columns(2)
        with col1:
            fig = distance(df1, fig = True)
            st.plotly_chart(fig)
            
        
        with col2:
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig)      
