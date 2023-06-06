import streamlit as st
import pandas as pd
import requests

def baixaDeputados(idLegislatura):
    url = 'https://dadosabertos.camara.leg.br/api/v2/deputados?idLegislatura=' + str(idLegislatura)
    r = requests.get(url)
    deputados = r.json()['dados']
    df = pd.DataFrame(deputados)
    return df

def obterDespesasDeputado(idDeputado):
    url = 'https://dadosabertos.camara.leg.br/api/v2/deputados/' + str(idDeputado) + '/despesas'
    r = requests.get(url)
    despesas = r.json()['dados']
    df = pd.DataFrame(despesas)
    return df

st.title('Lista de Deputados em Exercício')


st.header('Lista de deputados')
st.write(df)
st.download_button('Baixar lista de deputados', data=df.to_csv(), file_name='deputados.csv', mime='text/csv')

st.header('Gráficos')
st.subheader('Número de deputados por partido')
st.bar_chart(df['siglaPartido'].value_counts())
st.subheader('Número de deputados por estado')
st.bar_chart(df['siglaUf'].value_counts())

st.header('Lista de deputados por estado')
coluna1, coluna2 = st.columns(2)
estado = coluna1.selectbox('Escolha um estado', sorted(df['siglaUf'].unique()), index=25)
partido = coluna2.selectbox('Escolha um partido', sorted(df['siglaPartido'].unique()))
df2 = df[(df['siglaUf'] == estado) & (df['siglaPartido'] == partido)]
st.markdown('---')

if df2.empty:
    st.subheader(':no_entry_sign: Sem deputados nesse estado filiados a esse partido! :crying_cat_face:')
else:
    total_despesas_partido = 0
    for index, linha in df2.iterrows():
        with st.expander(linha['nome']):
            st.image(linha['urlFoto'], width=130)
            st.write('Nome: ' + linha['nome'])
            st.write('Partido: ' + linha['siglaPartido'])
            st.write('UF: ' + linha['siglaUf'])
            st.write('ID: ' + str(linha['id']))
            st.write('Email: ' + str(linha['email']))
            st.write('---')
            st.write('Despesas:')
            despesas_df = obterDespesasDeputado(linha['id'])
            st.write(despesas_df)
            total_despesas_deputado = despesas_df['valorLiquido'].sum()
            st.markdown(f'<h2 style="color:red;">Total de Despesas do Deputado: R${total_despesas_deputado:.2f}</h2>', unsafe_allow_html=True)
            total_despesas_partido += total_despesas_deputado
