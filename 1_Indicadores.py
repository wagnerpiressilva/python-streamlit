import streamlit as st
import pandas as pd
import locale
import os
import datetime
from numerize.numerize import numerize 
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from Configs_Modulo import *

# streamlit run 1_Indicadores.py

# Configurar a localidade para 'pt_BR' (Português do Brasil)
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Configurações da página no Streamlit
st.set_page_config(page_title='Indicadores',page_icon='💰',layout='wide',initial_sidebar_state='auto')

@st.cache_data
def carregar_excel_historico(arquivo_excel:str):
    # Define formatos das colunas
    df_historico = pd.read_excel(arquivo_excel, sheet_name='Historico',thousands='.', decimal=',')
    df_historico['Data'] = pd.to_datetime(df_historico['Data'], format='%Y-%m-%d %H:%M:%S')    
    df_historico['MesAno'] = df_historico['Data'].dt.strftime('%Y/%m')
    df_historico['MesAno'] = df_historico['MesAno'].astype('string',errors='ignore')
    df_historico = df_historico.drop(columns=['OBS'])
    df_historico['Ticker'] = df_historico['Ticker'].astype('string',errors='ignore')
    df_historico['Posicao'] = df_historico['Posicao'].astype('string',errors='ignore')
    df_historico['TP Rendimento'] = df_historico['TP Rendimento'].astype('string',errors='ignore')
    df_historico['Num Nota'] = df_historico['Num Nota'].astype('string',errors='ignore')    
    df_historico['Tipo'] = df_historico['Tipo'].astype('string',errors='ignore')

    # Define formatos das colunas
    df_cadastro = pd.read_excel(arquivo_excel, sheet_name='Cadastro').reset_index()
    df_cadastro = df_cadastro.set_index('Ticker')
    df_cadastro.rename(columns={'SEGMENTO': 'Segmento','TIPO':'Tipo'}, inplace=True)    
    
    # Obtem a data de modificação do arquivo
    dt_historico = datetime.datetime.fromtimestamp(os.path.getmtime(arquivo_excel)).strftime('%d/%m/%Y %H:%M')
    
    return df_historico, dt_historico, df_cadastro

@st.cache_data
def carregar_indicacoes(arquivo_excel:str):
    # Define formatos das colunas
    df_indicacoes = pd.read_excel(arquivo_excel)
    df_indicacoes['Ticker'] = df_indicacoes['Ticker'].astype('string',errors='ignore')
    df_indicacoes['Vies'] = df_indicacoes['Vies'].astype('string',errors='ignore')
    
    # Obtem a data de modificação do arquivo
    dt_excel_indicacoes = datetime.datetime.fromtimestamp(os.path.getmtime(arquivo_excel)).strftime('%d/%m/%Y %H:%M')    
    return df_indicacoes, dt_excel_indicacoes

@st.cache_data
def carregar_csv_google(url:str):
    # Ler a planilha diretamente no pandas
    df_google = pd.read_csv(url)
    # Define formatos das colunas
    df_google['Ticker'] = df_google['Ticker'].str.replace('BVMF:', '')
    df_google['Tradetime'] = pd.to_datetime(df_google['Tradetime'],dayfirst=True)
    df_google['Ticker'] = df_google['Ticker'].astype('string',errors='ignore')    

    # Obtem a maior data de atualização da base
    dt_excel_google = df_google['Tradetime'].max()
    dt_excel_google = dt_excel_google.strftime('%d/%m/%Y %H:%M')
    return df_google, dt_excel_google

def limpa_cache():
    st.cache_data.clear()

def monta_df_carteira(df_historico:pd.DataFrame, df_indicacoes:pd.DataFrame, df_google:pd.DataFrame, df_cadastro:pd.DataFrame) -> pd.DataFrame:
    
    with st.sidebar.expander('Filtros',expanded=False):
        # Filtros - Posição ------------------------------------------------------------------------------------------------------------------------------------------------------
        param_Posicao = st.multiselect(label='Posição', options=['Ativo','Liquidado'],default='Ativo', placeholder='Escolha uma posição')
        if param_Posicao: df_historico = df_historico[df_historico['Posicao'].isin(param_Posicao)]
                
        # Filtros - MesAno -------------------------------------------------------------------------------------------------------------------------------------------------------
        lista_MesAno:list = df_historico['MesAno'].unique().tolist()
        lista_MesAno.sort(reverse=True)
        param_MesAno_Dividendos = st.multiselect(label='Mes Ano (Ult Dividendo)', options=lista_MesAno, default=lista_MesAno[0], placeholder='Escolha um tipo')
        if param_MesAno_Dividendos: df_dividendos_mes_escolhido = df_historico.loc[df_historico['MesAno'].isin(param_MesAno_Dividendos)]
        else: df_dividendos_mes_escolhido = df_historico.loc[df_historico['MesAno'].isin(lista_MesAno)]
       
        # Montagem Compras --------------------------------------------------------------------------------------------------------------------------------------------------------
        df_compras = df_historico.loc[df_historico['TP Rendimento'] == 'Compra']
        df_compras = df_compras.groupby('Ticker')[['Quantidade','Valor']].sum().reset_index()
        df_compras = df_compras.loc[df_compras['Quantidade'] > 0]
        df_compras.rename(columns={'Ticker': 'Ticker','Quantidade':'Qtd','Valor':'Valor Aquisição'}, inplace=True)
        df_compras['Valor Aquisição'] = df_compras['Valor Aquisição'] * -1
        
        df_dividendos = df_historico.loc[df_historico['TP Rendimento'] == 'Dividendos']
        df_dividendos = df_dividendos.groupby('Ticker')['Valor'].sum().reset_index()
        df_dividendos.rename(columns={'Ticker': 'Ticker','Valor':'Dividendos'}, inplace=True)    
        
        df_dividendos_mes_escolhido = df_dividendos_mes_escolhido.loc[df_historico['TP Rendimento'] == 'Dividendos']
        df_dividendos_mes_escolhido = df_dividendos_mes_escolhido.groupby('Ticker')['Valor'].sum().reset_index()
        df_dividendos_mes_escolhido.rename(columns={'Ticker': 'Ticker','Valor':'Ult Divid'}, inplace=True)    

        df_carteira = pd.merge(df_compras, df_google, on='Ticker', how='left')
        df_carteira['Ticker'] = df_carteira['Ticker'].astype('string')
        df_carteira = pd.merge(df_carteira, df_dividendos, on='Ticker', how='left')
        df_carteira = pd.merge(df_carteira, df_dividendos_mes_escolhido, on='Ticker', how='left')    
        df_carteira = pd.merge(df_carteira, df_indicacoes, on='Ticker', how='left')
        df_carteira = pd.merge(df_carteira, df_cadastro, on='Ticker', how='left')
        
        df_carteira.loc[df_carteira['Segmento'].isnull(),'Segmento'] = 'Vazio'
        df_carteira.loc[df_carteira['Tipo'].isnull(),'Tipo'] = 'Vazio'
        df_carteira.loc[df_carteira['Dividendos'].isnull(),'Dividendos'] = 0
        df_carteira.loc[df_carteira['Ult Divid'].isnull(),'Ult Divid'] = 0

        df_carteira['Valor Mercado'] = df_carteira['Qtd'] * df_carteira['Price']
        df_carteira['Delta Mercado/Aquis.'] = df_carteira['Valor Mercado'] - df_carteira['Valor Aquisição']
        
        df_carteira['Delta Merc/Aq'] = (df_carteira['Valor Mercado'] / df_carteira['Valor Aquisição']) * 100
        df_carteira['Merc_menos_(Div_mais_Aquis)'] = df_carteira['Valor Mercado'] - (df_carteira['Valor Aquisição']-df_carteira['Dividendos'])
        df_carteira['Rentab'] =(((df_carteira['Valor Mercado'] + df_carteira['Dividendos']) - df_carteira['Valor Aquisição']) /df_carteira['Valor Aquisição'])*100

        df_carteira['YOC'] = (df_carteira['Dividendos'] / df_carteira['Valor Aquisição'])*100
        df_carteira['DY'] = (df_carteira['Ult Divid'] / df_carteira['Valor Aquisição'])*100

        # Calculando o percentual de participação para cada linha    
        valor_total_aquisicao = df_carteira['Valor Aquisição'].sum()
        df_carteira['%'] = (df_carteira['Valor Aquisição'] / valor_total_aquisicao) * 100

        # Convertendo null para Vazio
        df_carteira.loc[df_carteira['Vies'].isnull(),'Vies'] = 'Vazio'
        
        # Concatenando a nova linha de total
        df_carteira_total = pd.concat([df_carteira, pd.DataFrame({'Ticker': ['Total'], 'Todos': [''], 'Tipo': [''], 'Segmento':[''], 'Vies':[''] })], ignore_index=True)
        df_numeric = df_carteira_total.select_dtypes(include=['int64', 'float64']) 
        df_sum = df_numeric.sum() 
        df_carteira_total.loc[df_carteira_total['Ticker'] == 'Total', df_numeric.columns] = df_sum.values
        df_carteira_total = df_carteira_total[df_carteira_total['Ticker'] == 'Total']

        df_carteira_total['YOC'] = (df_carteira_total['Dividendos'] / df_carteira_total['Valor Aquisição'])*100
        df_carteira_total['DY'] = (df_carteira_total['Ult Divid'] / df_carteira_total['Valor Aquisição'])*100
        df_carteira_total['Delta Merc/Aq'] = (df_carteira_total['Valor Mercado'] / df_carteira_total['Valor Aquisição']) * 100
        df_carteira_total['Merc_menos_(Div_mais_Aquis)'] = df_carteira_total['Valor Mercado'] - (df_carteira_total['Valor Aquisição']-df_carteira_total['Dividendos'])
        df_carteira_total['Rentab'] =(((df_carteira_total['Valor Mercado'] + df_carteira_total['Dividendos']) - df_carteira_total['Valor Aquisição']) /df_carteira_total['Valor Aquisição'])*100

    return df_carteira, df_carteira_total

def monta_aba_carteira(df_carteira: pd.DataFrame, df_carteira_total: pd.DataFrame) -> None:
    cellstyle_percentual = JsCode("""function(params){
        if (params.value <= '85') {return{'color': '#9C0006','backgroundColor': '#FFC7CE',}}
        if ((params.value > '85') && (params.value < '100')){return {'color': '#9C5700','backgroundColor': '#FFEB9C',}}        
        if (params.value >= '100') {return{'color': '#006100','backgroundColor': '#C6EFCE',}}}""")
    cellstyle_absoluto = JsCode("""function(params){
        if (params.value <= '0') {return{'color': '#9C0006','backgroundColor': '#FFC7CE',}}
        if ((params.value > '0') && (params.value < '2')){return {'color': '#9C5700','backgroundColor': '#FFEB9C',}}        
        if (params.value >= '2') {return{'color': '#006100','backgroundColor': '#C6EFCE',}}}""")
    gb_options = GridOptionsBuilder()
    gb_options.configure_default_column(filterParams={'applyMiniFilterWhileTyping': 'true'},sortable=True, filter='agNumberColumnFilter')
    gb_options.configure_side_bar(defaultToolPanel='')
    gb_options.configure_grid_options(pinnedTopRowData=[df_carteira_total[["Ticker","Qtd","Valor Aquisição","Dividendos","Ult Divid","DY","Valor Mercado","Delta Mercado/Aquis.","Delta Merc/Aq","Merc_menos_(Div_mais_Aquis)","Rentab","YOC","%"]].to_dict("records")[0]])
    gb_options.configure_column(field="Ticker",header_name="Ticker",filter='agSetColumnFilter', initialPinned='left',width=85)
    gb_options.configure_column(field="Qtd",header_name="Qtd",type=["numericColumn"],width=80)
    gb_options.configure_column(field="Rentab",header_name="Rentab",cellStyle=cellstyle_absoluto,type=['numericColumn'],valueFormatter="x.toFixed(2) + '%'",width=100,initialSort='desc')
    gb_options.configure_column(field='Merc_menos_(Div_mais_Aquis)',header_name='Merc-(Div+Aquis)',type=["numericColumn"],valueFormatter="x.toLocaleString('pt-BR',{style: 'currency', currency: 'BRL'})",width=130)
    gb_options.configure_column(field="Valor Aquisição",header_name="Valor Aquisição",type=["numericColumn"],valueFormatter="x.toLocaleString('pt-BR',{style: 'currency', currency: 'BRL'})",width=130)
    gb_options.configure_column(field="Valor Mercado",header_name="Valor Mercado",type=["numericColumn"],valueFormatter="x.toLocaleString('pt-BR',{style: 'currency', currency: 'BRL'})",width=130)
    gb_options.configure_column(field='Delta Merc/Aq',header_name='∆ Merc/Aquis.',cellStyle=cellstyle_percentual,type=["numericColumn"],valueFormatter="x.toLocaleString('pt-BR',{style: 'currency', currency: 'BRL'})",width=100)
    gb_options.configure_column(field="Dividendos",header_name="Dividendos",type=["numericColumn"],valueFormatter="x.toLocaleString('pt-BR',{style: 'currency', currency: 'BRL'})",width=120)
    gb_options.configure_column(field="Ult Divid",header_name="Ult Divid",type=["numericColumn"],valueFormatter="x.toLocaleString('pt-BR',{style: 'currency', currency: 'BRL'})",width=100)
    gb_options.configure_column(field="YOC",header_name="YOC",type=["numericColumn"],valueFormatter="x.toFixed(2) + '%'",width=90)
    gb_options.configure_column(field="Vies",header_name="Vies",type=["stringColumn"],width=80,filter='agSetColumnFilter')
    gb_options.configure_column(field="DY",header_name="DY",type=["numericColumn"],valueFormatter="x.toFixed(2) + '%'",width=90)
    gb_options.configure_column(field="%",header_name="%",type=["numericColumn"],valueFormatter="x.toFixed(2) + '%'",width=90)
    gb_options.configure_column(field="Delta Merc/Aq",header_name="∆ Merc/Aq",type=["numericColumn"],valueFormatter="x.toFixed(2) + '%'",width=100)
    gb_options.configure_column(field="Tipo",header_name="Tipo",type=["stringColumn"],filter='agSetColumnFilter', width=100)
    gb_options.configure_column(field="Segmento",header_name="Segmento",type=["stringColumn"],filter='agSetColumnFilter', width=100)    
    gb_options = gb_options.build()
    AgGrid(df_carteira,gb_options,height=((df_carteira.shape[0]+3)*30), allow_unsafe_jscode=True, key='grid_carteira')

def monta_aba_dividendos_compras_mensais(df_historico: pd.DataFrame, TP_Rendimento: str = 'Dividendos') -> None:
    ''' TP_Rendimento: "Dividendos" ou "Compra" '''
    aba_barra, aba_linha, aba_tabela  = st.tabs(['Barra','Linha','Tabela'])
    
    if TP_Rendimento == 'Compra': df_historico['Valor'] = df_historico['Valor'] * -1
    
    # Gráfico de barras e linhas
    df_mensal = df_historico.loc[df_historico['TP Rendimento'] == TP_Rendimento]
    df_mensal = df_mensal.groupby(['MesAno'])['Valor'].sum()#.reset_index()#.set_index('MesAno')    
    aba_barra.write(px.bar(df_mensal, y='Valor', x=df_mensal.index, text_auto='.2s', labels={'Valor':'Valor em Reais'}))
    aba_linha.write(px.line(df_mensal, y='Valor', x=df_mensal.index, labels={'Valor':'Valor em Reais'}))

    # Tabela agrupada por Mês e Ano
    df_mensal = df_historico
    df_mensal = df_mensal.loc[df_mensal['TP Rendimento'] == TP_Rendimento]
    df_mensal = df_mensal[['Ticker','MesAno','Valor','Posicao']]    
    gb_options = GridOptionsBuilder()
    gb_options.configure_grid_options(pivotMode=True)
    gb_options.configure_side_bar(defaultToolPanel='')
    gb_options.configure_column(field="Posicao",header_name="Posição",filter='agSetColumnFilter', type=["stringColumn"],width=100, rowGroup=True, enableRowGroup=True, enableValue=False)
    gb_options.configure_column(field="Ticker",header_name="Ticker",filter='agSetColumnFilter', type=["stringColumn"],width=100, rowGroup=True, enableRowGroup=True, enableValue=False)
    gb_options.configure_column(field="MesAno",header_name="Mês Ano",width=100, type=["numericColumn"], enablePivot=True, pivot=True)
    gb_options.configure_column(field="Valor",header_name="Valor",width=100, type=["numericColumn"], aggFunc='sum', enableValue=True,valueFormatter="x.toLocaleString('pt-BR',{style: 'currency', currency: 'BRL'})")    
    gb_options = gb_options.build()
    with aba_tabela:
        AgGrid(df_mensal,gb_options,allow_unsafe_jscode=True, key='grid_'+TP_Rendimento)

def monta_indicadores(df_carteira:pd.DataFrame, qtd_ativos: int) -> None:
    # Cria bloco com 7 indicadores
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric('Aquisição', value=numerize(df_carteira['Valor Aquisição'].sum()), help=converter_numero_moeda(df_carteira['Valor Aquisição'].sum(),'Total Aquisição: '), delta='{:.2f}% Rentab'.format(df_carteira['Rentab'].sum()))
    col2.metric('Mercado', value=numerize(df_carteira['Valor Mercado'].sum()), help=converter_numero_moeda(df_carteira['Valor Mercado'].sum(),'Total Mercado: '), delta='{:.2f}% Aq/Merc'.format(taxa_aumento(df_carteira['Valor Aquisição'].sum(),df_carteira['Valor Mercado'].sum())))     
    col3.metric('Dividendos', value=numerize(df_carteira['Dividendos'].sum()), help=converter_numero_moeda(df_carteira['Dividendos'].sum(), 'Total Dividendos: '), delta='{:.2f}% YOC'.format(df_carteira['YOC'].sum()))
    col4.metric('Ult Dividendo', value=numerize(df_carteira['Ult Divid'].sum()), help=converter_numero_moeda(df_carteira['Ult Divid'].sum(),'Total Ult Divid: '), delta='{:.2f}% DY'.format(df_carteira['DY'].sum()))
    col5.metric('Ativos', qtd_ativos)
    #col6.metric('YOC', '{:.2f}%'.format((df_cateira['Dividendos'].sum() / df_cateira['Valor Aquisição'].sum()) * 100))
    #col7.metric('DYY Ult Mês', '{:.2f}%'.format((df_cateira['Ult Divid'].sum() / df_cateira['Valor Aquisição'].sum()) * 100))

def taxa_aumento(primeira_parcela:float, segunda_parcela: float) -> float:
    taxa = ((segunda_parcela - primeira_parcela) / primeira_parcela ) * 100
    return taxa

def converter_numero_moeda(numero:float, frase:str=''):   
    string = f'{frase}{locale.currency(numero,grouping=True)}'
    return string 

def monta_aba_IRPF(df_historico:pd.DataFrame):
    param_Ano_IRPF = st.slider('Ano Calendário', datetime.datetime.now().year, 2018, help='Selecion o ano calendário que deseja montar o imposto de renda.')

    df_compras_vendas_ano_atual = df_historico[(df_historico['TP Rendimento'].isin(['Compra','Venda'])) & (df_historico['Data'] <= ('31/12/' + str(param_Ano_IRPF)))]
    df_compras_vendas_ano_atual.loc[df_compras_vendas_ano_atual['TP Rendimento'] == 'Venda', 'Valor'] = 0
    df_compras_vendas_ano_atual = df_compras_vendas_ano_atual.groupby('Ticker')[['Quantidade','Valor']].sum()
    df_compras_vendas_ano_atual['Valor'] = df_compras_vendas_ano_atual['Valor'] * -1
    df_compras_vendas_ano_atual.loc[df_compras_vendas_ano_atual['Quantidade'] == 0, 'Valor'] = 0
    df_compras_vendas_ano_atual.rename(columns={'Quantidade':'Qtd '+str(param_Ano_IRPF),'Valor':'Valor '+str(param_Ano_IRPF)}, inplace=True)
    
    df_compras_vendas_ano_anteiror = df_historico[(df_historico['TP Rendimento'].isin(['Compra','Venda'])) & (df_historico['Data'] <= ('31/12/' + str(param_Ano_IRPF-1)))]
    df_compras_vendas_ano_anteiror.loc[df_compras_vendas_ano_anteiror['TP Rendimento'] == 'Venda', 'Valor'] = 0
    df_compras_vendas_ano_anteiror = df_compras_vendas_ano_anteiror.groupby('Ticker')[['Quantidade','Valor']].sum()
    df_compras_vendas_ano_anteiror['Valor'] = df_compras_vendas_ano_anteiror['Valor'] * -1
    df_compras_vendas_ano_anteiror.loc[df_compras_vendas_ano_anteiror['Quantidade'] == 0, 'Valor'] = 0
    df_compras_vendas_ano_anteiror.rename(columns={'Quantidade':'Qtd '+str(param_Ano_IRPF-1),'Valor':'Valor '+str(param_Ano_IRPF-1)}, inplace=True)
    
    df_dividendos_ano_atual = df_historico[(df_historico['TP Rendimento'].isin(['Dividendos'])) & (df_historico['Data'].dt.year == param_Ano_IRPF)]
    df_dividendos_ano_atual.loc[df_dividendos_ano_atual['TP Rendimento'] == 'Venda', 'Valor'] = 0
    df_dividendos_ano_atual = df_dividendos_ano_atual.groupby('Ticker')[['Valor']].sum()
    df_dividendos_ano_atual.rename(columns={'Valor':'Dividendos '+str(param_Ano_IRPF)}, inplace=True)

    df_anos_unificados = pd.merge(df_compras_vendas_ano_anteiror,df_compras_vendas_ano_atual, on='Ticker', how='outer')
    df_anos_unificados = pd.merge(df_anos_unificados,df_dividendos_ano_atual, on='Ticker', how='left')  
    df_anos_unificados = df_anos_unificados[(df_anos_unificados.iloc[:, 0] > 0) | (df_anos_unificados.iloc[:, 2] > 0)]    
    df_anos_unificados = cache_df_anos_unificados(df_anos_unificados)

    coluna1, coluna2 = st.columns(2)
    evento = coluna1.dataframe(df_anos_unificados,on_select="rerun",selection_mode=["single-row"],
                               column_config={'Valor '+str(param_Ano_IRPF-1): st.column_config.NumberColumn('Valor '+str(param_Ano_IRPF-1),help='Valor em Reais',format='R$ %.2f'),
                                              'Valor '+str(param_Ano_IRPF): st.column_config.NumberColumn('Valor '+str(param_Ano_IRPF),help='Valor em Reais',format='R$ %.2f'),
                                              'Dividendos '+str(param_Ano_IRPF): st.column_config.NumberColumn('Dividendos '+str(param_Ano_IRPF),help='Valor em Reais',format='R$ %.2f'),
                                              'Data': st.column_config.DateColumn('Data',format='DD/MM/YYYY'),
                                              })
    if len(evento.selection.rows) > 0: # type: ignore
        df_historico_selecionado = df_historico[(df_historico['TP Rendimento'].isin(['Compra','Venda'])) & (df_historico['Ticker'] == df_anos_unificados.index[evento.selection.rows[0]]) & (df_historico['Data'] <= ('31/12/' + str(param_Ano_IRPF)))]  # type: ignore
        df_historico_selecionado = df_historico_selecionado.set_index('Ticker')
        coluna2.dataframe(df_historico_selecionado,column_order=['Ticker','Data','Quantidade','Valor','TP Rendimento','Num Nota'],column_config={'Valor': st.column_config.NumberColumn('Valor',help='Valor em Reais',format='R$ %.2f'),'Data': st.column_config.DateColumn('Data',format='DD/MM/YYYY')})

def monta_aba_juros_compostos(df_cateira: pd.DataFrame):
    col1, col2 = st.columns([0.2,0.8])
    param_pagamento = col1.slider('Valor mensal', min_value=-20000, max_value=20000, step=1000, value=int(config['Aba_Juros_Compostos']['param_pagamento']), help='Selecione o valor mensal')
    param_saldo_carteira: float = float(col1.text_input(label='Valor em carteira', value=df_cateira['Valor Mercado'].sum(),max_chars=11)) # type: ignore
    param_juros: float = float(col1.text_input(label='Juros mensais', value='{:.2f}'.format((df_cateira['Ult Divid'].sum() / df_cateira['Valor Aquisição'].sum()) * 100),max_chars=11))
    param_meta_tipo = col1.radio(label='Meta', options=['Valor','Dividendos'], index=1)
    param_meta_valor: float = float(col1.text_input(label='Valor da Meta me R$', value=config['Aba_Juros_Compostos']['param_meta_valor'],max_chars=11))

    dados = []
    juros = 0
    #saldo_sem_juros = 0
   
    for count in range(1200):
        dados.append([param_saldo_carteira, juros])
        juros = param_saldo_carteira * (param_juros / 100)
        param_saldo_carteira += juros + param_pagamento
        if param_saldo_carteira < 1 : break
        if param_meta_tipo == 'Valor'and param_saldo_carteira > param_meta_valor: break
        if param_meta_tipo == 'Dividendos'and juros > param_meta_valor: break

    col2.markdown(mes_para_ano(count))
    # Criar o DataFrame
    df = pd.DataFrame(dados, columns=['Saldo Carteira', 'Juros'])
    df= df.sort_index(ascending=False)
    col2.dataframe(df,column_config={'Saldo Carteira': st.column_config.NumberColumn('Saldo Carteira',help='Valor em Reais',format='R$ %.2f'),
                                                                                     'Juros': st.column_config.NumberColumn('Juros Mensais',help='Valor em Reais',format='R$ %.2f')})

def mes_para_ano(meses: int):
    anos = int(meses/12)
    if anos == 1: plural_anos = 'ano'
    else: plural_anos = 'anos'

    meses = meses - (anos * 12)
    if meses == 1: plural_meses = 'mês' 
    else: plural_meses = 'meses'

    if anos == 0:
        anos = ''
        plural_anos = ''
        preposicao = ''
    else:
        preposicao = 'e'
    
    frase = f'Tempo até a meta: {anos} {plural_anos} {preposicao} {meses} {plural_meses}'

    return frase

@st.cache_data
def cache_df_anos_unificados(df_anos_unificados: pd.DataFrame):
    return df_anos_unificados

def monta_aba_dataframe(df: pd.DataFrame) -> None:    
    grid_options = GridOptionsBuilder.from_dataframe(df)
    grid_options.configure_default_column(filterParams={'applyMiniFilterWhileTyping': 'true'}, filter=True, sortable=True,flex=1)
    grid_options.configure_side_bar(defaultToolPanel='')
    AgGrid(data=df,gridOptions=grid_options.build(),fit_columns_on_grid_load=True)

def monta_principal():
    df_historico, dt_excel_historico, df_cadastro = carregar_excel_historico(arquivo_excel=config['Aba_Historico']['arquivo_excel'])
    df_indicacao, dt_excel_indicacao = carregar_indicacoes(arquivo_excel=config['Aba_Indicacoes']['arquivo_excel'])
    df_google, dt_excel_google = carregar_csv_google(url=config['Aba_Google']['url'])

    df_carteira, df_carteira_total = monta_df_carteira(df_google=df_google, df_historico=df_historico,df_indicacoes=df_indicacao,df_cadastro=df_cadastro)
    monta_indicadores(df_carteira_total,  df_carteira.shape[0])

    # Cria as abas do painel
    aba_carteira, aba_historico, aba_google, aba_indicacoes, aba_dividendos, aba_compras, aba_IRPF, aba_setorial, aba_juros_compostos = st.tabs(['Carteira', 'Historico', 'Google', 'Indicações','Dividendos', 'Compras', 'IRPF', 'Setorial', 'Juros Compostos'])

    with aba_google:
        monta_aba_dataframe(df_google)
    with aba_indicacoes:
        monta_aba_dataframe(df_indicacao)
    with aba_historico:
        monta_aba_dataframe(df_historico)
    with aba_dividendos:
        monta_aba_dividendos_compras_mensais(df_historico,TP_Rendimento='Dividendos')
    with aba_compras:
        monta_aba_dividendos_compras_mensais(df_historico,TP_Rendimento='Compra')
    with aba_IRPF:        
        monta_aba_IRPF(df_historico)
    with aba_setorial:
        agrupamentos_multi = st.multiselect('Agrupamentos', ['Tipo','Segmento','Ticker','Vies'], default=['Tipo','Segmento','Ticker']
                                      , help='Escolha os agrupamentos que deseja visualizar no gráfico de treemap.')
        #st.write(agrupamentos_multi)
        agrupamentos_multi.insert(0,px.Constant("Todos"))
        st.plotly_chart(px.treemap(df_carteira, path=agrupamentos_multi, values='Valor Mercado'))
    with aba_carteira:        
        monta_aba_carteira(df_carteira=df_carteira, df_carteira_total=df_carteira_total)
    with aba_juros_compostos:
        monta_aba_juros_compostos(df_carteira)

    st.sidebar.button('Limpar Cache',on_click=limpa_cache)
    st.sidebar.subheader("Atualizações", divider="red", anchor=False)
    st.sidebar.info(body='Google: '+dt_excel_google)
    st.sidebar.info(body='Indicações: '+dt_excel_indicacao)
    st.sidebar.info(body='Excel: '+dt_excel_historico)

if __name__ == '__main__':
    monta_principal()