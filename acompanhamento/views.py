from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from registros.models import Ocorrencia, StatusOcorrencia, CategoriaOcorrencia
from .models import Acompanhamento, HistoricoAlteracao
from .forms import AcompanhamentoForm, AlterarStatusForm
from usuarios.decorators import coordenacao_required


@login_required
@coordenacao_required
def painel_triagem_view(request):
    """
    Painel de triagem da Coordenação Pedagógica.
    Permite visualizar ocorrências divididas por status e aplicar filtros.
    """
    status_filtro = request.GET.get('status', '')
    categoria_filtro = request.GET.get('categoria', '')
    busca = request.GET.get('busca', '').strip()

    ocorrencias = Ocorrencia.objects.all().select_related(
        'matricula_turma__aluno',
        'matricula_turma__turma',
        'professor',
        'categoria'
    )

    if status_filtro:
        ocorrencias = ocorrencias.filter(status=status_filtro)
    if categoria_filtro:
        ocorrencias = ocorrencias.filter(categoria_id=categoria_filtro)
    if busca:
        ocorrencias = ocorrencias.filter(
            matricula_turma__aluno__nome__icontains=busca
        ) | ocorrencias.filter(
            matricula_turma__aluno__matricula__icontains=busca
        ) | ocorrencias.filter(
            professor__nome__icontains=busca
        )

    ocorrencias = ocorrencias.order_by('-data_ocorrencia')

    # Contadores para as abas/métricas
    total_registradas = Ocorrencia.objects.filter(status=StatusOcorrencia.REGISTRADA).count()
    total_em_analise = Ocorrencia.objects.filter(status=StatusOcorrencia.EM_ANALISE).count()
    total_em_acompanhamento = Ocorrencia.objects.filter(status=StatusOcorrencia.EM_ACOMPANHAMENTO).count()
    total_concluidas = Ocorrencia.objects.filter(status=StatusOcorrencia.CONCLUIDA).count()

    return render(request, 'acompanhamento/painel_triagem.html', {
        'ocorrencias': ocorrencias,
        'categorias': CategoriaOcorrencia.objects.filter(ativo=True),
        'status_choices': StatusOcorrencia.choices,
        'status_selecionado': status_filtro,
        'categoria_selecionada': categoria_filtro,
        'busca': busca,
        'total_registradas': total_registradas,
        'total_em_analise': total_em_analise,
        'total_em_acompanhamento': total_em_acompanhamento,
        'total_concluidas': total_concluidas,
    })


@login_required
@coordenacao_required
def detalhe_triagem_view(request, pk):
    """
    Exibe o prontuário completo de uma ocorrência:
    - Relato do professor
    - Histórico de acompanhamentos pedagógicos e intervenções
    - Trilha de auditoria LGPD
    - Formulário para registrar parecer ou ata de reunião
    - Formulário para tramitar o status da ocorrência
    """
    ocorrencia = get_object_or_404(
        Ocorrencia.objects.select_related(
            'matricula_turma__aluno',
            'matricula_turma__turma',
            'professor',
            'categoria'
        ),
        pk=pk
    )

    acompanhamentos = ocorrencia.acompanhamentos.select_related('responsavel').order_by('-data_registro')
    historico_alteracoes = ocorrencia.historico_alteracoes.select_related('usuario').order_by('-data_hora')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'novo_acompanhamento':
            acomp_form = AcompanhamentoForm(request.POST)
            if acomp_form.is_valid():
                with transaction.atomic():
                    novo_acomp = acomp_form.save(commit=False)
                    novo_acomp.ocorrencia = ocorrencia
                    novo_acomp.responsavel = request.user
                    novo_acomp.save()

                    # Auditoria
                    HistoricoAlteracao.objects.create(
                        usuario=request.user,
                        ocorrencia=ocorrencia,
                        acao_realizada=f"Registro de {novo_acomp.get_tipo_registro_display()}",
                        descricao_alteracao=f"Intervenção registrada por {request.user.nome}."
                    )

                messages.success(request, "Intervenção pedagógica registrada com sucesso!")
                return redirect('acompanhamento:detalhe_ocorrencia', pk=ocorrencia.id)

        elif action == 'mudar_status':
            status_form = AlterarStatusForm(request.POST)
            if status_form.is_valid():
                novo_status = status_form.cleaned_data['novo_status']
                justificativa = status_form.cleaned_data['justificativa']
                status_anterior = ocorrencia.get_status_display()

                with transaction.atomic():
                    ocorrencia.status = novo_status
                    ocorrencia.save()

                    # Auditoria
                    HistoricoAlteracao.objects.create(
                        usuario=request.user,
                        ocorrencia=ocorrencia,
                        acao_realizada=f"Alteração de Status para {ocorrencia.get_status_display()}",
                        descricao_alteracao=f"Status alterado de '{status_anterior}' para '{ocorrencia.get_status_display()}'. {justificativa}"
                    )

                messages.success(
                    request,
                    f"Status da ocorrência atualizado para '{ocorrencia.get_status_display()}' com sucesso!"
                )
                return redirect('acompanhamento:detalhe_ocorrencia', pk=ocorrencia.id)

    acomp_form = AcompanhamentoForm()
    status_form = AlterarStatusForm(initial={'novo_status': ocorrencia.status})

    return render(request, 'acompanhamento/detalhe_ocorrencia.html', {
        'ocorrencia': ocorrencia,
        'acompanhamentos': acompanhamentos,
        'historico_alteracoes': historico_alteracoes,
        'acomp_form': acomp_form,
        'status_form': status_form,
    })
