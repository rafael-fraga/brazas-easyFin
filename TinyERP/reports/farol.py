from datetime import datetime
import pandas as pd
import json, requests

tokens = json.loads(open('./reports/tokens.json').read())

class Inads:

    def __init__(self, bu):
        self.token = tokens[bu]
        self.bu = bu
        self.dia = datetime.today().strftime('%d/%m/%Y')
        url = 'https://api.tiny.com.br/api2/contas.receber.pesquisa.php'
        
        data = {'token': self.token,
                'formato': 'json',
                'data_fim_vencimento': self.dia,
                'situacao': 'aberto'}
        self.aberto = [x['conta'] for x in requests.post(url, data).json()['retorno']['contas']]

        data = {'token': self.token,
                'formato': 'json',
                'data_fim_vencimento': self.dia,
                'situacao': 'parcial'}
        self.parcial = [x['conta'] for x in requests.post(url, data).json()['retorno']['contas']]

        self.list = self.aberto + self.parcial
        
    def raw(self):
        return self.list

    def df(self,bu):
        self.table = pd.DataFrame(Inads(bu).list)
        self.table.drop(['id', 'historico', 'numero_banco', 'numero_doc',
        'serie_doc', 'data_emissao'], axis=1, inplace=True)
        for i, cliente in enumerate(self.table['nome_cliente']):
            for forbiden in ['ls', 'marcella', 'bh', 'rj', 'brazas']:    
                if forbiden in cliente.casefold():
                    self.table.drop(i, inplace=True)
                    break
        self.table.reset_index(inplace=True, drop=True)


        return self.table



