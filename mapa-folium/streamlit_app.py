import pandas as pd
import folium
import streamlit as st
from streamlit_folium import folium_static
import re

# configurando o app
st.set_page_config(layout='wide')
st.title('WOs a serem executadas')
col1, col2, col3 = st.beta_columns([2, 3, 2])

# inserindo a senha
with col1:
    senha = st.text_input('Insira a palavra passe abaixo:')
if senha == 'maparollout':
    # criando df para novos sites
    old_site = ['RCE-IBA01-NKI01CO',
                'FLA-CEN01-NKI01CO',
                'MWE-RJ-RJCG11-T1-HW x RJO-RJCG11-THWP01',
                'AIR-ETC01-NKI01CO',
                'AJO-ETO01-NKI01AG',
                'MCO-JCT01-NKI01CO',
                'RCE-IBA01',
                'RGO-FER01',
                'MWE-BA-CASA05-N1',
                'MCO-JCT01',
                'RCE-JFE01',
                'MWE-BA-NLSAIG30-Y8056-SI',
                'MWE-BA-NLCASA37-Y8994-SI',
                'BALFS_0051',
                'MWE-AL-RGRG00-N1-ER',
                'MWE-AL-RGRG00-N1-NO',
                'MWE-SE-CNAR01-T1-NO',
                'MWE-SE-NGAR01-N1-SI',
                'MWE-BA-CRVMW01-Y40703-SI',
                'MWE-BA-BA1320-N1-SI',
                'MWE-RJ-ARMA03-T3-HW x MWE-RJ-ARMA03-N1-HW',
                'DQCX76',
                'MWE-RJ-ANGR01-N1-NO x MWE-RJ-ANGR01-T4-HW',
                'AGR-8660-SP-SNE-02',
                'AGR-8660-DF-BSA-03',
                'BSA-CZRO01-ZTP03/BSA-BSA041-ZTP01',
                'MWE-RJ-SQRM03-N2 HW',
                'MWE-RJ-ARMA03-N1-HW'
                ]

    new_site = ['RCE-IBA01-NKI01',
                'FLA-CEN01-NKI01',
                'MWE-RJ-RJCG11-T1-HW x RJO-RJCG11-THWP01',
                'AIR-ETC01-NKI01',
                'AJO-ETO01-NKI01',
                'MCO-JCT01-NKI01',
                'RCE-IBA01-FHW01',
                'RGO-FER01-NKW01',
                'CASA05',
                'MCO-JCT01-NKI01',
                'RCE-JFE01-NKI01CO',
                'NLSAIG30',
                'NLCASA37',
                'NLLFSA34',
                'RGRG00',
                'RGRG00',
                'CNAR01',
                'NGAR01',
                'CRVMW01',
                'BA1320',
                'MWE-RJ-ARMA03-T3-HW x MWE-RJ-ARMA03-N1-HW',
                'SR-DQCX76',
                'MWE-RJ-ANGR01-N1-NO x MWE-RJ-ANGR01-T4-HW',
                'SP-SNE-WLC-0001',
                'DF-BSA-RAP-LJ01',
                'BSA-CZRO01-ZTP03/BSA-BSA041-ZTP01',
                'SQRM03',
                'ARMA03'
                ]

    sites_certos = pd.DataFrame()
    sites_certos['site_certo'] = new_site
    sites_certos['site_errado'] = old_site
    sites_certos.set_index('site_errado', drop=True, inplace=True)
    with col1:
        # adicionando bot??o de upload file para spazio
        up_spazio = st.file_uploader("Insira a planilha 'Spazio.xlsb'")
    if up_spazio is not None:
        spazio = pd.read_excel(up_spazio, engine='pyxlsb')
        # criando df apenas com algumas colunas da spazio
        clean = pd.DataFrame()
        clean['SITE'] = spazio['Site ID']
        clean['LATITUDE'] = spazio['Latitude']
        clean['LONGITUDE'] = spazio['Longitude']
        clean['CIDADE'] = spazio['Munic??pio']
        # adicionando bot??o de upload dfile para xtts
        with col1:
            up_xtts = st.file_uploader("Insira a planilha 'xtts.xlsx'")
        if up_xtts is not None:
            xtts = pd.read_excel(up_xtts, engine='openpyxl')
            # ajustando xtts e removendo algumas linhas
            xtts.columns = xtts.loc[1, :].values
            xtts.drop([0, 1], axis=0, inplace=True)
            xtts.reset_index(drop=True, inplace=True)
            # criando uma df apenas com informa????es relevantes do xtts
            dados = pd.DataFrame()
            dados['WO'] = xtts['ID do Ticket']
            dados['SITE'] = xtts['NE ID']
            # trocando nome dos sites que n??o tem correspond??ncia
            for site, i in zip(dados['SITE'], dados['SITE'].index):
                if site in sites_certos.index.values:
                    dados['SITE'][i] = sites_certos.loc[site, 'site_certo']
                else:
                    pass
            # combinando os dados
            dados = dados.merge(clean, how='left', on='SITE')
            # adicionando as f??rmulas para extrair os sites certos
            pattern = [r"\w*([A-Z]{6}[0-9]{2})\w*",
                       r"\w*([A-Z]{5}[0-9]{2})\w*",
                       r"\w*([A-Z]{4}[0-9]{2})\w*",
                       r"([A-Z]{3}.[A-Z]{3}[0-9]{2}.[A-Z]{3}[0-9]{2})[A-Z]{2}"
                       ]
            spazio.set_index('Site ID', drop=True, inplace=True)
            for d, i in zip(dados.loc[dados['LATITUDE'].isna(), 'SITE'],  dados[dados['LATITUDE'].isna()].index):
                if d == 'CENTRALIZADO_TX':
                    pass
                else:
                    for p in pattern:
                        sitenovo = re.search(p, d)
                        if sitenovo != None:
                            sitenovo = sitenovo.group(1)
                            if sitenovo in spazio.index:
                                dados.loc[i, 'SITE'] = sitenovo
                                dados.loc[i, 'LATITUDE'] = spazio.loc[sitenovo, 'Latitude']
                                dados.loc[i, 'LONGITUDE'] = spazio.loc[sitenovo, 'Longitude']
                                dados.loc[i, 'CIDADE'] = spazio.loc[sitenovo, 'Munic??pio']
           # tratando as strings
            dados['LATITUDE'] = dados['LATITUDE'].str.strip()
            dados['LONGITUDE'] = dados['LONGITUDE'].str.strip()
            dados['LATITUDE'] = dados['LATITUDE'].str.replace(',', '.').astype(float)
            dados['LONGITUDE'] = dados['LONGITUDE'].str.replace(',', '.').astype(float)
            dados['LATITUDE'] = dados['LATITUDE'].round(2)
            dados['LONGITUDE'] = dados['LONGITUDE'].round(2)
            # mostrando os n??o encontrados
            n_encontrados = dados[dados['LATITUDE'].isnull()]
            with col1:
                with st.beta_expander('WOs em sites n??o localizados'):
                    st.text(n_encontrados['WO'].unique())
                with st.beta_expander('Sites n??o localizados'):
                    for i in n_encontrados['SITE'].unique():
                        st.text(i)
            # removendo as nulas
            dados.dropna(axis=0, inplace=True)
            # plotando o Brasil
            brasil = folium.Map(
                                location=[-16.1237611, -59.9219642],
                                zoom_start=4
                                )
            # adicionando marcadores
            for i in range(0,len(dados)):
                html=f"""
                <p>WO: {dados.iloc[i]['WO']}
                <br>Cidade: {dados.iloc[i]['CIDADE']}
                <br>Site: {dados.iloc[i]['SITE']}</p>
                """
                iframe = folium.IFrame(html=html, width=170, height=80)
                popup = folium.Popup(iframe, max_width=2650)
                folium.Marker(
                              location=[dados.iloc[i]['LATITUDE'], dados.iloc[i]['LONGITUDE']],
                              popup=popup,
                              ).add_to(brasil)
            with col2:
                folium_static(brasil, width=800, height=650)
        else:
            print("O arquivo contendo xtts n??o foi inserido")
    else:
        print("O arquivo contendo Spazio n??o foi inserido")
else:
    print("Voc?? n??o tem permiss??o para acessar a aplica????o.")
   
