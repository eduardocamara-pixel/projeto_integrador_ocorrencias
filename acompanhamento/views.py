from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.utils.dateparse import parse_date
from registros.models import Ocorrencia, StatusOcorrencia, CategoriaOcorrencia
from turmas.models import Turma
from .models import Acompanhamento, HistoricoAlteracao
from .forms import AcompanhamentoForm, AlterarStatusForm
from usuarios.decorators import coordenacao_required


@login_required
@coordenacao_required
def painel_triagem_view(request):
    """
    Painel de Gestão e Triagem da Coordenação Pedagógica (RF09 e RF13).
    Permite visualizar a fila de ocorrências por ciclo de vida, aplicar filtros
    multidimensionais e identificar rapidamente casos que requerem atenção prioritária.
    """
    status_filtro = request.GET.get('status', '')
    categoria_filtro = request.GET.get('categoria', '')
    turma_filtro = request.GET.get('turma', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
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
    if turma_filtro:
        ocorrencias = ocorrencias.filter(matricula_turma__turma_id=turma_filtro)
    if data_inicio:
        d_ini = parse_date(data_inicio)
        if d_ini:
            ocorrencias = ocorrencias.filter(data_ocorrencia__date__gte=d_ini)
    if data_fim:
        d_fim = parse_date(data_fim)
        if d_fim:
            ocorrencias = ocorrencias.filter(data_ocorrencia__date__lte=d_fim)
    if busca:
        ocorrencias = ocorrencias.filter(
            matricula_turma__aluno__nome__icontains=busca
        ) | ocorrencias.filter(
            matricula_turma__aluno__matricula__icontains=busca
        ) | ocorrencias.filter(
            professor__nome__icontains=busca
        )

    ocorrencias = ocorrencias.order_by('-data_ocorrencia')

    # Contadores para as abas/métricas em tempo real
    total_registradas = Ocorrencia.objects.filter(status=StatusOcorrencia.REGISTRADA).count()
    total_em_analise = Ocorrencia.objects.filter(status=StatusOcorrencia.EM_ANALISE).count()
    total_em_acompanhamento = Ocorrencia.objects.filter(status=StatusOcorrencia.EM_ACOMPANHAMENTO).count()
    total_encaminhadas = Ocorrencia.objects.filter(status=StatusOcorrencia.ENCAMINHADA).count()
    total_concluidas = Ocorrencia.objects.filter(status=StatusOcorrencia.CONCLUIDA).count()

    # Identificação de ocorrências pendentes há mais de 48h sem acolhimento
    limite_48h = timezone.now() - timedelta(hours=48)
    total_atrasadas_48h = Ocorrencia.objects.filter(
        status=StatusOcorrencia.REGISTRADA,
        data_registro__lte=limite_48h
    ).count()

    turmas = Turma.objects.filter(ativa=True).order_by('-ano_letivo', 'nome')
    categorias = CategoriaOcorrencia.objects.filter(ativo=True).order_by('nome')

    return render(request, 'acompanhamento/painel_triagem.html', {
        'ocorrencias': ocorrencias,
        'turmas': turmas,
        'categorias': categorias,
        'status_choices': StatusOcorrencia.choices,
        'status_selecionado': status_filtro,
        'categoria_selecionada': categoria_filtro,
        'turma_selecionada': turma_filtro,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'busca': busca,
        'total_registradas': total_registradas,
        'total_em_analise': total_em_analise,
        'total_em_acompanhamento': total_em_acompanhamento,
        'total_encaminhadas': total_encaminhadas,
        'total_concluidas': total_concluidas,
        'total_atrasadas_48h': total_atrasadas_48h,
        'limite_48h': limite_48h,
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
