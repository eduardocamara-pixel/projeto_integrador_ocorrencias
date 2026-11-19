from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.dateparse import parse_date
from registros.models import Ocorrencia, StatusOcorrencia, CategoriaOcorrencia
from turmas.models import Turma
from alunos.models import Aluno
from usuarios.decorators import coordenacao_required, professor_ou_coordenacao_required


@login_required
@professor_ou_coordenacao_required
def painel_relatorios_view(request):
    """
    Central de Emissão de Relatórios Oficiais e Pedagógicos do SIGOE (RF10).
    Apresenta os tipos de relatórios disponíveis para exportação e impressão.
    """
    turmas = Turma.objects.filter(ativa=True).order_by('-ano_letivo', 'nome')
    categorias = CategoriaOcorrencia.objects.all().order_by('nome')

    context = {
        'turmas': turmas,
        'categorias': categorias,
        'total_ocorrencias': Ocorrencia.objects.count(),
        'total_concluidas': Ocorrencia.objects.filter(status=StatusOcorrencia.CONCLUIDA).count(),
        'total_alunos': Aluno.objects.filter(ativo=True).count(),
    }
    return render(request, 'relatorios/painel_relatorios.html', context)


@login_required
@coordenacao_required
def relatorio_geral_view(request):
    """
    Relatório Geral Consolidado para Gestão Escolar e Secretarias de Educação (RF10).
    Formatado com padrão A4 para impressão oficial e arquivo institucional.
    """
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    turma_id = request.GET.get('turma', '')
    categoria_id = request.GET.get('categoria', '')
    status_filtro = request.GET.get('status', '')

    ocorrencias = Ocorrencia.objects.all().select_related(
        'matricula_turma__aluno',
        'matricula_turma__turma',
        'categoria',
        'professor'
    ).order_by('data_ocorrencia')

    turma_selecionada = None
    if turma_id:
        ocorrencias = ocorrencias.filter(matricula_turma__turma_id=turma_id)
        turma_selecionada = Turma.objects.filter(id=turma_id).first()

    categoria_selecionada = None
    if categoria_id:
        ocorrencias = ocorrencias.filter(categoria_id=categoria_id)
        categoria_selecionada = CategoriaOcorrencia.objects.filter(id=categoria_id).first()

    if status_filtro:
        ocorrencias = ocorrencias.filter(status=status_filtro)

    if data_inicio:
        d_ini = parse_date(data_inicio)
        if d_ini:
            ocorrencias = ocorrencias.filter(data_ocorrencia__date__gte=d_ini)

    if data_fim:
        d_fim = parse_date(data_fim)
        if d_fim:
            ocorrencias = ocorrencias.filter(data_ocorrencia__date__lte=d_fim)

    # Estatísticas consolidadas do filtro
    total = ocorrencias.count()
    total_concluidas = ocorrencias.filter(status=StatusOcorrencia.CONCLUIDA).count()
    total_em_aberto = total - total_concluidas
    taxa_resolucao = round((total_concluidas / total * 100), 1) if total > 0 else 100

    context = {
        'ocorrencias': ocorrencias,
        'total': total,
        'total_concluidas': total_concluidas,
        'total_em_aberto': total_em_aberto,
        'taxa_resolucao': taxa_resolucao,
        'turma_selecionada': turma_selecionada,
        'categoria_selecionada': categoria_selecionada,
        'status_selecionado': status_filtro,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'data_emissao': timezone.now(),
    }
    return render(request, 'relatorios/relatorio_geral.html', context)


@login_required
@coordenacao_required
def relatorio_turma_view(request, pk):
    """
    Relatório Diagnóstico por Turma Escolar.
    Mapeia os principais focos de indisciplina e o histórico de intervenções da turma.
    """
    turma = get_object_or_404(Turma, pk=pk)

    ocorrencias = Ocorrencia.objects.filter(
        matricula_turma__turma=turma
    ).select_related(
        'matricula_turma__aluno',
        'categoria',
        'professor'
    ).order_by('-data_ocorrencia')

    # Distribuição por categoria na turma
    categorias_dist = list(
        CategoriaOcorrencia.objects.filter(
            ocorrencias__matricula_turma__turma=turma
        ).annotate(
            qtd=Count('ocorrencias')
        ).order_by('-qtd')
    )

    context = {
        'turma': turma,
        'ocorrencias': ocorrencias,
        'total_ocorrencias': ocorrencias.count(),
        'total_concluidas': ocorrencias.filter(status=StatusOcorrencia.CONCLUIDA).count(),
        'total_em_aberto': ocorrencias.exclude(status=StatusOcorrencia.CONCLUIDA).count(),
        'categorias_dist': categorias_dist,
        'data_emissao': timezone.now(),
    }
    return render(request, 'relatorios/relatorio_turma.html', context)


@login_required
@professor_ou_coordenacao_required
def ficha_ocorrencia_impressao_view(request, pk):
    """
    Ficha Oficial e Ata de Atendimento da Ocorrência Escolar (RF10).
    Documento para arquivo impresso e coleta de assinaturas dos envolvidos
    (Discente, Responsável Legal, Professor Relator e Coordenação Pedagógica).
    """
    ocorrencia = get_object_or_404(
        Ocorrencia.objects.select_related(
            'matricula_turma__aluno',
            'matricula_turma__turma',
            'categoria',
            'professor'
        ),
        pk=pk
    )

    # Restrição: se for professor comum, só visualiza ocorrência que registrou
    if request.user.is_professor and not (request.user.is_admin or request.user.is_coordenacao):
        if ocorrencia.professor != request.user:
            return render(request, '403.html', {'perfis_permitidos': ['Coordenação Pedagógica']}, status=403)

    acompanhamentos = ocorrencia.acompanhamentos.select_related('responsavel').order_by('data_registro')
    historico = ocorrencia.historico_alteracoes.select_related('usuario').order_by('data_hora')

    context = {
        'oc': ocorrencia,
        'acompanhamentos': acompanhamentos,
        'historico': historico,
        'data_emissao': timezone.now(),
    }
    return render(request, 'relatorios/ficha_ocorrencia.html', context)
