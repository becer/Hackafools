from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Tarefa
import json
# Create your views here.
def home(request):
    return render(request, "index.html")


@csrf_exempt
def criar_tarefa(request):

    if request.method != 'POST':
        return JsonResponse(
            {"erro": "Método não permitido"},
            status=405
        )

    try:

        audio = request.FILES.get("audio")

        if not audio:
            return JsonResponse(
                {"erro": "Nenhum áudio foi enviado"},
                status=400
            )

        dados = {
            "nome_arquivo": audio.name,
            "tipo": audio.content_type,
            "tamanho": audio.size
        }

        tarefa = Tarefa.objects.create(

            dados_entrada=dados,

            audio=audio

        )

        return JsonResponse({

            "task_id": str(tarefa.id),

            "status": tarefa.status,

            "arquivo": tarefa.audio.name

        })

    except Exception as e:

        return JsonResponse({

            "erro": str(e)

        }, status=500)

def consultar_tarefa(request, task_id):
    try:
        tarefa = Tarefa.objects.get(id=task_id)
        if tarefa.status == 'done':
            return JsonResponse({"status": "done", "resultado": tarefa.resultado})
        elif tarefa.status == 'failed':
            return JsonResponse({"status": "failed", "erro": "Falha no processamento"})
        else:
            return JsonResponse({"status": tarefa.status})
    except Tarefa.DoesNotExist:
        return JsonResponse({"erro": "Tarefa não encontrada"}, status=404)

@csrf_exempt
def pegar_proxima_tarefa(request):
    if request.method != 'GET':
        return JsonResponse(
            {"erro": "Método não permitido"},
            status=405
        )

    tarefa = (
        Tarefa.objects
        .filter(status='pending')
        .order_by('criado_em')
        .first()
    )

    if not tarefa:
        return JsonResponse({
            "mensagem": "Nenhuma tarefa no momento"
        })

    # Verifica se existe arquivo
    if not tarefa.audio:
        tarefa.status = "failed"
        tarefa.resultado = {
            "erro": "Tarefa não possui arquivo de áudio"
        }
        tarefa.save()

        return JsonResponse({
            "erro": "A tarefa encontrada não possui áudio",
            "task_id": str(tarefa.id)
        }, status=400)

    # Só marca como processing depois de confirmar
    # que existe áudio
    tarefa.status = 'processing'
    tarefa.save()

    return JsonResponse({

        "task_id": str(tarefa.id),

        "dados": tarefa.dados_entrada,

        "audio_url": tarefa.audio.url

    })

@csrf_exempt
def enviar_resultado(request):

    print("\n========== ENVIAR RESULTADO ==========")
    print("Método:", request.method)

    if request.method != 'POST':
        return JsonResponse(
            {"erro": "Método não permitido"},
            status=405
        )

    try:
        data = json.loads(request.body)

        print("Dados recebidos:")
        print(data)

        task_id = data.get("task_id")
        resultado = data.get("resultado")
        erro = data.get("erro")

        print("TASK ID RECEBIDO:", task_id)
        print("RESULTADO RECEBIDO:", resultado)
        print("ERRO:", erro)

        if not task_id:
            return JsonResponse(
                {"erro": "task_id não enviado"},
                status=400
            )

        tarefa = Tarefa.objects.get(id=task_id)

        print("TAREFA ENCONTRADA:", tarefa.id)
        print("STATUS ANTES:", tarefa.status)

        if erro:

            tarefa.status = 'failed'

            tarefa.resultado = {
                "erro": erro
            }

        else:

            tarefa.status = 'done'

            tarefa.resultado = resultado

        tarefa.save()

        # Recarrega do banco para confirmar
        tarefa.refresh_from_db()

        print("STATUS DEPOIS:", tarefa.status)
        print("RESULTADO NO BANCO:", tarefa.resultado)
        print("====================================\n")

        return JsonResponse({
            "status": "ok",
            "task_id": str(tarefa.id),
            "status_tarefa": tarefa.status,
            "resultado": tarefa.resultado
        })

    except Tarefa.DoesNotExist:

        print("TAREFA NÃO ENCONTRADA:", task_id)

        return JsonResponse(
            {
                "erro": "Tarefa não encontrada",
                "task_id": task_id
            },
            status=404
        )

    except Exception as e:

        print("ERRO:", str(e))

        return JsonResponse(
            {
                "erro": str(e)
            },
            status=500
        )