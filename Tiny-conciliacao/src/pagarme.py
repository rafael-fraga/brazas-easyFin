import pandas as pd
import os

def unifloat(latin_value):
    return float(latin_value.replace('.', '').replace(',', '.'))

def pagarme_processing(bu, dia):
    if bu == 'ls':

        extrato = None
    else:
        extrato = pd.read_csv('./extratos/pagarme-' + bu + '.csv')
        extrato.drop(['Entrada líquida', 'Saída líquida', 'Taxa de operação', 'Taxa de antecipação'], axis=1, inplace=True)

        extrato['Data da operação'] = [x.split()[0] for x in extrato['Data da operação']]
        extrato = extrato[extrato['Data da operação'] == dia]


        if len(extrato) > 0:

        

            for col in ['Taxa total da operação',
                'Entrada bruta', 'Saída bruta']:
                extrato[col] = [unifloat(x) for x in extrato[col]]

            extrato['historico'] = ''
            for i, row in enumerate(extrato.index):
                hist = ''
                for col in ['Tipo da operação', 'Id da operação',
                'Descrição da operação', 'Id da transação', 'Parcela',
                'Método de pagamento']:
                    hist += ' ' + str(extrato[col].iloc[i])
                extrato['historico'].iloc[i] = hist
            extrato = extrato.drop(['Tipo da operação', 'Id da operação',
                'Descrição da operação', 'Id da transação', 'Parcela',
                'Método de pagamento'], axis=1)
            
            extrato['valor'] = extrato['Entrada bruta'] + extrato['Saída bruta']
            extrato.drop(['Entrada bruta', 'Saída bruta'], axis=1, inplace=True)
            extrato['tipo'] = ['D' if x < 0 else 'C' for x in extrato['valor']]
            extrato.loc['taxa'] = [dia,0,'Taxas',-extrato['Taxa total da operação'].sum(), 'D']
            extrato.drop(['Taxa total da operação', 'Data da operação'], axis=1, inplace=True)

            template = pd.DataFrame(columns=['data', 'categoria', 'historico', 'tipo', 'valor', 'id', 'contato',
                    'cnpj', 'marcadores', 'conta_de_destino', 'no_documento'])
            extrato = pd.concat([template, extrato], axis=0)

            extrato['conta_de_destino'] = 'PAGAR.ME'
            extrato['marcadores'] = 'auto'
            extrato['valor'] = [str(x).replace(',', '').replace('-', '').replace('.', ',') for x in extrato['valor']]
            extrato['data'] = dia
            extrato.to_csv('./output/pagarme-' + bu + '.csv', index=False)
        else:
            extrato = None

    return extrato