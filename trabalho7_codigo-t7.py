'''
Objetivos Específicos:
    Utilizar as bibliotecas BeautifulSoup, Requests e Selenium para raspagem de dados.
    Manipular e analisar dados utilizando a biblioteca pandas.
    Criar visualizações informativas com a biblioteca matplotlib.
    Desenvolver um aplicativo interativo com a biblioteca Streamlit que apresente os dados de forma clara e envolvente.
    Exportar informações em PDF, utilizando a biblioteca pdfkit.
    Aplicar técnicas de storytelling para tornar a apresentação dos dados mais impactante.
    Publicar o arquivo em um repositório do GitHub e fazer o deploy na Streamlit Cloud. 
'''
import io
import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import pdfkit

def get_data(url, cabecalho):
    requisicao = requests.get(url=url, headers=cabecalho, verify=False)
    site = BeautifulSoup(requisicao.text, 'html.parser')
    table = site.find_all('div', class_='col-xl-8 col-lg-8')
    salario_now = []
    salario_old = []
    moeda = []
    nome = []
    periodo = []
    
    if table:
        for div in table:
            links = div.find_all('a')
            new_val = div.find_all('tr')
            
            for link in links:
                nome.append(link.text.strip())
            for tr in new_val:
                tds = tr.find_all('td')
                if len(tds) > 1:
                    salario_old.append(tds[1].text.strip())
                if len(tds) > 2:
                    salario_now.append(tds[2].text.strip())
                if len(tds) > 4:
                    moeda.append(tds[4].text.strip())
                if len(tds) > 3:
                    periodo.append(tds[3].text.strip())

    dados = {
        'País': nome,
        'Salário Antigo': salario_old,
        'Salário Atual': salario_now,
        'Moeda': moeda,
        'Período': periodo
    }
    return pd.DataFrame(dados)

def clean_data(df):
    df['Salário Antigo'] = df['Salário Antigo'].str.replace(',', '').astype(float)
    df['Salário Atual'] = df['Salário Atual'].str.replace(',', '').astype(float)
    return df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

def create_general_chart(df):
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.bar(df['País'], df['Salário Antigo'], label='Salário Antigo', color='skyblue')
    ax.bar(df['País'], df['Salário Atual'], bottom=df['Salário Antigo'], label='Salário Atual', color='orange')
    ax.set_ylabel('Salário')
    ax.set_title('Comparação de Salários Antigo e Atual por País')
    ax.legend()
    ax.tick_params(axis='x', rotation=60)
    ax.grid(axis='y')
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.2)
    return fig

def create_country_chart(df, pais):
    fig, ax = plt.subplots(figsize=(10, 6))
    df_pais = df[df['País'] == pais]
    ax.bar(['Salário Antigo', 'Salário Atual'], [df_pais['Salário Antigo'].values[0], df_pais['Salário Atual'].values[0]], color=['skyblue', 'orange'])
    ax.set_ylabel(f'Salário ({df_pais["Moeda"].values[0]})')
    ax.set_title(f'Comparação de Salários Antigo e Atual - {pais}')
    ax.grid(axis='y')
    return fig

def export_to_csv(df):
    csv_data = df.to_csv(index=False)
    st.markdown("### Download arquivo em CSV (Excel)")
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name="salarios.csv",
        mime="text/csv"
    )

def export_graph(fig, pais):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    st.markdown(f"### Download Gráfico - {pais}")
    st.download_button(
        label=f"Download Gráfico PNG - {pais}",
        data=buf,
        file_name=f"grafico_{pais}.png",
        mime="image/png"
    )

def export_to_pdf(df):
    st.markdown("### Download Tabela em PDF")
    html = df.to_html(index=False)
    pdf_data = pdfkit.from_string(html, False)
    st.download_button(
        label="Download PDF",
        data=pdf_data,
        file_name="salarios.pdf",
        mime="application/pdf"
    )

def main():
    url = 'https://pt.tradingeconomics.com/country-list/minimum-wages?continent=europe'
    cabecalho = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    df = get_data(url, cabecalho)
    df = clean_data(df)
    
    st.title('Exemplo de Gráficos de Barras por País com Streamlit e Matplotlib')
    
    # Gráfico Geral
    st.header('Gráfico Geral de Comparação de Salários')
    fig_general = create_general_chart(df)
    st.pyplot(fig_general)
    
    # Exportar Gráfico Geral
    export_graph(fig_general, 'geral')
    
    # Barra de Pesquisa
    st.header('Pesquisar por País')
    pais = st.text_input('Digite o nome do país')
    
    if pais:
        if pais in df['País'].values:
            fig_pais = create_country_chart(df, pais)
            st.pyplot(fig_pais)
            export_graph(fig_pais, pais)
        else:
            st.write('País não encontrado.')
    
    st.write("Dados:")
    st.write(df)
    export_to_csv(df)
    

main()
