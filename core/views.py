from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
import json
from registros.models import Ocorrencia, StatusOcorrencia, CategoriaOcorrencia
from alunos.models import Aluno
from turmas.models import Turma


@login_required
def home_view(request):
    """
    Página inicial e Dashboard analítico com indicadores básicos do SIGOE (RF09).
    Apresenta métricas consolidadas, gráficos dinâmicos (Chart.js) e atalhos contextuais.
    """
    user = request.user

    total_ocorrencias = Ocorrencia.objects.count()
    ocorrencias_concluidas = Ocorrencia.objects.filter(status=StatusOcorrencia.CONCLUIDA).count()
    ocorrencias_em_aberto = total_ocorrencias - ocorrencias_concluidas
    taxa_resolucao = round((ocorrencias_concluidas / total_ocorrencias * 100), 1) if total_ocorrencias > 0 else 100

    # Dados para o gráfico de Status do Ciclo de Vida
    status_labels = ['Registrada', 'Em Análise', 'Em Acompanhamento', 'Encaminhada', 'Concluída']
    status_data = [
        Ocorrencia.objects.filter(status=StatusOcorrencia.REGISTRADA).count(),
        Ocorrencia.objects.filter(status=StatusOcorrencia.EM_ANALISE).count(),
        Ocorrencia.objects.filter(status=StatusOcorrencia.EM_ACOMPANHAMENTO).count(),
        Ocorrencia.objects.filter(status=StatusOcorrencia.ENCAMINHADA).count(),
        ocorrencias_concluidas,
    ]

    # Dados para o gráfico de Categorias
    top_categorias = list(
        CategoriaOcorrencia.objects.annotate(
            total=Count('ocorrencias')
        ).filter(total__gt=0).order_by('-total')[:6].values('nome', 'total')
    )
    cat_labels = [item['nome'] for item in top_categorias]
    cat_data = [item['total'] for item in top_categorias]

    # Dados para o gráfico de Ocorrências por Turma
    top_turmas = list(
        Turma.objects.filter(ativa=True).annotate(
            total=Count('matriculas__ocorrencias')
        ).filter(total__gt=0).order_by('-total')[:6].values('nome', 'total')
    )
    turma_labels = [item['nome'] for item in top_turmas]
    turma_data = [item['total'] for item in top_turmas]

    context = {
        'total_ocorrencias': total_ocorrencias,
        'ocorrencias_concluidas': ocorrencias_concluidas,
        'ocorrencias_em_aberto': ocorrencias_em_aberto,
        'taxa_resolucao': taxa_resolucao,
        'total_alunos': Aluno.objects.filter(ativo=True).count(),
        'total_turmas': Turma.objects.filter(ativa=True).count(),
        # Gráficos Chart.js
        'status_labels_json': json.dumps(status_labels),
        'status_data_json': json.dumps(status_data),
        'cat_labels_json': json.dumps(cat_labels),
        'cat_data_json': json.dumps(cat_data),
        'turma_labels_json': json.dumps(turma_labels),
        'turma_data_json': json.dumps(turma_data),
    }

    if user.is_professor:
        # Estatísticas contextuais do Professor
        context['minhas_ocorrencias_qtd'] = Ocorrencia.objects.filter(professor=user).count()
        context['ultimas_ocorrencias'] = Ocorrencia.objects.filter(professor=user).select_related(
            'matricula_turma__aluno', 'matricula_turma__turma', 'categoria'
        )[:6]
    else:
        # Estatísticas da Coordenação / Administrador
        context['pendentes_analise_qtd'] = Ocorrencia.objects.filter(status=StatusOcorrencia.REGISTRADA).count()
        context['em_acompanhamento_qtd'] = Ocorrencia.objects.filter(status=StatusOcorrencia.EM_ACOMPANHAMENTO).count()
        context['ultimas_ocorrencias'] = Ocorrencia.objects.select_related(
            'matricula_turma__aluno', 'matricula_turma__turma', 'professor', 'categoria'
        )[:6]

    return render(request, 'core/home.html', context)


@login_required
def roadmap_view(request):
    """
    Interface de Funcionalidades Futuras e Evolução do SIGOE.
    Apresenta os módulos e extensões do sistema planejados para o ecossistema educacional.
    """
    return render(request, 'core/roadmap.html')
