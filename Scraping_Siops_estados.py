# Pacotes
from selenium import webdriver
import pymysql 
import pandas as pd 
import time 
import configparser
import numpy as np

# Estrutura de conexão do banco de dados 
host = 'localhost'
user = 'alexandre'
passwd = '34340012'
db = 'Data_saude'
port= 3306
db_conn = pymysql.connect(host=host, port=port, db=db, user=user, passwd=passwd, charset='utf8')
db_cur = db_conn.cursor()

# 1. Estados
est = pd.read_csv("Lista de Estados.csv")

# 2. Raspando os dados
drive = webdriver.Chrome(executable_path='/home/alexandre/Documents/Observatório do Federalismo Brasileiro/Siops-Datasus-Webscraping/chromedriver')

# 3. Criando a estrutura de raspagem 
for estado in [23,31,53,32,52,21,51,50,15,25,41,26,22,24,43,33,11,14,42,35,28,17,12,27,16,13,29]:
    Estado = est[est['Codigo']==estado]['UF'].iloc[0]
    for ano in range(2013,2020):
        try:
            # Criando o link de acesso as informações 
            site = 'http://siops.datasus.gov.br/consleirespfiscal_uf.php?S=1&UF={};&Ano={}&Periodo=2'.format(estado,ano)
            print("Estado:{} e Ano:{}".format(estado,ano))

            # Acessando o link 
            drive.get(site)
            # Gerando as labelasde informações 
            buttom = drive.find_element_by_xpath("//div[@id='tudo']").find_element_by_xpath("//div[@id='container']").find_element_by_xpath("//div[@class='informacao']").find_element_by_xpath("//div[@class='centro']").find_element_by_xpath("//input[@type='Submit']")
            buttom.click()

            # Extraindo as tabelas de informações
            table = drive.find_element_by_xpath("//div[@id='tudo']").find_element_by_xpath("//div[@id='arearelatorio']").find_element_by_xpath("//div[@class='informacao']").find_elements_by_xpath("//table[@class='tam2 tdExterno']")

            if estado != 53:
                # RECEITAS PARA APURAÇÃO DA APLICAÇÃO EM AÇÕES E SERVIÇOS PÚBLICOS DE SAÚDE
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
                    sql = 'INSERT INTO Receitas_apuracao_sps_estadual(estado,ano,campo,previsao_inicial,previsao_atualizada,Receitas_realizadas_Bimestre,Receitas_realizadas_Porcentagem) VALUES("{}","{}","{}","{}","{}","{}","{}")'
                    db_cur.execute(sql.format(Estado,str(ano),str(Descrição[k].replace('"',"|")),str(var[k][0]),str(var[k][1]),str(var[k][2]),str(var[k][3])))
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
                    sql = 'INSERT INTO Receitas_adicionais_financiamento_estadual(estado,ano,campo,previsao_inicial,previsao_atualizada,Receitas_realizadas_Bimestre,Receitas_realizadas_Porcentagem) VALUES("{}","{}","{}","{}","{}","{}","{}")'
                    db_cur.execute(sql.format(Estado,str(ano),str(Descrição[k].replace('"',"|")),str(var[k][0]),str(var[k][1]),str(var[k][2]),str(var[k][3])))
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
                    sql = 'INSERT INTO Despesas_saude_natureza_estadual(estado,ano,campo,dotacao_inicial,dotacao_atualizada,despesas_executadas_liquidadas,despesas_executadas_inscritas,despesas_executadas_porcentagem)VALUES("{}","{}","{}","{}","{}","{}","{}","{}")'
                    db_cur.execute(sql.format(Estado,str(ano),str(Descrição[k].replace('"',"|")),str(var[k][0]),str(var[k][1]),str(var[k][2]),str(var[k][3]),str(var[k][4])))
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
                    sql = 'INSERT INTO Despesas_saude_nao_computadas_estadual(estado,ano,campo,dotacao_inicial,dotacao_atualizada,despesas_executadas_liquidadas,despesas_executadas_inscritas,despesas_executadas_porcentagem)VALUES("{}","{}","{}","{}","{}","{}","{}","{}")'
                    db_cur.execute(sql.format(Estado,str(ano),str(Descrição[k].replace('"',"|")),str(var[k][0]),str(var[k][1]),str(var[k][2]),str(var[k][3]),str(var[k][4])))
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
                    sql = 'INSERT INTO Despesas_saude_subfuncao_estadual(estado,ano,campo,dotacao_inicial,dotacao_atualizada,despesas_executadas_liquidadas,despesas_executadas_inscritas,despesas_executadas_porcentagem)VALUES("{}","{}","{}","{}","{}","{}","{}","{}")'
                    db_cur.execute(sql.format(Estado,str(ano),str(Descrição[k].replace('"',"|")),str(var[k][0]),str(var[k][1]),str(var[k][2]),str(var[k][3]),str(var[k][4])))
                    db_conn.commit()
                    print("Insert")
            else: 
                # RECEITAS PARA APURAÇÃO DA APLICAÇÃO EM AÇÕES E SERVIÇOS PÚBLICOS DE SAÚDE
                Descrição = []
                var = []
                for i in range(0,40):    
                    Descrição.append(table[1].find_elements_by_xpath("//td[@class='td2 caixa']")[i].text)        
                Previsão = []
                for j in range(0,156):
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
                for k in range(0,len(Descrição)-1):
                    sql = 'INSERT INTO Receitas_apuracao_sps_estadual(estado,ano,campo,previsao_inicial,previsao_atualizada,Receitas_realizadas_Bimestre,Receitas_realizadas_Porcentagem) VALUES("{}","{}","{}","{}","{}","{}","{}")'
                    db_cur.execute(sql.format(Estado,str(ano),str(Descrição[k].replace('"',"|")),str(var[k][0]),str(var[k][1]),str(var[k][2]),str(var[k][3])))
                    db_conn.commit()
                    print("Insert")
                
                # 2.3.2 RECEITAS ADICIONAIS PARA FINANCIAMENTO DA SAÚDE	
                Descrição =[]
                var =[]
                for i in range(40,48):
                    Descrição.append(table[1].find_elements_by_xpath("//td[@class='td2 caixa']")[i].text)
                Previsão =[]
                for j in range(160,196):
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
                    sql = 'INSERT INTO Receitas_adicionais_financiamento_estadual(estado,ano,campo,previsao_inicial,previsao_atualizada,Receitas_realizadas_Bimestre,Receitas_realizadas_Porcentagem) VALUES("{}","{}","{}","{}","{}","{}","{}")'
                    db_cur.execute(sql.format(Estado,str(ano),str(Descrição[k].replace('"',"|")),str(var[k][0]),str(var[k][1]),str(var[k][2]),str(var[k][3])))
                    db_conn.commit()
                    print("Insert")

                #2.3.3 DESPESAS COM SAÚDE
                Descrição =[]
                var=[]
                for i in range(48,57):
                    Descrição.append(table[1].find_elements_by_xpath("//td[@class='td2 caixa']")[i].text)
                Previsão =[]
                for j in range(112,240):
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
                    sql = 'INSERT INTO Despesas_saude_natureza_estadual(estado,ano,campo,dotacao_inicial,dotacao_atualizada,despesas_executadas_liquidadas,despesas_executadas_inscritas,despesas_executadas_porcentagem)VALUES("{}","{}","{}","{}","{}","{}","{}","{}")'
                    db_cur.execute(sql.format(Estado,str(ano),str(Descrição[k].replace('"',"|")),str(var[k][0]),str(var[k][1]),str(var[k][2]),str(var[k][3]),str(var[k][4])))
                    db_conn.commit()
                    print("Insert")

                # 2.3.4 Despesas com saúde não computadas
                Descrição =[]
                var =[]
                for i in range(57,68):
                    Descrição.append(table[1].find_elements_by_xpath("//td[@class='td2 caixa']")[i].text)
                Previsão =[]
                for j in range(236,284):
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
                    if i%4!=0:
                        pre_var.append(Previsão[i])
                    else:
                        var.append(pre_var)
                        pre_var=[]
                        pre_var.append(Previsão[i])   
                        
                var_last=var[-1][0:3]
                var_last.insert(3,'0.000000001')
                var[-1]=var_last
                var=var[1:]
                for k in range(0,len(Descrição)-1):
                    sql = 'INSERT INTO Despesas_saude_nao_computadas_estadual(estado,ano,campo,dotacao_inicial,dotacao_atualizada,despesas_executadas_liquidadas,despesas_executadas_inscritas,despesas_executadas_porcentagem)VALUES("{}","{}","{}","{}","{}","{}","{}","{}")'
                    db_cur.execute(sql.format(Estado,str(ano),str(Descrição[k].replace('"',"|")),str(var[k][0]),str(var[k][1]),str(var[k][2]),str(var[k][3]),str(var[k][4])))
                    db_conn.commit()
                    print("Insert")
                        
                # 2.3.5 DESPESAS COM SAÚDE (Por Subfunção)
                Descrição =[]
                var =[]
                for i in range(8,0,-1):
                    Descrição.append(table[1].find_elements_by_xpath("//td[@class='td2 caixa']")[-i].text)
                Previsão =[]
                for j in range(39 ,0,-1):
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
                for k in range(0,len(Descrição)-1):
                    sql = 'INSERT INTO Despesas_saude_subfuncao_estadual(estado,ano,campo,dotacao_inicial,dotacao_atualizada,despesas_executadas_liquidadas,despesas_executadas_inscritas,despesas_executadas_porcentagem)VALUES("{}","{}","{}","{}","{}","{}","{}","{}")'
                    db_cur.execute(sql.format(Estado,str(ano),str(Descrição[k].replace('"',"|")),str(var[k][0]),str(var[k][1]),str(var[k][2]),str(var[k][3]),str(var[k][4])))
                    db_conn.commit()
                    print("Insert")
        except Exception as e:
            print(e)
