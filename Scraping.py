# Pacotes 
from selenium import webdriver
import pymysql
import pandas as pd 
import time 

# Estrutura de conexão do banco de dados 
host = 'localhost'
user = 'root'
passwd = "34340012"
db = "Datasus"
port=3306
db_conn = pymysql.connect(host=host, port=port, db=db, user=user, passwd=passwd, charset='utf8')
db_cur = db_conn.cursor()


# 1. Importando os códigos referêntes do municipios 
cod_mun = pd.read_csv("Lista de municipios.csv")

# 2. Raspando os dados 
# 2.1 Configurando o drive do chrome 
drive = webdriver.Chrome(executable_path='/home/alexandre/Documentos/Ciência de Dados/Monografia/Classificate_Political_Ideology/Scraper/chromedriver')

# 2.2 Criando a estrutura de raspagem
for ano in range(2013,2020):
    for code in cod_mun['Codigo']:
        # Identificando o nome do municipio
        municipio = cod_mun[cod_mun['Codigo']==code]['Cidade']

        # Criando o link de acesso as informações 
        site = 'http://siops.datasus.gov.br/consleirespfiscal.php?S=1&UF=23;&Municipio={};&Ano={}&Periodo=2'.format(code,ano)
        print(site)

        # Acessando o link
        drive.get(site)
        
        # Criando um sleep na raspagem 
        time.sleep(2)

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
            sql = 'INSERT INTO 1_Receitas_apuração_SPS(municipio,codigo_municipio,estado,ano,campo,previsao_inicial,previsão_atualizada,Receitas_realizadas_Bimestre,Receitas_realizadas_Porcentagem) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'
            db_cur.execute(sql.format(list(municipio)[0], str(code),'Ceará',str(ano),str(Descrição[k]),str(var[k][0]),str(var[k][1]),str(var[k][2]),str(var[k][3])))
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
                Previsão.append('0.000000001')
            elif lines == 'N/A':
                Previsão.append("0.000000001")
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
            sql = 'INSERT INTO 2_Receitas_adicionais_financiamento(municipio,codigo_municipio,estado,ano,campo,previsao_inicial,previsão_atualizada,Receitas_realizadas_Bimestre,Receitas_realizadas_Porcentagem) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'
            db_cur.execute(sql.format(list(municipio)[0], str(code),'Ceará',str(ano),str(Descrição[k]),str(var[k][0]),str(var[k][1]),str(var[k][2]),str(var[k][3])))
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
        print(pre_var)
        pre_var.insert(3,"0.000000001")
        var.append(pre_var[0:-1])
        var=var[1:]
        for k in range(0,len(Descrição)-1):
            sql = 'INSERT INTO 3_Despesas_saúde_natureza(municipio,codigo_Municipio,estado,ano,campo,dotação_inicial,dotação_atualizada,despesas_executadas_liquidadas,despesas_executadas_inscritas,despesas_executadas_porcentagem)VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")'
            db_cur.execute(sql.format(list(municipio)[0], str(code),'Ceará',str(ano),str(Descrição[k]),str(var[k][0]),str(var[k][1]),str(var[k][2]),str(var[k][3]),str(var[k][4])))
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
            sql = 'INSERT INTO 4_Despesas_saúde_não_computadas(municipio,codigo_Municipio,estado,ano,campo,dotação_inicial,dotação_atualizada,despesas_executadas_liquidadas,despesas_executadas_inscritas,despesas_executadas_porcentagem)VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")'
            db_cur.execute(sql.format(list(municipio)[0], str(code),'Ceará',str(ano),str(Descrição[k]),str(var[k][0]),str(var[k][1]),str(var[k][2]),str(var[k][3]),str(var[k][4])))
            db_conn.commit()
            print("Insert")

        # 2.3.5 DESPESAS COM SAÚDE (Por Subfunção)
        Descrição =[]
        var =[]
        for i in range(56,64):
            Descrição.append(table[1].find_elements_by_xpath("//td[@class='td2 caixa']")[i].text)
        Previsão =[]
        for j in range(246,285):
            lines = table[1].find_elements_by_xpath("//td[@class='tdr caixa']")[j].text
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
            sql = 'INSERT INTO 5_Despesas_saúde_subfunção(municipio,codigo_municipio,estado,ano,campo,dotação_inicial,dotação_atualizada,despesas_executadas_liquidadas,despesas_executadas_inscritas,despesas_executadas_porcentagem)VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")'
            db_cur.execute(sql.format(list(municipio)[0], str(code),'Ceará',str(ano),str(Descrição[k]),str(var[k][0]),str(var[k][1]),str(var[k][2]),str(var[k][3]),str(var[k][4])))
            db_conn.commit()
            print("Insert")