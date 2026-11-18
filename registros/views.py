from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Ocorrencia, StatusOcorrencia, CategoriaOcorrencia
from .forms import OcorrenciaForm
from acompanhamento.models import HistoricoAlteracao
from usuarios.decorators import professor_required


@login_required
@professor_required
def nova_ocorrencia_view(request):
    """
    Permite que o professor (ou admin) registre uma nova ocorrência escolar.
    O status inicial é sempre REGISTRADA e o autor é request.user.
    """
    if request.method == 'POST':
        form = OcorrenciaForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                ocorrencia = form.save(commit=False)
                ocorrencia.professor = request.user
                ocorrencia.status = StatusOcorrencia.REGISTRADA
                ocorrencia.save()

                # Auditoria no HistoricoAlteracao
                HistoricoAlteracao.objects.create(
                    usuario=request.user,
                    ocorrencia=ocorrencia,
                    acao_realizada='Registro Inicial da Ocorrência',
                    descricao_alteracao=f"Ocorrência #{ocorrencia.id} registrada pelo professor {request.user.nome}."
                )

            messages.success(
                request,
                f"Ocorrência #{ocorrencia.id} de {ocorrencia.aluno.nome} registrada com sucesso!"
            )
            return redirect('registros:minhas_ocorrencias')
        else:
            messages.error(request, "Por favor, corrija os erros no formulário abaixo.")
    else:
        form = OcorrenciaForm()

    return render(request, 'registros/nova_ocorrencia.html', {'form': form})


@login_required
@professor_required
def minhas_ocorrencias_view(request):
    """
    Lista as ocorrências registradas pelo professor logado com opções de filtro.
    (Se for administrador, permite visualizar todas).
    """
    user = request.user
    if user.is_admin:
        ocorrencias = Ocorrencia.objects.all()
    else:
        ocorrencias = Ocorrencia.objects.filter(professor=user)

    # Filtros opcionais via GET
    status_filtro = request.GET.get('status')
    categoria_filtro = request.GET.get('categoria')
    busca = request.GET.get('busca', '').strip()

    if status_filtro:
        ocorrencias = ocorrencias.filter(status=status_filtro)
    if categoria_filtro:
        ocorrencias = ocorrencias.filter(categoria_id=categoria_filtro)
    if busca:
        ocorrencias = ocorrencias.filter(
            matricula_turma__aluno__nome__icontains=busca
        ) | ocorrencias.filter(
            matricula_turma__aluno__matricula__icontains=busca
        )

    ocorrencias = ocorrencias.select_related(
        'matricula_turma__aluno',
        'matricula_turma__turma',
        'categoria',
        'professor'
    ).order_by('-data_ocorrencia')

    categorias = CategoriaOcorrencia.objects.filter(ativo=True)
    status_choices = StatusOcorrencia.choices

    return render(request, 'registros/minhas_ocorrencias.html', {
        'ocorrencias': ocorrencias,
        'categorias': categorias,
        'status_choices': status_choices,
        'status_selecionado': status_filtro,
        'categoria_selecionada': categoria_filtro,
        'busca': busca,
    })
