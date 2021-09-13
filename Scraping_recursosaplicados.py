# Pacotes 
from selenium import webdriver
import pymysql
import pandas as pd 
import time 
import configparser
import numpy as np

# Estrutura de conexão do banco de dados 
#config = configparser.ConfigParser()
#parser = config.read('config.ini')
#banco = parser['Banco']

host = 'localhost'
user = 'alexandre'
passwd = '34340012'
db = 'Data_saude'
port= 3306
db_conn = pymysql.connect(host=host, port=port, db=db, user=user, passwd=passwd, charset='utf8')
db_cur = db_conn.cursor()

# 1. Importando os códigos referêntes do municipios e Estados
# 1.1 Municipios 
mun = pd.read_csv("Lista de municipios.csv")

# 1.2 Estados
est = pd.read_csv("Lista de Estados.csv")

# 2. Raspando os dados 
# 2.1 Configurando o drive do chrome 
#options = webdriver.ChromeOptions()
#options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
#options.add_argument('headless')
#options.add_argument('window-size=0x0')
drive = webdriver.Chrome(executable_path='/home/alexandre/Documentos/Ciência de Dados/Monografia/Classificate_Political_Ideology/Scraper/chromedriver')#,chrome_options=options)

# 2.2 Criando a estrutura de raspagem
for estado in [23,31,53,32,52,21,51,50,15,25,41,26,22,24,43,33,11,14,42,35,28,17,12,27,16,13,29]:
    cod_mun = mun[mun['Codigo_UF']==estado]
    Estado = est[est['Codigo']==estado]['UF'].iloc[0]
    for ano in range(2013,2020):
        for code in cod_mun['Codigo']:
            try:
                # Identificando o nome do municipio
                municipio = cod_mun[cod_mun['Codigo']==code]['Municipio']

                # Criando o link de acesso as informações
                site = 'http://siops.datasus.gov.br/rel_perc_LC141.php?S=1&UF={};&Municipio={};&Ano={}&Periodo=2&g=0&e=2'.format(estado,code,ano)
                drive.get(site)
                buttom = drive.find_element_by_xpath("//div[@id='tudo']").find_element_by_xpath("//div[@id='container']").find_element_by_xpath("//div[@id='arearelatorio']").find_element_by_xpath("//div[@class='informacao centro']").find_element_by_xpath("//input[@id='carregar']").click()
                time.sleep(2)
                table =drive.find_element_by_xpath("//div[@id='dados']").find_elements_by_xpath("//table[@class='nova']")                
                #  Receitas de Impostos e Transferências Constitucionais e Legais
                Descrição = []
                var =[]
                for i in range(0,19):
                    Descrição.append(table[0].find_elements_by_xpath("//td[@align='left']")[i].text.replace(" ",""))
                Previsão=[]
                for j in range(0,38):
                    lines = table[0].find_elements_by_xpath("//td[@align='right']")[j].text
                    if lines ==' ':
                        lines='0.000000001'
                    elif lines == 'N/A':
                        lines="0.000000001"       
                    else:
                        lines = float(lines.replace(".","").replace(",","."))

                        if j >0 :
                            if j%2 !=0:
                                Previsão.append(lines)
                            else:
                                var.append(Previsão)
                                Previsão=[]
                                Previsão.append(lines)
                        else:
                            Previsão.append(lines)
                var.append(Previsão)
                # TODO: Sql conection

                # Despesa Total com Ações e Serviços Públicos de Saúde
                Descrição = []
                var =[]
                for i in range(19,32):
                    Descrição.append(table[0].find_elements_by_xpath("//td[@align='left']")[i].text.replace(" ",""))
                Previsão=[]
                for j in range(36,88):
                    lines = table[0].find_elements_by_xpath("//td[@align='right']")[j].text
                    if lines ==' ':
                        lines='0.000000001'
                    elif lines == 'N/A':
                        lines="0.000000001"       
                    else:
                        lines = float(lines.replace(".","").replace(",","."))
                        Previsão.append(lines)
                pre_var=[]
                for i in range(len(Previsão)):
                    if i%4!=0:
                        pre_var.append(Previsão[i])
                    else:
                        var.append(pre_var)
                        pre_var=[]
                        pre_var.append(Previsão[i])
                        
                var.append(pre_var)
                var_last = var[-1][0:4]
                var[-1] = var_last
                var = var[1:]

                # Receitas de Transferências de Recursos do SUS
                Descrição =[]
                var =[]
                for i in range(32,57):
                    Descrição.append(table[0].find_elements_by_xpath("//td[@align='left']")[i].text.replace(" ",""))
                Previsão =[]
                for j in range(88,140):
                     lines = table[0].find_elements_by_xpath("//td[@align='right']")[j].text
                     if lines ==' ':
                         lines='0.000000001'
                     elif lines == 'N/A':
                         lines="0.000000001"       
                     else:
                         lines = float(lines.replace(".","").replace(",","."))
                         Previsão.append(lines)
                pre_var=[]
                for i in range(len(Previsão)):
                    if i%2!=0:
                        pre_var.append(Previsão[i])
                    else:
                        var.append(pre_var)
                        pre_var=[]
                        pre_var.append(Previsão[i])
                var.append(pre_var)
                var_last = var[-1][0:4]
                var[-1] = var_last
                var = var[1:]
