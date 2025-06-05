import pandas as pd
import numpy as np


def calcular_metricas_de_serie(lista_dados):
    dados_validos = [x for x in lista_dados if x is not None and not (isinstance(x, float) and np.isnan(x))]

    if not dados_validos: # Se a lista original era vazia ou só tinha None/NaN
        return {'media': None, 'desvioPadrao': None, 'variancia': None, 'count': 0}

    serie = pd.Series(dados_validos)
    
    media = serie.mean()
    desvio_padrao = serie.std(ddof=0)
    variancia = serie.var(ddof=0)
    
    return {
        'media': float(media) if not pd.isna(media) else None,
        'desvioPadrao': float(desvio_padrao) if not pd.isna(desvio_padrao) else None,
        'variancia': float(variancia) if not pd.isna(variancia) else None,
        'count': len(serie)
    }
    
def calculoMedidasDispersao(dados_serie1, dados_serie2):
    metricas_serie1 = calcular_metricas_de_serie(dados_serie1)
    metricas_serie2 = calcular_metricas_de_serie(dados_serie2)

    diferencas = {}
    for key in ['media', 'desvioPadrao', 'variancia']:
        if metricas_serie1[key] is not None and metricas_serie2[key] is not None:
            diferencas[key] = metricas_serie2[key] - metricas_serie1[key]
        else:
            diferencas[key] = None
            
    return metricas_serie1, metricas_serie2, diferencas
