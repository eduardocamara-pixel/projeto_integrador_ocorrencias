from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from registros.models import Ocorrencia, StatusOcorrencia
from alunos.models import Aluno
from turmas.models import Turma


@login_required
def home_view(request):
    """
    Página inicial / Painel principal do SIGOE.
    Apresenta resumo de acordo com o perfil do usuário logado (Professor, Coordenação, Admin).
    """
    user = request.user
    context = {
        'total_ocorrencias': Ocorrencia.objects.count(),
        'total_alunos': Aluno.objects.filter(ativo=True).count(),
        'total_turmas': Turma.objects.filter(ativa=True).count(),
    }

    if user.is_professor:
        # Estatísticas contextuais do Professor
        context['minhas_ocorrencias_qtd'] = Ocorrencia.objects.filter(professor=user).count()
        context['ultimas_ocorrencias'] = Ocorrencia.objects.filter(professor=user).select_related(
            'matricula_turma__aluno', 'matricula_turma__turma', 'categoria'
        )[:5]
    else:
        # Estatísticas da Coordenação / Administrador
        context['pendentes_analise_qtd'] = Ocorrencia.objects.filter(status=StatusOcorrencia.REGISTRADA).count()
        context['em_acompanhamento_qtd'] = Ocorrencia.objects.filter(status=StatusOcorrencia.EM_ACOMPANHAMENTO).count()
        context['ultimas_ocorrencias'] = Ocorrencia.objects.select_related(
            'matricula_turma__aluno', 'matricula_turma__turma', 'professor', 'categoria'
        )[:5]

    return render(request, 'core/home.html', context)
