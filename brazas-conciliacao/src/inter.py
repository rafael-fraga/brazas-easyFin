import pandas as pd
import re, os

def inter_processing(bu, dia):

    file = [x.split(';') for x in open('./extratos/inter-' + bu + '.csv', encoding='utf-8').read().replace(' R$ ', '').replace(' -', '-').splitlines()]
    
    template = pd.DataFrame(columns=['data', 'categoria', 'historico', 'tipo', 'valor', 'id', 'contato',
        'cnpj', 'marcadores', 'conta_de_destino', 'no_documento'])
    
    extrato = pd.DataFrame(file[7:], columns=['data', 'historico', 'valor', 'saldo'])
    extrato = extrato[extrato['data'] == dia].reset_index(drop=True)
    extrato['marcadores'] = 'auto'
    extrato['conta_de_destino'] = 'Banco Inter'
    
    historicos = extrato['historico'].to_list()
    for i, historico in enumerate(historicos):
        historicos[i] = [re.sub(r'[^a-zA-Z]', '', x).title() for x in historico.split()]
        historicos[i] = ' '.join(historicos[i])
        for expression in ['Cp', 'Pix Enviado Interno', 'Transferencia A Debito', 'Pix Recebido Interno']:
            historicos[i] = historicos[i].split(expression)[-1]
    extrato['historico'] = historicos

    extrato['tipo'] = ['D' if '-' in x else 'C' for x in extrato['valor']]
    extrato['valor'] = extrato['valor'].str.replace('-', '')
    
    extrato = pd.concat([template, extrato.drop('saldo', axis=1)])
    extrato.to_csv('./output/inter-' + bu + '.csv', index=False)

    return extrato