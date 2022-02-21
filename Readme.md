<h1 align=center> Scraping Siops/Datasus</h1>
<h2 align=center> Script para raspagem do Demonstrativo da despesa com saúde </h2>

--- 

O SIOPS é o sistema informatizado, de alimentação obrigatória e acesso público, operacionalizado pelo Ministério da Saúde, instituído para coleta, recuperação, processamento, armazenamento, organização, e disponibilização de informações referentes às receitas totais e às despesas com saúde dos orçamentos públicos em saúde. O sistema possibilita o acompanhamento e monitoramento da aplicação de recursos em saúde, no âmbito da  União, Estados, Distrito Federal e Municípios, sem prejuízo das atribuições próprias dos Poderes Legislativos e dos Tribunais de Contas.

---
## Informação sobre o scraper 

### Histórico das versões 

- [ ] Versão para o estado do Ceará
- [x] Versão para todo o Brasil 
- [x] Versão com tabelas adicionais
### Versão 0.1 

- Raspagem das principais tabelas do siops 
  - Receitas para apuração da aplicação em ações e serviços públicos de saúde
  - Receitas adicionais para financiamento da saúde	
  - Despesas com saúde (por grupo de natureza de despesa)
  - Despesas com saúde não computadas para fins de apuração do percentual mínimo	
  - Despesas com saúde	
- Amostra : Municipios do Estado do Ceará 
- Intervalo Temporal : 2013 -2019 

### Versão 0.1.1 

- Inclusão do tratamento de erro (try and except)

### Versão 0.2 
- Amostra : Municipios de todo o território brasileiro

### Versão 0.3 
- Raspagem das principais tabelas do siops
  - Receitas para apuração da aplicação em ações e serviços públicos de saúde
  - Receitas adicionais para financiamento da saúde	
  - Despesas com saúde (por grupo de natureza de despesa)
  - Despesas com saúde não computadas para fins de apuração do percentual mínimo	
  - Despesas com saúde	
  - Tabelas adicionais (Percentual de Aplicação em Ações e Valor referente à diferença)
  
### Versão 0.3.1 
- Correção da raspagem da tabela Despesas com Saúde (Por Subfunção) 

### Versão 0.4 

- Raspagem das tabelas do siops - Recursos Próprios Aplicados em Saúde
  - Receitas de Impostos e Transferências Constitucionais e Legais Vinculadas à Saúde
  - Despesa Total com Ações e Serviços Públicos de Saúde
  - Receitas de Transferências de Recursos do SUS
- Amostra : Municipios do Brasileiros
- Intervalo Temporal : 2013 -2019 

### Versão 0.5 
- Amostra: Municipios e Estados Brasileiros 

### Versão 0.6 
- Personalização do codigo para o Distrito Federal 

---
## Pre requisitos 

Antes de iniciar, verifique se você atende os seguintes requisitos:

### 1. Necessita da instalação das seguintes ferramentas 

- [Python 3.9+](https://www.python.org/downloads/)
- [MySQL 8+](https://www.mysql.com/) ou [Mariadb 10.6 +](https://mariadb.org/)
- [Google Chrome 87.0](https://www.google.com/intl/pt-BR/chrome/) 
- [Google Chrome chromedrive 87.0 ](https://chromedriver.storage.googleapis.com/index.html?path=87.0.4280.88/)

### 2. Necessita da instalação dos seguintes pacotes para python: 


- [selenium](https://selenium-python.readthedocs.io/installation.html)
- [pymysql](https://pypi.org/project/PyMySQL/)
- [pandas](https://pandas.pydata.org/) 
- [time](https://docs.python.org/3/library/time.html) 
- [configparser](https://docs.python.org/3/library/configparser.html)

---

## Executando o Scraper 

### Obtendo o repositório 

```shell
$ git clone https://github.com/LuizAlexandre21/Siops-Datasus-Webscraping.git
```

### Atribuindo os valores para o banco de dados 
Editando o arquivo config.ini 
```python
[Banco]
host = 'localhost'
user = 'user'
passwd = "passwd"
db = "db"
port = "port"
```

### Executando o código 
- **Tabelas principais do SIOPS**

```shell 
python Scraping.py 
```

- **Recursos Próprios Aplicados em Saúde**

```shell
python Scraping_recursosaplicados.py
```

- **Tabelas dos SIOPS para o estado**

```shell
python Scraping_Siops_estados.py
```
## Contato 

:bust_in_silhouette: Luiz Alexandre Moreira Barros 

:mailbox_with_mail:	 luizalexandremoreira21@outlook.com

:octocat: https://github.com/LuizAlexandre21

:notebook_with_decorative_cover: http://lattes.cnpq.br/9458204748985902
