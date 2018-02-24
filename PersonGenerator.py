import sys
import datetime
import argparse as argp
from math import floor
from random import randint, random

import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup as bs

from Person import Person


DB_USER = ""
DB_PASS = ""
DB_HOST = ""
DB_PORT = ""
DB_USES = ""
DB_COLL = ""

# Função para tratar a data de nascimento
def parseDate(dateString):
    month = [
        'January', 'February', 'March', 'April',
        'May', 'June', 'July', 'August', 'September',
        'October', 'November', 'December'
    ]
    month = {m: i+1 for i, m in enumerate(month)}
    split = dateString.split(' ')

    return datetime.datetime(int(split[2]), month[split[0]], int(split[1][0]))

# Função Scrapper para destrinchar o .html e gerar um objeto <Person>
def parsePerson(sex, infos):
    main_info = infos.find('div', class_='address')
    p = Person()
    p.name = main_info.find('h3').get_text() # OK
    p.sex = sex
    
    adr_pretty = main_info.find('div', class_='adr').prettify()
    adr_pretty = adr_pretty.replace('\n', '').split('<br/>')

    p.address = adr_pretty[0][18:][:-1] # OK
    p.city = adr_pretty[1].split('-')[0][1:] # OK
    p.uf = adr_pretty[1].split('-')[1][:-1] # OK

    extra_info = infos.find_all('dl', class_='dl-horizontal')
    p.cardCompany = extra_info[13].find('dt').get_text()
    extra_info = [ex.find('dd').get_text() for ex in extra_info]

    p.cpf = extra_info[1].replace('.','').replace('-', '')[:-1] # OK
    p.cel = extra_info[3].replace(' ','').replace('(', '').replace(')','').replace('-','') # OK
    p.bDay = parseDate(extra_info[5])
    p.email = extra_info[8].split(' ')[0]
    p.cardNumber = extra_info[13].replace(' ', '')
    p.cardVigor = datetime.datetime(int(extra_info[14].split('/')[1]), int(extra_info[14].split('/')[0]), 1)
    p.cardLimit = round(700 + 500 * random(), 2)
    p.cvc2 = int(extra_info[15])
    p.height = float(extra_info[18].split(' ')[2][1:])/100
    p.weigh = float(extra_info[19].split(' ')[2][1:])
    p.tBlood = extra_info[20]
    p.guid = extra_info[26]
    
    return p

# Função de 'probabilidade' dos sexos
def getSex(mp):
    if 0 <= randint(0, 100) <= mp:
        return 'M'
    
    return 'F'

# Função para configurar as variáveis do DB
def setDbConfig():
    global DB_USER
    global DB_PASS
    global DB_HOST
    global DB_PORT
    global DB_USES
    global DB_COLL

    try:
        file = open('dbconfig.txt', 'r')
        text = file.read().split('|')
        DB_USER = text[0]
        DB_PASS = text[1]
        DB_HOST = text[2]
        DB_PORT = text[3]
        DB_USES = text[4]
        DB_COLL = text[5]
    except:
        print("Erro ao abrir arquivo")
        sys.exit()

# Função para perguntar 'Quer adicionar ao DB?' 
def wannaAddToDB():
    print("\nInserir no banco de dados[s,n]? ", end="")
    res = input()
    res = res.lower()

    if res in ['s', 'n']:
        if res == 's': return True
        return False
    
    print("Opção inválida")
    wannaAddToDB()
    
# Função para inserir um objeto <Person> no mongoDB
def addToDB(p, collection):
    try:
        collection.insert_one(p.toDict())
        print("Adicionado")

    except:
        print("Erro ao adicionar perfil") 

# main
def main(manprob=50, age=[1, 100], qntd=1, dbConfig=False, each=True):
    URL = 'http://pt.fakenamegenerator.com/advanced.php?'

    try:
        sex = {'M': 100, 'F': 0}
        addCount = 0

        if dbConfig:
            setDbConfig()
            client = MongoClient(
                'mongodb://'+DB_USER+':'+DB_PASS+'@'+DB_HOST+':'+DB_PORT+'/'+DB_USES
            )
            db = client[DB_USES]
            collection = db[DB_COLL]


        for _ in range(qntd):
            s = getSex(manprob)
            params = {
                't': 'country',
                'n[]': 'br',
                'c[]': 'br',
                'gen': sex[s],
                'age-min': age[0],
                'age-max': age[1]
            }
            page = requests.get(URL, params=params)
            
            if page.status_code == 200:
                soup = bs(page.content, 'html.parser')
                infos = soup.find('div', class_='info')

                if infos:
                    p = parsePerson(s, infos)
                    print("\033c")
                    if not dbConfig:
                        print(p)
                        input()

                    if dbConfig:
                        if each:
                            print(p)

                            if wannaAddToDB():
                                addToDB(p, collection)
                                addCount += 1

                        else:
                            addToDB(p, collection)        
                            addCount += 1
                            print(str(addCount) + "/" + str(qntd))
                                                           
                else:
                    print("ERROR")

            else:
                print(URL + ' não alcançado')

        print("\033c")

        if dbConfig: 
            print(str(addCount) + " perfis adicionados no banco de dados")

    except Exception as err:
        print(err)


if __name__ == "__main__":
    def str2bool(v):
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            print("Valor booleano esperado")
            sys.exit()


    parser = argp.ArgumentParser(description='Gerador de pessoas aleatórias')

    parser.add_argument('-mp', action='store', dest='mp', help='Probabilidade de ser gerado um homem entre [0, 100]', default=50, type=int)
    parser.add_argument('-max', action='store', dest='max', help='Quantidade de pessoas a ser gerada, valor >= 1', default=1, type=int)
    parser.add_argument('-age', action='store', nargs='+', dest='age', help='Idade mínima e idade máxima entre 1 e 100 ', default=[1, 100], type=int)
    parser.add_argument('-db', action='store', dest='toDB', help='Indica se dados serão inseridos em um MongoDB', default=False, type=str2bool)
    parser.add_argument('-each', action='store', dest='each', help='Se verdadeiro, solicita confirmação a cada perfil', default=True, type=str2bool)

    args = parser.parse_args()

    if not 0 <= args.mp <= 100:
        print("Probabilidade deve estar no intervalo [0, 100]")
    if args.max < 1:
        print("Número máximo deve ser >= 1")
    if args.age[0] <= 0 or args.age[1] > 100:
        print("Idades inválidas")
    if args.age[0] > args.age[1]:
        print("Idade mínima deve ser maior que idade máxima")
    if len(args.age) != 2:
        print("Apenas 2 argumentos para as idades")
    else:    
        main(args.mp, args.age, args.max, args.toDB, args.each)
        
        
    

