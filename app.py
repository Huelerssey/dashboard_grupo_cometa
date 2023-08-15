import pandas as pd
import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.metric_cards import style_metric_cards
import plotly.express as px
from datetime import timedelta


## CONFIGURAÇÕES DA PAGINA ##

# configurações da pagina
st.set_page_config(
    page_title='Dashboard Performance',
    page_icon='📈',
    layout='wide'
)

# função que otimiza o carregamento dos dados
@st.cache_data
def carregar_dados():
    tabela = pd.read_excel("dataset/Base_de_Vendas_XPTO.xlsx")
    return tabela

# tabela otimizada
data = carregar_dados()

#aplicar estilos de css a pagina
with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

##  QUESTÃO 1 ##
# Calculando o número de clientes únicos na carteira
num_clientes = data['COD CLIENTE'].nunique()

# Calculando o faturamento total no período
faturamento_total = data['VALOR VENDIDO'].sum()

# Calculando o número total de compras realizadas no período
num_compras = data.shape[0]

##QUESTÃO 2 ##
# Calculando a média de faturamento por cliente
media_faturamento_cliente = faturamento_total / num_clientes

# Calculando a média de compras por cliente
media_compras_cliente = num_compras / num_clientes

# Organizando os dados por cliente e data de venda
data_sorted = data.sort_values(by=['COD CLIENTE', 'DATA VENDA'])

# Calculando a diferença entre as datas de compra consecutivas para cada cliente
data_sorted['DIFF'] = data_sorted.groupby('COD CLIENTE')['DATA VENDA'].diff()

# Calculando o tempo médio entre compras por cliente
tempo_medio_compras = data_sorted['DIFF'].mean()

# Convertendo o tempo médio para uma representação mais legível
tempo_medio_compras_days = tempo_medio_compras.days
tempo_medio_compras_months = tempo_medio_compras.days // 30

## QUESTÃO 3 ##
# Criando um mapeamento dos códigos dos clientes para seus nomes
cliente_mapping = data[['COD CLIENTE', 'NOME']].drop_duplicates().set_index('COD CLIENTE')['NOME'].to_dict()

# Agrupando os dados por cliente e calculando o faturamento total e o número de compras por cliente
ranking_clientes = data.groupby('COD CLIENTE').agg(
    faturamento_total=('VALOR VENDIDO', 'sum'),
    numero_compras=('VALOR VENDIDO', 'count')
).reset_index()

# Classificando os clientes pelo faturamento total em ordem decrescente
ranking_clientes = ranking_clientes.sort_values(by='faturamento_total', ascending=False)

# Selecionando os top 10 clientes
top_10_ranking = ranking_clientes.head(10).copy()

# Aplicando o mapeamento ao dataframe top_10_ranking
top_10_ranking['NOME CLIENTE'] = top_10_ranking['COD CLIENTE'].map(cliente_mapping)

# Ordenando os top 10 clientes por faturamento em ordem crescente
top_10_ranking = top_10_ranking.sort_values(by='faturamento_total', ascending=True)

## QUESTÃO 4 ##
# Clientes Novos: Aqueles que fizeram sua primeira compra no último ano.
# Clientes Perdidos: Aqueles que não fizeram compras nos últimos 2 anos e 2 meses (conforme mencionado na observação).
# Clientes Recorrentes: Aqueles que fizeram compras em mais de um ano.

# Definindo o período atual
data_atual = data['DATA VENDA'].max()

# Definindo os limites de tempo para classificar os clientes
limite_novos = data_atual - timedelta(days=365)
limite_perdidos = data_atual - timedelta(days=(2 * 365 + 2 * 30))

# Encontrando a data da primeira e última compra para cada cliente
clientes_info = data.groupby('COD CLIENTE')['DATA VENDA'].agg(
    primeira_compra='min',
    ultima_compra='max'
).reset_index()

# Classificando os clientes como novos, perdidos e recorrentes
clientes_info['status'] = 'Recorrente'
clientes_info.loc[clientes_info['primeira_compra'] > limite_novos, 'status'] = 'Novo'
clientes_info.loc[clientes_info['ultima_compra'] < limite_perdidos, 'status'] = 'Perdido'

# Contando o número de clientes em cada categoria
status_clientes = clientes_info['status'].value_counts()

## QUESTÃO 5 ##
# Extraindo o ano da data de venda
data['ANO VENDA'] = data['DATA VENDA'].dt.year

# Calculando o número de clientes únicos por ano
clientes_por_ano = data.groupby('ANO VENDA')['COD CLIENTE'].nunique()

# Calculando o número de clientes recorrentes por ano (com mais de uma compra no ano)
clientes_recorrentes_por_ano = data[data.duplicated(subset=['ANO VENDA', 'COD CLIENTE'], keep=False)].groupby('ANO VENDA')['COD CLIENTE'].nunique()

# Calculando a taxa de retenção por ano
taxa_retencao_por_ano = (clientes_recorrentes_por_ano / clientes_por_ano * 100).fillna(0)

# Criando um DataFrame com os anos e as taxas de retenção
retencao_df = pd.DataFrame({
    'Ano': taxa_retencao_por_ano.index,
    'Taxa de Retenção (%)': taxa_retencao_por_ano.values
})

##                              DASHBOARD                               ##

st.markdown("<h1 style='text-align: center;'> XPTO Dashboard Market Performance 🚀</h1>", unsafe_allow_html=True)

# marcador azul
colored_header(
label="",
description="",
color_name="light-blue-70"
)

#cria 3 colunas
coluna1, coluna2, coluna3 = st.columns(3)

# cores dos cards
style_metric_cards(
    background_color='#EEEEEE',
    border_color='#0D98E2',
    border_left_color='#0D98E2'
)

with st.container():
    # Questão 1: Métricas
    coluna1.metric("Número de Clientes", value=100)
    coluna2.metric("Faturamento Total", value="R$ 1.383.297")
    coluna3.metric("Número de Compras", value=499)

with st.container():
    # Questão 2: Métricas
    coluna1.metric("Média de Faturamento por Cliente", value="R$ 13.832,97")
    coluna2.metric("Média de Compras por Cliente", value=4.99)
    coluna3.metric("Tempo médio entre compras por Cliente", value='377 Dias')

# cria duas colunas
colu1, colu2 = st.columns(2)

with st.container():

    # Questão 3: Top 10 Clientes por Faturamento
    colu1.subheader("Top 10 Clientes por Faturamento")
    fig = px.bar(top_10_ranking, x='NOME CLIENTE', y='faturamento_total')

    # Ajustando o tamanho do gráfico
    fig.update_layout(width=800, height=500)

    # altera a cor de fundo do gráfico
    fig.update_layout(paper_bgcolor='#EEEEEE', plot_bgcolor='#EEEEEE')

    #mostra o gráfico
    colu1.plotly_chart(fig)

    # Questão 4: Distribuição de Clientes
    colu2.subheader("Distribuição de Clientes: Novos, Perdidos e Recorrentes")

    # Criando um DataFrame para o gráfico de pizza
    status_df = status_clientes.reset_index()
    status_df.columns = ['Status', 'Count']

    # Criando o gráfico de pizza com Plotly
    fig = px.pie(status_df, values='Count', names='Status')

    # Ajustando o tamanho das legendas
    fig.update_layout(legend_font=dict(size=10))

    # Ajustando o tamanho do gráfico
    fig.update_layout(width=800, height=500)

    # altera as cores de fundo
    fig.update_layout(paper_bgcolor='#EEEEEE', plot_bgcolor='#EEEEEE')

    # mostra o gráfico
    colu2.plotly_chart(fig)

with st.container():

    # Questão 5: Taxa de Retenção por Ano
    st.subheader("Taxa de Retenção por Ano")

    # Criando o gráfico de linhas com Plotly Express
    fig = px.line(retencao_df, x='Ano', y='Taxa de Retenção (%)')

    # Ajustando o tamanho do gráfico
    fig.update_layout(width=1700, height=500)

    # altera as cores de fundo
    fig.update_layout(paper_bgcolor='#EEEEEE', plot_bgcolor='#EEEEEE')

    # Exibe o gráfico no Streamlit
    st.plotly_chart(fig)

# marcador azul
colored_header(
label="",
description="",
color_name="light-blue-70"
)

#footer
with st.container():
    col1, col2, col3 = st.columns(3)
    
    col2.write("Developed By: [@Huelerssey](https://huelerssey-portfolio.website)")