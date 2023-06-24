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

st.title('Cadê Meu Dinheiro?')
st.subheader('Fiscalizador de Despesas')

id_legislatura = 57  
df = get_deputados(id_legislatura)

with st.expander('Lista de Deputados'):
    st.write(df)
    st.download_button('Baixar esta lista', data=df.to_csv(), file_name='deputados.csv', mime='text/csv')


st.header('Gráfico - Numero de Deputados por Estado')
st.bar_chart(df['siglaUf'].value_counts())

coluna1, coluna2 = st.columns(2)
estado = coluna1.selectbox('Escolha um estado', sorted(df['siglaUf'].unique()), index=25)
partido = coluna2.selectbox('Escolha um partido', sorted(df['siglaPartido'].unique()))
df_ = df[(df['siglaUf'] == estado) & (df['siglaPartido'] == partido)]
st.markdown('---')

if df_.empty:
    st.subheader('Não Há Deputados Disponiveis!')
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
            valorDocumento = [col for col in despesas_df.columns if 'id' in col.lower()]
            if valorDocumento in despesas_df.columns:
                despesas_df = despesas_df.groupby(valorDocumento).sum().reset_index()
            else:
                st.error('Column not found in despesas_df DataFrame')
                st.stop()  

            despesas_df = despesas_df.groupby(valorDocumento).sum().reset_index()
            despesas_df = despesas_df.sort_values('valorDocumento', ascending=False)
            st.write(despesas_df)
            despesas_totais_deputado = despesas_df['valorLiquido'].sum()
            st.markdown(f'<h2>Total de Despesas do Deputado: R${despesas_totais_deputado:.2f}</h2>', unsafe_allow_html=True)
            despesas_totais_partido += despesas_totais_deputado 
            st.subheader('*Apenas gastos pessoais, gabinete e assessores não incluídos')

            
            st.markdown('---')
    st.subheader('Total de Despesas dos Integrantes do Partido')
    st.markdown(f'<h2>R${despesas_totais_partido:.2f}</h2>', unsafe_allow_html=True)
