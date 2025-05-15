import streamlit as st
import pandas as pd
import plotly.express as px

#'C:/Users/Victor/Desktop/PEGA/python/visualizacoes2/dados_sus_processados.csv'

dados_sus = pd.read_csv(
    'dados_sus_processados.csv',
    sep = ","
)

#print(dados_sus.columns.tolist())

# ----------- PÁGINA PRINCIPAL -----------
st.set_page_config(layout="wide")

# TÍTULO E INTRODUÇÃO
st.title("Análise das Internações do SUS de 2024")
st.markdown("""
Análise das características das incidências 
das doenças nas internações utilizando a 
base de dados SIH do SUS de 2024 para pacientes com residência em cidades no Rio Grande do S
""")

st.markdown("---")
# ----------- GRÁFICO 1 - TOP 10 por valor_total -----------
st.subheader("Doenças que geraram maior investimento dos cofres públicos")

# Seleciona os 10 diagnósticos com maior valor total
top10_valor = dados_sus.sort_values(by='valor_total', ascending=False).head(10)

# Cria uma coluna de categoria para cores harmoniosas
top10_valor['Categoria'] = top10_valor['sexo_majoritario']

# Criação do gráfico de barras empilhadas com cores harmoniosas
fig_bar = px.bar(
    top10_valor,
    x='DIAG_PRINC',  # Eixo X: Diagnóstico
    y='valor_total',  # Eixo Y: Valor Total
    color='Categoria',  # Cores por categoria
    hover_data=['descricao_cid'],  # Exibe a descrição do CID ao passar o mouse
    labels={'valor_total': 'Valor Total (R$)', 'DIAG_PRINC': 'Diagnóstico'},
    title="Doenças que geraram maior investimento dos cofres públicos",
    color_discrete_map={
        'Masculino': '#1f77b4',  # Azul para masculino
        'Feminino': '#ff7f0e',  # Laranja para feminino
        'Ignorado': '#2ca02c'  # Verde para ignorado
    }
)

# Exibindo o gráfico
st.plotly_chart(fig_bar, use_container_width=True)



st.markdown("---")
# ----------- GRÁFICO 2 - Distribuição por sexo -----------
st.subheader("Distribuição de Diagnósticos por Sexo")
st.markdown("""
Selecionado as 5 doenças que mais estão associados a cada gênero
""")

# Seleciona os top 5 diagnósticos por sexo incluindo descricao_cid
top_mulher = dados_sus.nlargest(5, 'total_feminino')[['DIAG_PRINC', 'total_feminino', 'descricao_cid']]
top_homem = dados_sus.nlargest(5, 'total_masculino')[['DIAG_PRINC', 'total_masculino', 'descricao_cid']]

# Renomeia para facilitar concatenação
top_mulher = top_mulher.rename(columns={
    'total_feminino': 'total',
    'DIAG_PRINC': 'Diagnóstico',
    'descricao_cid': 'Nome da doença'
})
top_mulher['Sexo'] = 'Feminino'

top_homem = top_homem.rename(columns={
    'total_masculino': 'total',
    'DIAG_PRINC': 'Diagnóstico',
    'descricao_cid': 'Nome da doença'
})
top_homem['Sexo'] = 'Masculino'

# Junta os dados
dados_top = pd.concat([top_mulher, top_homem], ignore_index=True)

# Cria o gráfico com hover_data personalizado
fig2 = px.bar(
    dados_top,
    x='total',
    y='Diagnóstico',
    color='Sexo',
    orientation='h',
    hover_data={'Nome da doença': True, 'Sexo': False},  # Mostra nome da doença, oculta sexo (opcional)
    labels={'total': 'Total de Pacientes'},
    #title='Diagnósticos mais frequentes para cada sexo'
)

st.plotly_chart(fig2, use_container_width=True)


st.markdown("---")
# ----------- GRÁFICO 3 - Diagnósticos por faixa etária -----------
st.subheader("Diagnósticos mais frequentes por faixa etária com base na idade média")

# Define função para classificar a faixa etária
def faixa_etaria(idade):
    if idade <= 12:
        return 'Criança'
    elif idade <= 24:
        return 'Jovem'
    elif idade <= 59:
        return 'Adulto'
    else:
        return 'Idoso'

# Aplica classificação no DataFrame
dados_sus['Faixa Etária'] = dados_sus['idade_media'].apply(faixa_etaria)

# Agrupa e seleciona os top 5 por faixa etária com base em total de pacientes
# Vamos supor que há uma coluna 'total' com o número de pacientes por linha
# Se não houver, substitua por outra métrica de volume, como 'valor_total' ou similar

top_faixas = []

for faixa in ['Criança', 'Jovem', 'Adulto', 'Idoso']:
    top = (
        dados_sus[dados_sus['Faixa Etária'] == faixa]
        .nlargest(5, 'TOTAL_OCORRENCIAS')[['DIAG_PRINC', 'descricao_cid', 'TOTAL_OCORRENCIAS']]
        .copy()
    )
    top.rename(columns={
        'DIAG_PRINC': 'Diagnóstico',
        'descricao_cid': 'Nome da doença'
    }, inplace=True)
    top['Faixa Etária'] = faixa
    top_faixas.append(top)

# Junta tudo
dados_top_faixa = pd.concat(top_faixas, ignore_index=True)

fig_facet = px.bar(
    dados_top_faixa,
    x='TOTAL_OCORRENCIAS',
    y='Diagnóstico',
    color='Faixa Etária',
    facet_col='Faixa Etária',
    facet_col_wrap=2,
    orientation='h',
    hover_data={'Nome da doença': True},
    labels={'TOTAL_OCORRENCIAS': 'Total de Pacientes'},
    title='Top 5 Diagnósticos mais Frequentes por Faixa Etária'
)

fig_treemap_idade = px.treemap(
    dados_top_faixa,
    path=['Faixa Etária', 'Nome da doença'],
    values='TOTAL_OCORRENCIAS',
    color='Faixa Etária',
    hover_data={'TOTAL_OCORRENCIAS': True},
    labels={'TOTAL_OCORRENCIAS': 'Total de Pacientes'},
    title='Distribuição dos Diagnósticos mais Frequentes por Faixa Etária'
)

st.plotly_chart(fig_treemap_idade, use_container_width=True)


st.markdown("---")
# ----------- MÓDULO: Consulta por Diagnóstico (CID) -----------

st.subheader("Consulta Detalhada por Diagnóstico (CID)")
st.markdown("""
Selecione um CID e veja dados sobre sua incidência no RS em 2024
""")

# Cria uma lista ordenada de CIDs disponíveis para seleção
cid_opcoes = dados_sus['DIAG_PRINC'].unique()
cid_selecionado = st.selectbox("Selecione um diagnóstico (CID):", sorted(cid_opcoes))

# Filtra os dados com base na seleção
dados_cid = dados_sus[dados_sus['DIAG_PRINC'] == cid_selecionado]

# Exibe os dados apenas se houver correspondência
if not dados_cid.empty:
    linha = dados_cid.iloc[0]  # Assume que cada CID é único
    st.markdown(f"### Informações para o CID `{cid_selecionado}`")
    st.markdown(f"- **Nome da Doença:** {linha['descricao_cid']}")
    st.markdown(f"- **Total de Ocorrências:** {int(linha['TOTAL_OCORRENCIAS'])}")
    st.markdown(f"- **Valor Total das Internações:** R$ {linha['valor_total']:,.2f}")
    st.markdown(f"- **Incidência em Mulheres:** {int(linha['total_feminino'])}")
    st.markdown(f"- **Incidência em Homens:** {int(linha['total_masculino'])}")
    st.markdown(f"- **Incidência Ignorada:** {int(linha['total_ignorado'])}")
else:
    st.warning("Nenhum dado encontrado para o CID selecionado.")


st.markdown("---")
# ----------- AMOSTRA E DOWNLOAD DOS DADOS -----------
st.subheader("Amostra dos Dados e Download")

st.dataframe(dados_sus.head(20))

# Botão para download do dataset
csv = dados_sus.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Baixar dados como CSV",
    data=csv,
    file_name='dados_sus_2024.csv',
    mime='text/csv'
)
