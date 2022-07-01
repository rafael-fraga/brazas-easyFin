import pandas as pd
from random import randint
import os

def latin2float(latin_value):
    return float(latin_value.replace('.', '').replace(',', '.'))

def safra_processing(bu, dia):


    if bu == 'rj':
        extrato = None
    else:
        file = open('./extratos/safra-' + bu + '.txt', encoding='utf-8').read().splitlines()[1:]
        file = [[x[:5] + dia[-5:], x[5:]] for x in file]
        file
        ops = [x[1].split()[0] for x in file]

        for i, op in enumerate(ops):
            if op == 'SALDO':
                ops[i] = 'S'
            elif op in ['ANTECIPACAO', 'RESUMO', 'RESGATE']:
                ops[i] = 'C'
            elif op in ['TARIFA', 'APLICACAO', 'PACOTE', 'PAGAMENTO']:
                ops[i] = 'D'
            elif op == 'PIX':
                if '-' in file[i][1]:
                    ops[i] = 'D'
                else:
                    ops[i] = 'C'
                    
        valor = [x[1].split()[-1] for x in file]
        valor = [x[1].split(ops[x[0]])[1] for x in enumerate(valor)]

        historico = [str(x[1][1].split(valor[x[0]])[0][:-2]) for x in enumerate(file)]
        extrato_iso = pd.DataFrame(file)
        extrato_iso['ops'] = ops
        extrato_iso[2] = pd.to_numeric(valor)
        extrato_iso[1] = historico
        extrato_iso = extrato_iso[extrato_iso[0] == dia]
        extrato_iso[4] = ['Taxas' if 'TARIFA' in x else '' for x in extrato_iso[1]]
        extrato_iso[4] = ['Taxas' if 'PACOTE PJ' in x else '' for x in extrato_iso[1]]
        extrato_iso[3] = ''
        extrato_iso = extrato_iso.drop_duplicates(1)
        extrato_iso

        antec = pd.read_excel('./extratos/antec-' + bu + '.xlsx').iloc[::-1]
        antec = antec.T.set_index(5, drop=True).T.drop([0,1,2,3,4])
        antec.columns = antec.columns.str.casefold()
        antec['valor bruto da venda'] = [latin2float(x.split('R$ ')[1]) for x in antec['valor bruto da venda']]
        antec = antec.T.reindex(['data do pagamento', 'bandeira', 'valor bruto da venda']).T
        antec.columns = range(3)
        antec[1] = ['Antecipação Crédito ' + x for x in antec[1]]
        antec = antec[antec[0] == dia]
        antec[4] = ['Eventos' if x > 500 else '' for x in antec[2]]
        antec[3] = ''

        vendas = pd.read_excel('./extratos/vendas-' + bu + '.xlsx').iloc[::-1]
        vendas = vendas.T.set_index(5, drop=True).T.drop([0,1,2,3,4])
        vendas = vendas[vendas['Modalidade'] == 'Débito']
        vendas = vendas.T.reindex(['Data da Venda', 'Bandeira / Arranjo', 'Valor Bruto da Venda']).T
        vendas.columns = range(3)
        vendas[1] = ['Venda Débito ' + x for x in vendas[1]]
        vendas[2] = [latin2float(x.split()[-1]) for x in vendas[2]]
        vendas = vendas[vendas[0] == dia]
        vendas[4] = ['Eventos' if x > 500 else '' for x in vendas[2]]
        vendas[3] = ''

        if len(extrato_iso) > 0:
            extrato = pd.concat([extrato_iso.drop('ops', axis=1), antec, vendas])

            extrato = extrato.T.reindex([0,1,2,3,4]).T

            if len(antec) > 0:
                extrato = pd.concat([extrato, pd.DataFrame([dia, 'Taxas Antecipação', -(antec[2].sum() - extrato[extrato[1].str.contains('ANTECIPACAO')][2].sum()), 'D', 'Taxas']).T])
                extrato = extrato.drop(extrato[extrato[1].str.contains('RVSAFRAPAY')].index).reset_index(drop=True)
            if len(vendas) > 0:
                extrato = pd.concat([extrato, pd.DataFrame([dia, 'Taxas Débito', -(vendas[2].sum() - extrato[extrato[1].str.contains('RESUMO')][2].sum()), 'D', 'Taxas']).T])
                extrato = extrato.drop(extrato[extrato[1].str.contains('RESUMO')].index).reset_index(drop=True)
            saldo = extrato.reset_index().iloc[0][2]
            extrato = extrato.drop(extrato[extrato[1].str.contains('SALDO')].index).reset_index(drop=True)

            extrato[3] = ['D' if x < 0 else 'C' for x in extrato[2]]
            extrato[2] = [x*-1 if x < 0 else x for x in extrato[2]]

            extrato[2] = [str(x).replace('.', ',') for x in extrato[2]]


            extrato.columns = ['data', 'historico', 'valor', 'tipo', 'categoria']
            extrato = pd.concat([pd.DataFrame(columns=['data', 'categoria', 'historico', 'tipo', 'valor', 'id', 'contato',
                    'cnpj', 'marcadores', 'conta_de_destino', 'no_documento']), extrato], ignore_index=True)
            extrato['conta_de_destino'] = 'Banco Safra'
            extrato['marcadores'] = 'auto'
            extrato['historico'] = extrato['historico'].str.title()
            extrato.to_csv('./output/safra-'+ bu + '.csv', index=False)
        else:
            extrato = None
            


    return extrato