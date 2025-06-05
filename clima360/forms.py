from django import forms
from .models import CidadeDisponivies, MesesDisponiveis, AnosDisponiveis

class ComparacaoForm(forms.Form):
    cidadesEcolhas = [(cidade[0], cidade[0]) for cidade in CidadeDisponivies]
    
    medidaEscolhas = [
        ('temperatura', 'Temperatura Média (tavg)'),
        ('precipitacao', 'Precipitação (prcp)')
    ]

    cidade = forms.ChoiceField(choices=cidadesEcolhas, label="Cidade")
    mes = forms.ChoiceField(choices=MesesDisponiveis, label="Mês de Referência")
    ano1 = forms.ChoiceField(choices=AnosDisponiveis, label="Primeiro Ano")
    ano2 = forms.ChoiceField(choices=AnosDisponiveis, label="Segundo Ano")
    medida = forms.ChoiceField(choices=medidaEscolhas, label="Tipo de Medida Climática")

    def clean(self):
        LimparData = super().clean()
        ano1 = LimparData.get("ano1")
        ano2 = LimparData.get("ano2")

        if ano1 and ano2 and ano1 == ano2:
            raise forms.ValidationError("Os anos de comparação devem ser diferentes.")
        return LimparData