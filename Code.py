import streamlit as st
import pandas as pd
import requests

def get_deputados(id_legislatura):
    url = f'https://dadosabertos.camara.leg.br/api/v2/deputados?idLegislatura={id_legislatura}'
    response = requests.get(url)
    deputados = response.json()['dados']
    df = pd.DataFrame(deputados)
    return df

def get_despesas_deputados(id_deputados):
    url = f'https://dadosabertos.camara.leg.br/api/v2/deputados/{id_deputados}/despesas'
    response = requests.get(url)
    despesas = response.json()['dados']
    df = pd.DataFrame(despesas)
    return df

st.title('Saiba quanto os Deputados estão gastando - Fiscalizador de Despesas')

id_legislatura = 57  
df = get_deputados(id_legislatura)

with st.expander('Lista de deputados'):
    st.write(df)
    st.download_button('Baixar lista de deputados', data=df.to_csv(), file_name='deputados.csv', mime='text/csv')


st.header('Gráficos')
st.subheader('Número de deputados por estado')
st.bar_chart(df['siglaUf'].value_counts())

col1, col2 = st.columns(2)
state = col1.selectbox('Escolha um estado', sorted(df['siglaUf'].unique()), index=25)
party = col2.selectbox('Escolha um partido', sorted(df['siglaPartido'].unique()))
df_ = df[(df['siglaUf'] == state) & (df['siglaPartido'] == party)]
st.markdown('---')

if df_.empty:
    st.subheader('Não há deputados nesse estado filiados a esse partido!')
else:
    despesas_totais_partido = 0
    for _, row in df_.iterrows():
        with st.expander(row['nome']):
            st.image(row['urlFoto'], width=130)
            st.write('Nome:', row['nome'])
            st.write('Partido:', row['siglaPartido'])
            st.write('UF:', row['siglaUf'])
            st.write('ID:', row['id'])
            st.write('Email:', row['email'])
            st.write('---')
            st.write('Despesas:')
            despesas_df = get_despesas_deputados(row['id'])
            valorDocumento = [col for col in despesas_df.columns if 'id' in col.lower()][0]
            despesas_df = despesas_df.groupby(valorDocumento).sum().reset_index()
            despesas_df = despesas_df.sort_values('valorDocumento', ascending=False)  # Sort DataFrame in descending order
            st.write(despesas_df)
            despesas_totais_deputado = despesas_df['valorLiquido'].sum()
            st.markdown(f'<h2 style="color:red;">Total de Despesas do Deputado: R${despesas_totais_deputado:.2f}</h2>', unsafe_allow_html=True)
            despesas_totais_partido += despesas_totais_deputado
            
            st.markdown('---')
    st.subheader('Total de Despesas do Partido')
    st.markdown(f'<h2 style="color:red;">R${despesas_totais_partido:.2f}</h2>', unsafe_allow_html=True)
