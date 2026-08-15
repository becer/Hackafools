from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path(
        "api/tarefa/criar/",
        views.criar_tarefa,
        name="criar"
    ),

    path(
        "api/tarefa/consultar/<uuid:task_id>/",
        views.consultar_tarefa,
        name="consultar"
    ),

    path(
        "api/colab/pegar/",
        views.pegar_proxima_tarefa,
        name="pegar"
    ),

    path(
        "api/colab/resultado/",
        views.enviar_resultado,
        name="resultado"
    ),
]