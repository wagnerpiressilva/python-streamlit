import streamlit as st
from Configs_Modulo import *

def main():
    st.set_page_config(page_title='Configurações',page_icon='⚙️',layout='wide',initial_sidebar_state='expanded')

    st.subheader("Aba_Juros_Compostos", divider="red", anchor=False)
    st.write('param_pagamento: ',config['Aba_Juros_Compostos']['param_pagamento'])
    st.write('param_meta_tipo: ',config['Aba_Juros_Compostos']['param_meta_tipo'])
    st.write('param_meta_valor: ',config['Aba_Juros_Compostos']['param_meta_valor'])

    st.subheader("Aba_Indicacoes", divider="red", anchor=False)
    st.write('arquivo_excel: ',config['Aba_Indicacoes']['arquivo_excel'])

    st.subheader("Aba_Google", divider="red", anchor=False)
    st.write(config['Aba_Google']['url'])

    st.subheader("Aba_Historico", divider="red", anchor=False)
    st.write('arquivo_excel: ',config['Aba_Historico']['arquivo_excel'])

    st.subheader("Nota_Negociacao_B3", divider="red", anchor=False)
    st.write(config['Nota_Negociacao_B3']['pasta'])

    st.subheader("Conversor_Extrato", divider="red", anchor=False)
    st.write('arquivo_excel: ',config['Conversor_Extrato']['arquivo_excel'])

if __name__ == "__main__":
    main()