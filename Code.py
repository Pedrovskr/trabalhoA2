import streamlit as st
import pandas as pd
import requests

def get_deputies(legislature_id):
    url = f'https://dadosabertos.camara.leg.br/api/v2/deputados?idLegislatura={legislature_id}'
    response = requests.get(url)
    deputies = response.json()['dados']
    df = pd.DataFrame(deputies)
    return df

def get_deputy_expenses(deputy_id):
    url = f'https://dadosabertos.camara.leg.br/api/v2/deputados/{deputy_id}/despesas'
    response = requests.get(url)
    expenses = response.json()['dados']
    df = pd.DataFrame(expenses)
    return df

st.title('Lista de Deputados em Exercício')

legislature_id = st.slider('Escolha de qual legislatura você quer a lista de deputados', 50, 57, 57)
df = get_deputies(legislature_id)

st.header('Lista de deputados')
st.write(df)
st.download_button('Baixar lista de deputados', data=df.to_csv(), file_name='deputados.csv', mime='text/csv')

st.header('Gráficos')
st.subheader('Número de deputados por partido')
st.bar_chart(df['siglaPartido'].value_counts())
st.subheader('Número de deputados por estado')
st.bar_chart(df['siglaUf'].value_counts())

st.header('Lista de deputados por estado')
col1, col2 = st.columns(2)
state = col1.selectbox('Escolha um estado', sorted(df['siglaUf'].unique()), index=25)
party = col2.selectbox('Escolha um partido', sorted(df['siglaPartido'].unique()))
df_filtered = df[(df['siglaUf'] == state) & (df['siglaPartido'] == party)]
st.markdown('---')

if df_filtered.empty:
    st.subheader(':no_entry_sign: Sem deputados nesse estado filiados a esse partido! :crying_cat_face:')
else:
    total_party_expenses = 0
    for _, row in df_filtered.iterrows():
        with st.expander(row['nome']):
            st.image(row['urlFoto'], width=130)
            st.write('Nome:', row['nome'])
            st.write('Partido:', row['siglaPartido'])
            st.write('UF:', row['siglaUf'])
            st.write('ID:', row['id'])
            st.write('Email:', row['email'])
            st.write('---')
            st.write('Despesas:')
            expenses_df = get_deputy_expenses(row['id'])
            st.write(expenses_df)
            total_deputy_expenses = expenses_df['valorLiquido'].sum()
            st.markdown(f'<h2 style="color:red;">Total de Despesas do Deputado: R${total_deputy_expenses:.2f}</h2>', unsafe_allow_html=True)
            total_party_expenses += total_deputy_expenses
