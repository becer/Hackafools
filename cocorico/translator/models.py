from django.db import models
import uuid


class Tarefa(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    dados_entrada = models.JSONField()

    audio = models.FileField(
        upload_to="audios/",
        null=True,
        blank=True
    )

    resultado = models.JSONField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pendente'),
            ('processing', 'Processando'),
            ('done', 'Concluído'),
            ('failed', 'Falha')
        ],
        default='pending'
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )