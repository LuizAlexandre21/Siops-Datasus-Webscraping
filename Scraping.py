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
for estado in [31,53,32,52,21,51,50,15,25,41,26,22,24,43,33,11,14,42,35,28,17,12,27,16,13,29]:
    cod_mun = mun[mun['Codigo_UF']==estado]
    Estado =  est[est['Codigo']==estado]['UF'].iloc[0]
    for ano in range(2014,2020): # TODO: Corrigir o intervalo
        for code in cod_mun['Codigo']:
            try:
               
                # Identificando o nome do municipio
                municipio = cod_mun[cod_mun['Codigo']==code]['municipio']
                # Criando o link de acesso as informações 
                site = 'http://siops.datasus.gov.br/consleirespfiscal.php?S=1&UF={};&Municipio={};&Ano={}&Periodo=2'.format(estado,code,ano)
                print(site)
                # Acessando o link
                drive.get(site)

                # Gerando as tabelas de informações 
                buttom = drive.find_element_by_xpath("//div[@id='tudo']").find_element_by_xpath("//div[@id='container']").find_element_by_xpath("//div[@class='informacao']").find_element_by_xpath("//div[@class='centro']").find_element_by_xpath("//input[@type='Submit']")
                buttom.click()

                # 2.3 Extraindo tabelas do siops 
                table = drive.find_element_by_xpath("//div[@id='tudo']").find_element_by_xpath("//div[@id='arearelatorio']").find_element_by_xpath("//div[@class='informacao']").find_elements_by_xpath("//table[@class='tam2 tdExterno']")
                
                # 2.3.1 RECEITAS PARA APURAÇÃO DA APLICAÇÃO EM AÇÕES E SERVIÇOS PÚBLICOS DE SAÚDE
                Descrição = []
                var = []
                for i in range(0,19):    
                    Descrição.append(table[1].find_elements_by_xpath("//td[@class='td2 caixa']")[i].text)        
                Previsão = []
                for j in range(0,76):
                    lines = table[1].find_elements_by_xpath("//td[@class='tdr caixa']")[j].text
                    if lines ==' ':
                        lines='0.000000001'
                    elif lines == 'N/A':
                        lines="0.000000001"       
                    else:
                        lines = float(lines.replace(".","").replace(",","."))
                    if j >0 :
                        if j%4 !=0:
                            Previsão.append(lines)
                        else: 
                            var.append(Previsão)
                            Previsão=[]
                            Previsão.append(lines)
                    else:
                        Previsão.append(lines) 
                var.append(Previsão)
                # Importando os dados para o banco 
                for k in range(0,len(Descrição)):
                    sql = 'INSERT INTO Receitas_apuração_sps(municipio,codigo_municipio,estado,ano,campo,previsao_inicial,previsão_atualizada,Receitas_realizadas_Bimestre,Receitas_realizadas_Porcentagem) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'
                    db_cur.execute(sql.format(list(municipio)[0], str(code),Estado,str(ano),str(Descrição[k]),str(var[k][0]),str(var[k][1]),str(var[k][2]),str(var[k][3])))
                    db_conn.commit()
                    print("Insert")
            
                # 2.3.2 RECEITAS ADICIONAIS PARA FINANCIAMENTO DA SAÚDE	
                Descrição =[]
                var =[]
                for i in range(19,28):
                    Descrição.append(table[1].find_elements_by_xpath("//td[@class='td2 caixa']")[i].text)
                Previsão =[]
                for j in range(76,113):
                    lines = table[1].find_elements_by_xpath("//td[@class='tdr caixa']")[j].text
                    if lines ==' ':
                        lines='0.000000001'
                    elif lines == 'N/A':
                        lines="0.000000001"
                    else:
                        lines = float(lines.replace(".","").replace(",","."))
                    if j%4 !=0:
                        Previsão.append(lines)
                    else: 
                        var.append(Previsão)
                        Previsão=[]
                        Previsão.append(lines)
                var = var[1:]
                for k in range(0,len(Descrição)):
                    sql = 'INSERT INTO Receitas_adicionais_financiamento(municipio,codigo_municipio,estado,ano,campo,previsao_inicial,previsão_atualizada,Receitas_realizadas_Bimestre,Receitas_realizadas_Porcentagem) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'
                    db_cur.execute(sql.format(list(municipio)[0], str(code),Estado,str(ano),str(Descrição[k]),str(var[k][0]),str(var[k][1]),str(var[k][2]),str(var[k][3])))
                    db_conn.commit()
                    print("Insert")

                #2.3.3 DESPESAS COM SAÚDE
                Descrição =[]
                var=[]
                for i in range(28,38):
                    Descrição.append(table[1].find_elements_by_xpath("//td[@class='td2 caixa']")[i].text)
                Previsão =[]
                for j in range(112,159):
                    lines = table[1].find_elements_by_xpath("//td[@class='tdr caixa']")[j].text
                    if lines ==' ':
                        continue
                    else:
                        lines = lines.replace(".","").replace(",",".")
                        Previsão.append(lines)
                pre_var =[]
                for i in range(len(Previsão)-2):
                    if i%5!=0:
                        pre_var.append(Previsão[i])
                    else:
                        var.append(pre_var)
                        pre_var=[]
                        pre_var.append(Previsão[i])
                pre_var.insert(3,"0.000000001")
                if ano not in [2016,2017,2018,2019]:
                    var.append(pre_var[0:-1])
                else:
                    var.append(pre_var)
                var=var[1:]
                for k in range(0,len(Descrição)-1):
                    sql = 'INSERT INTO Despesas_saude_natureza(municipio,codigo_Municipio,estado,ano,campo,dotação_inicial,dotação_atualizada,despesas_executadas_liquidadas,despesas_executadas_inscritas,despesas_executadas_porcentagem)VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")'
                    db_cur.execute(sql.format(list(municipio)[0], str(code),Estado,str(ano),str(Descrição[k]),str(var[k][0]),str(var[k][1]),str(var[k][2]),str(var[k][3]),str(var[k][4])))
                    db_conn.commit()
                    print("Insert")

                # 2.3.4 Despesas com saúde não computadas
                Descrição =[]
                var =[]
                for i in range(37,49):
                    Descrição.append(table[1].find_elements_by_xpath("//td[@class='td2 caixa']")[i].text)
                Previsão =[]
                for j in range(156,214):
                    lines = table[1].find_elements_by_xpath("//td[@class='tdr caixa']")[j].text
                    if lines ==' ':
                        Previsão.append('0.000000001')
                    elif lines == 'N/A':
                        Previsão.append("0.000000001")
                    else:
                        lines = lines.replace(".","").replace(",",".")
                        Previsão.append(lines)
                    
                pre_var =[]
                for i in range(len(Previsão)):
                    if i%5!=0:
                        pre_var.append(Previsão[i])
                    else:
                        var.append(pre_var)
                        pre_var=[]
                        pre_var.append(Previsão[i])   
                    
                var_last=var[-1][0:4]
                var_last.insert(3,'0.000000001')
                var[-1]=var_last
                var=var[1:]
                for k in range(0,len(Descrição)-1):
                    sql = 'INSERT INTO Despesas_saúde_não_computadas(municipio,codigo_Municipio,estado,ano,campo,dotação_inicial,dotação_atualizada,despesas_executadas_liquidadas,despesas_executadas_inscritas,despesas_executadas_porcentagem)VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")'
                    db_cur.execute(sql.format(list(municipio)[0], str(code),Estado,str(ano),str(Descrição[k]),str(var[k][0]),str(var[k][1]),str(var[k][2]),str(var[k][3]),str(var[k][4])))
                    db_conn.commit()
                    print("Insert")
                    
                # 2.3.5 DESPESAS COM SAÚDE (Por Subfunção)
                Descrição =[]
                var =[]
                for i in range(8,0,-1):
                    Descrição.append(table[1].find_elements_by_xpath("//td[@class='td2 caixa']")[-i].text)
                Previsão =[]
                for j in range(40 ,0,-1):
                    lines = table[1].find_elements_by_xpath("//td[@class='tdr caixa']")[-j].text
                    if lines ==' ':
                        Previsão.append('0.000000001')
                    elif lines == 'N/A':
                        Previsão.append("0.000000001")
                    else:
                        lines = lines.replace(".","").replace(",",".")
                        Previsão.append(lines)
                pre_var =[]
                for k in range(len(Previsão)):
                    if k%5!=0:
                        pre_var.append(Previsão[k])
                        if k == len(Previsão):
                            var.append(pre_var)
                    else:
                        var.append(pre_var)
                        pre_var=[]
                        pre_var.append(Previsão[k]) 
                var.append(pre_var)  
                var_last=var[-1][0:4]
                var_last.insert(3,'0.000000001')
                var[-1]=var_last
                var=var[1:]
                for k in range(0,len(Descrição)):
                    sql = 'INSERT INTO Despesas_saúde_subfunção(municipio,codigo_municipio,estado,ano,campo,dotação_inicial,dotação_atualizada,despesas_executadas_liquidadas,despesas_executadas_inscritas,despesas_executadas_porcentagem)VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")'
                    db_cur.execute(sql.format(list(municipio)[0], str(code),Estado,str(ano),str(Descrição[k]),str(var[k][0]),str(var[k][1]),str(var[k][2]),str(var[k][3]),str(var[k][4])))
                    db_conn.commit()
                    print("Insert")

                # 2.3.6 Contas adicionais
                Previsão =[]
                for n in range(214,216):
                    lines = table[1].find_elements_by_xpath("//td[@class='tdr caixa']")[n].text
                    if lines ==' ':
                        Previsão.append('0.000000001')
                    elif lines == 'N/A':
                        Previsão.append("0.000000001")
                    else:
                        lines = lines.replace(".","").replace(",",".")
                        Previsão.append(lines)
                    if n%2 ==0:
                        for k in range(0,len(Descrição)):
                            sql = 'INSERT INTO Tabelas_adicionais(municipio,codigo_municipio,estado,ano,campo,Total)VALUES("{}","{}","{}","{}","{}","{}")'
                            db_cur.execute(sql.format(list(municipio)[0], str(code),Estado,str(ano),'PERCENTUAL DE APLICAÇÃO EM AÇÕES E SERVIÇOS PÚBLICOS DE SAÚDE SOBRE A RECEITA DE IMPOSTOS LÍQUIDA E TRANSFERÊNCIAS CONSTITUCIONAIS E LEGAIS',str(var[k][0])))
                            db_conn.commit()
                            print("Insert")
                    else:
                        for k in range(0,len(Descrição)):
                            sql = 'INSERT INTO Tabelas_adicionais(municipio,codigo_municipio,estado,ano,campo,Total)VALUES("{}","{}","{}","{}","{}","{}")'
                            db_cur.execute(sql.format(list(municipio)[0], str(code),Estado,str(ano),'VALOR REFERENTE À DIFERENÇA ENTRE O VALOR EXECUTADO E O LIMITE MÍNIMO CONSTITUCIONAL',str(var[k][0])))
                            db_conn.commit()
                            print("Insert")
            except Exception as e:
                print(e)
                print(" Na cidade {} e no Ano {}, existe um problema".format(code,ano))
