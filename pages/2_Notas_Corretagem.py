import io
import os
from correpy.parsers.brokerage_notes.parser_factory import ParserFactory
import pandas as pd
import streamlit as st
from Configs_Modulo import *
from st_aggrid import AgGrid, GridOptionsBuilder

def limpa_cache():
    st.cache_data.clear()

@st.cache_data
def carrega_notas(caminho_pasta:str):
    dados = []
    # Itera sobre todos os arquivos no diretório
    for filename in os.listdir(caminho_pasta):
        # Cria o caminho completo para o arquivo
        file_path = os.path.join(caminho_pasta, filename)
        # Verifica se é um arquivo (não um diretório)
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                content = io.BytesIO(f.read())
                content.seek(0)
                brokerage_notes = ParserFactory(brokerage_note=content).parse()
                brokerage_note = brokerage_notes[0]
                for transaction in brokerage_note.transactions:
                    dados.append([brokerage_note.reference_date,brokerage_note.reference_id,transaction.transaction_type.name,transaction.amount,transaction.unit_price,transaction.security.ticker,transaction.security.name, filename])        
    return dados

def main():
    st.sidebar.button('Limpar Cache',on_click=limpa_cache)
    st.subheader('Upload de Notas de Corretagem - SINACOR', divider='red', anchor=False)
    
    # Caminho para o diretório onde os arquivos estão localizados
    st.write('Pasta:', config['Nota_Negociacao_B3']['pasta'])

    # Cria o componente de upload
    uploaded_file = st.file_uploader(
        label="Escolha um arquivo para fazer upload:",
        type=["pdf"],  # Tipos permitidos
        accept_multiple_files=False,
    )

    # Verifica se um arquivo foi carregado
    if uploaded_file is not None:
        try:
            # Opção para salvar o arquivo no servidor
            if st.button("Salvar arquivo"):
                # 2. Criar o diretório se não existir
                os.makedirs(config['Nota_Negociacao_B3']['pasta'], exist_ok=True)
                with open(os.path.join(config['Nota_Negociacao_B3']['pasta'], uploaded_file.name), "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"Arquivo {uploaded_file.name} salvo com sucesso!")
                limpa_cache()

        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {str(e)}")

    # Tabela com transações consolidadas
    try:
        df_notas = pd.DataFrame(carrega_notas(config['Nota_Negociacao_B3']['pasta']),columns=['Data','Num','Tipo','Qtd', 'Valor','Ticker','Descrição','Arquivo'])
        df_notas['Data'] = pd.to_datetime(df_notas['Data'], format='%Y-%m-%d')
        
        # Imprime tabela de notas
        gb_options = GridOptionsBuilder()
        gb_options = gb_options.from_dataframe(df_notas)
        gb_options.configure_default_column(filterParams={'applyMiniFilterWhileTyping': 'true'}, filter=True, sortable=True,flex=1)
        gb_options.configure_side_bar(defaultToolPanel='')
        gb_options.configure_column(field='Valor',header_name='Valor',type=["numericColumn"],valueFormatter="x.toLocaleString('pt-BR',{style: 'currency', currency: 'BRL'})",width=130)
        AgGrid(df_notas,gb_options.build())   
    
    except Exception as e:
            st.error(f"Erro ao processar arquivos da pasta: {str(e)}")
            
if __name__ == '__main__':
    main()