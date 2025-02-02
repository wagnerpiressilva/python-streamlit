import streamlit as st
import pandas as pd
from st_aggrid import AgGrid
from Configs_Modulo import *
import locale
from st_aggrid import AgGrid, GridOptionsBuilder

# Configurar a localidade para 'pt_BR' (Português do Brasil)
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def limpa_cache():
    st.cache_data.clear()

@st.cache_data
def carregar_excel_extrato(arquivo_excel:str):
    # Define formatos das colunas
    df_extrato = pd.read_excel(arquivo_excel, sheet_name='Planilha1',thousands='.', decimal=',')
    df_extrato.rename(columns={'Unnamed: 1': 'Data','Unnamed: 2':'Liquidação','Unnamed: 3':'Ticker','Unnamed: 4':'Quantidade','Unnamed: 5':'Valor','Unnamed: 6':'Saldo (R$)'}, inplace=True)
    df_extrato['Data'] = pd.to_datetime(df_extrato['Data'], format='%Y-%m-%d',errors='coerce')
    df_extrato['Ticker'].fillna('', inplace=True)
    df_extrato = df_extrato[df_extrato['Ticker'].str.contains('RENDIMENTOS DE CLIENTES')]    
    df_extrato['Ticker'] = df_extrato['Ticker'].str.replace('RENDIMENTOS DE CLIENTES ', '')
    df_extrato['Quantidade'] = df_extrato['Ticker'].str.extract(r'S/\s*(\d+)')
    df_extrato['Ticker'] = df_extrato['Ticker'].str.extract(r'(.+?) S/')
    df_extrato = df_extrato.drop(columns=['Unnamed: 0','Liquidação', 'Saldo (R$)'])
    df_extrato['Num Nota']=''
    df_extrato['Posição']='Ativo'
    df_extrato['TP Rendimento']='Dividendos'
    df_extrato['Tipo']='FII'
    return df_extrato

def main():
    st.sidebar.button('Limpar Cache',on_click=limpa_cache)
    st.subheader("Conversor de Extrato", divider="red", anchor=False)
    df_extrato = carregar_excel_extrato(config['Conversor_Extrato']['arquivo_excel'])
    ordem = ['Data','Num Nota','Quantidade','Valor','Ticker','Posição','TP Rendimento','Tipo']
    df_extrato = df_extrato[ordem]

    # Imprime tabela de notas
    gb_options = GridOptionsBuilder()
    gb_options = gb_options.from_dataframe(df_extrato)
    gb_options.configure_default_column(filterParams={'applyMiniFilterWhileTyping': 'true'}, filter=True, sortable=True,flex=1)
    gb_options.configure_side_bar(defaultToolPanel='')
    gb_options.configure_column(field='Valor',header_name='Valor',type=["numericColumn"],valueFormatter="x.toLocaleString('pt-BR',{style: 'currency', currency: 'BRL'})",width=130)
    AgGrid(df_extrato,gb_options.build())   

if __name__ == "__main__":
    main()

