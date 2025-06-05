from django.contrib import admin
from clima360.models import ComparacaoClimatica

class ListaClimatica(admin.ModelAdmin):
    list_display = ('id', 'cidade', 'mes', 'ano1', 'ano2', 'resultadoDispersao')
    list_display_links = ('id', 'cidade')
    search_fields = ('cidade', 'mes')
    list_filter = ('cidade', 'mes')
    readonly_fields = ('resultadoDispersao', 'dataConsulta')
    list_per_page = 10

admin.site.register(ComparacaoClimatica, ListaClimatica)