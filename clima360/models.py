from django.db import models

TiposMedidas = [
    ('1', 'Temperatura'),
    ('2', 'Pluviosidade'),
]

AnosDisponiveis = [(ano, str(ano)) for ano in range(2016, 2025)]

MesesDisponiveis = [
    ('01', 'Janeiro'),
    ('02', 'Fevereiro'),
    ('03', 'Março'),
    ('04', 'Abril'),
    ('05', 'Maio'),
    ('06', 'Junho'),
    ('07', 'Julho'),
    ('08', 'Agosto'),
    ('09', 'Setembro'),
    ('10', 'Outubro'),
    ('11', 'Novembro'),
    ('12', 'Dezembro'),
]

CidadeDisponivies = [
    ('Americana', (-22.7390, -47.3313)),
    ('Santa Bárbara d\'Oeste', (-22.7556, -47.4141)),
    ('Nova Odessa', (-22.7834, -47.2954)),
    ('Sumaré', (-22.8204, -47.2730)),
    ('Hortolândia', (-22.8529, -47.2215)),
    ('Limeira', (-22.5648, -47.4015)),
    ('Piracicaba', (-22.7338, -47.6476)),
    ('Campinas', (-22.9099, -47.0626)),
]

class ComparacaoClimatica(models.Model):
    medida = models.CharField(max_length=50, choices=TiposMedidas)
    cidade = models.CharField(max_length=50, choices=[(cidade[0], cidade[0]) for cidade in CidadeDisponivies])
    mes = models.CharField(max_length=2, choices=MesesDisponiveis)
    ano1 = models.IntegerField(choices=AnosDisponiveis)
    ano2 = models.IntegerField(choices=AnosDisponiveis)
    resultadoDispersao = models.JSONField(null=True, blank=True)

    dataConsulta = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.medida} - {self.cidade} - {self.mes} ({self.ano1} vs {self.ano2})"
