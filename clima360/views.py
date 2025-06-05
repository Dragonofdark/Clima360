from django.shortcuts import render, redirect
from django.http import HttpResponseServerError
from .models import ComparacaoClimatica, CidadeDisponivies, AnosDisponiveis, MesesDisponiveis
from .medidas import calculoMedidasDispersao
from datetime import datetime
import json
from .forms import ComparacaoForm
import requests 
import calendar

def inicio(request):
    return render(request, 'inicio.html')

def medida(request):
    opcoes_medida = [('temperatura', 'Temperatura'), ('precipitacao', 'Pluviosidade')]
    valores_validos = [opcao[0] for opcao in opcoes_medida]

    if request.method == 'POST':
        medida_selecionada = request.POST.get('medida')
        if medida_selecionada in valores_validos:
            request.session['medida_escolhida'] = medida_selecionada
            return redirect('cidades')
        else:
            return render(request, 'medida.html', {'tipos_medidas': opcoes_medida, 'erro': 'Seleção inválida.'})
    
    return render(request, 'medida.html', {'tipos_medidas': opcoes_medida})

def cidade(request):
    cidades_validas = [c[0] for c in CidadeDisponivies]
    if request.method == 'POST':
        cidade_selecionada = request.POST.get('cidade')
        if cidade_selecionada in cidades_validas:
            request.session['cidade_escolhida'] = cidade_selecionada
            return redirect('mes')
        else:
            return render(request, 'cidades.html', {'cidades': CidadeDisponivies, 'erro': 'Seleção inválida.'})

    return render(request, 'cidades.html', {'cidades': CidadeDisponivies})

def escolher_mes(request):
    meses_validos = [m[0] for m in MesesDisponiveis]
    if request.method == 'POST':
        mes_selecionado = request.POST.get('mes') 
        if mes_selecionado in meses_validos:
            request.session['mes_escolhido'] = mes_selecionado
            return redirect('anos')
        else:
            return render(request, 'escolher_mes.html', {'meses': MesesDisponiveis, 'erro': 'Seleção inválida.'})
    
    return render(request, 'escolher_mes.html', {'meses': MesesDisponiveis})

def compara_anos(request):
    anos_disponiveis = AnosDisponiveis
    anos_validos = [str(ano_tupla[0]) for ano_tupla in AnosDisponiveis]

    if request.method == 'POST':
        ano1_selecionado = request.POST.get('ano1')
        ano2_selecionado = request.POST.get('ano2')

        if not ano1_selecionado or not ano2_selecionado:
            return render(request, 'compara_anos.html', {
                'anos': anos_disponiveis,
                'erro': 'Ambos os anos devem ser selecionados.'
            })

        if ano1_selecionado not in anos_validos or \
           ano2_selecionado not in anos_validos:
            return render(request, 'compara_anos.html', {
                'anos': anos_disponiveis,
                'erro': 'Um ou ambos os anos selecionados são inválidos.'
            })

        if ano1_selecionado == ano2_selecionado:
            return render(request, 'compara_anos.html', {
                'anos': anos_disponiveis,
                'erro': 'Os anos de comparação devem ser diferentes.'
            })
            
        request.session['ano1_escolhido'] = ano1_selecionado
        request.session['ano2_escolhido'] = ano2_selecionado
        
        return redirect('resultados')
    
    else:
        return render(request, 'compara_anos.html', {'anos': anos_disponiveis})


def resultados(request):
    if request.method == 'POST':
        form = ComparacaoForm(request.POST)
        if form.is_valid():
            cidade_nome = form.cleaned_data['cidade']
            mes_str = form.cleaned_data['mes'] 
            ano1 = int(form.cleaned_data['ano1'])
            ano2 = int(form.cleaned_data['ano2'])
            medida_selecionada_form = form.cleaned_data['medida'] 

            try:
                mes_int = int(mes_str)
                if not (1 <= mes_int <= 12):
                    raise ValueError("Mês inválido")
            except ValueError:
                return render(request, 'resultados.html', {
                    'form': form,
                    'mensagem_erro': "Mês selecionado é inválido."
                })

            map_medida_form_to_model_id = {
                'temperatura': '1',
                'precipitacao': '2',
            }
            medida_id_modelo = map_medida_form_to_model_id.get(medida_selecionada_form)
            if not medida_id_modelo:
                return render(request, 'resultados.html', {
                    'form': form,
                    'mensagem_erro': f"Tipo de medida '{medida_selecionada_form}' inválido para salvar."
                })

            coord_dict = dict(CidadeDisponivies)
            lat, lon = coord_dict.get(cidade_nome, (None, None))
            if lat is None or lon is None:
                return HttpResponseServerError(f"Coordenadas não encontradas para a cidade: {cidade_nome}.")
            
            map_medida_to_openmeteo_var = {
                'temperatura': 'temperature_2m_mean',
                'precipitacao': 'precipitation_sum',
            }
            openmeteo_variable = map_medida_to_openmeteo_var.get(medida_selecionada_form)
            if not openmeteo_variable:
                return render(request, 'resultados.html', {
                    'form': form,
                    'mensagem_erro': f"Tipo de medida '{medida_selecionada_form}' não mapeado para a API Open-Meteo."
                })
            
            dados_diarios_por_ano = {} 

            for ano_atual in [ano1, ano2]:
                primeiro_dia_mes = 1
                try:
                    _, ultimo_dia_mes = calendar.monthrange(ano_atual, mes_int)
                except calendar.IllegalMonthError:
                     return render(request, 'resultados.html', {
                        'form': form,
                        'mensagem_erro': f"Mês/Ano inválido para obter dias: {mes_int}/{ano_atual}."
                    })

                start_date_str = f"{ano_atual}-{mes_str}-{str(primeiro_dia_mes).zfill(2)}"
                end_date_str = f"{ano_atual}-{mes_str}-{str(ultimo_dia_mes).zfill(2)}"
                
                openmeteo_url = (
                    f"https://archive-api.open-meteo.com/v1/archive?"
                    f"latitude={lat}&longitude={lon}"
                    f"&start_date={start_date_str}&end_date={end_date_str}"
                    f"&daily={openmeteo_variable}&timezone=America/Sao_Paulo" 
                )

                try:
                    response = requests.get(openmeteo_url, timeout=10)
                    response.raise_for_status() 
                    api_data = response.json()
                except requests.exceptions.RequestException as e:
                    return render(request, 'resultados.html', {
                        'form': form,
                        'mensagem_erro': f"Erro ao buscar dados da API Open-Meteo para {ano_atual}: {e}"
                    })
                
                if 'daily' in api_data and openmeteo_variable in api_data['daily']:
                    lista_dados_diarios = api_data['daily'][openmeteo_variable]
                    
                    if len(lista_dados_diarios) != ultimo_dia_mes:
                         print(f"DEBUG: Open-Meteo retornou {len(lista_dados_diarios)} dias, esperado {ultimo_dia_mes} para {mes_str}/{ano_atual}")
                         
                    dados_processados = []
                    for valor in lista_dados_diarios:
                        if valor is None:
                            dados_processados.append(None)
                        else:
                            try:
                                dados_processados.append(float(valor))
                            except (ValueError, TypeError):
                                dados_processados.append(None)
                    
                    dados_diarios_por_ano[str(ano_atual)] = dados_processados
                else:
                    dados_diarios_por_ano[str(ano_atual)] = []
        
            if not dados_diarios_por_ano.get(str(ano1)) or not dados_diarios_por_ano.get(str(ano2)):
                 return render(request, 'resultados.html', {
                        'form': form,
                        'mensagem_erro': "Não foi possível obter os dados diários para um ou ambos os períodos selecionados."
                    })
            
            metricas_ano1, metricas_ano2, diferencas_metricas = calculoMedidasDispersao(
                dados_diarios_por_ano[str(ano1)], 
                dados_diarios_por_ano[str(ano2)]
            )
            
            resultado_json_dispersao = {
                'ano1_metricas': metricas_ano1, 
                'ano2_metricas': metricas_ano2,
                'diferencas': diferencas_metricas
            }


            ComparacaoClimatica.objects.create(
                medida=medida_id_modelo,
                cidade=cidade_nome,
                mes=mes_str,
                ano1=ano1,
                ano2=ano2,
                resultadoDispersao=resultado_json_dispersao
            )
            
            nome_do_mes_display = dict(MesesDisponiveis).get(mes_str)
            session_keys_to_clear = ['medida_escolhida', 'cidade_escolhida', 'mes_escolhido', 'ano1_escolhido', 'ano2_escolhido']
            for key in session_keys_to_clear:
                if key in request.session:
                    del request.session[key]
            
            num_dias_no_mes_selecionado = calendar.monthrange(ano1, mes_int)[1]

            context = {
                'medida_selecionada': medida_selecionada_form.capitalize(),
                'cidade': cidade_nome,
                'mes_numero': mes_str,
                'mes_nome': nome_do_mes_display,
                'ano1': ano1,
                'ano2': ano2,
                
                'dados_diarios_ano1_json': json.dumps(dados_diarios_por_ano.get(str(ano1), [])),
                'dados_diarios_ano2_json': json.dumps(dados_diarios_por_ano.get(str(ano2), [])),
                'labels_dias_mes_json': json.dumps(list(range(1, num_dias_no_mes_selecionado + 1))),
                                
                'dispersao': resultado_json_dispersao, 
                'form': form,
                'comparacao_salva': True
            }
            return render(request, 'resultados.html', context)
        else: 
            return render(request, 'resultados.html', {'form': form, 'mensagem_erro': 'Dados do formulário inválidos.'})
    
    else:
        initial_data = {}
        if 'medida_escolhida' in request.session:
            initial_data['medida'] = request.session.get('medida_escolhida')
        if 'cidade_escolhida' in request.session:
            initial_data['cidade'] = request.session.get('cidade_escolhida')
        if 'mes_escolhido' in request.session:
            initial_data['mes'] = request.session.get('mes_escolhido')
        if 'ano1_escolhido' in request.session:
            initial_data['ano1'] = request.session.get('ano1_escolhido')
        if 'ano2_escolhido' in request.session:
            initial_data['ano2'] = request.session.get('ano2_escolhido')
        
        form = ComparacaoForm(initial=initial_data if initial_data else None)
        return render(request, 'resultados.html', {'form': form})