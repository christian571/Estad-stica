from django.urls import path
from .views import index, pagina_calculadora, pagina_radiacion, calcular_estadisticas, calcular_radiacion, pagina_ayuda

urlpatterns = [
    path('', index, name='index'),  
    path('calculadora/', pagina_calculadora, name='pagina_calculadora'),
    path('radiacion/', pagina_radiacion, name='pagina_radiacion'),
    path('api/calcular/', calcular_estadisticas, name='calcular_estadisticas'),
    path('api/calcular_radiacion/', calcular_radiacion, name='calcular_radiacion'),
    path('ayuda/', pagina_ayuda, name='ayuda'),  # Ruta para la página de ayuda
]
