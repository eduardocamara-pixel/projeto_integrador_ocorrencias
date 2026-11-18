from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Turma, MatriculaTurma, SituacaoMatricula
from usuarios.decorators import professor_ou_coordenacao_required


@login_required
@professor_ou_coordenacao_required
def lista_turmas_view(request):
    """
    Lista as turmas cadastradas com quantidade de discentes matriculados.
    Acessível por Professores, Coordenação Pedagógica e Administradores.
    """
    ano_filtro = request.GET.get('ano')
    turno_filtro = request.GET.get('turno')

    turmas = Turma.objects.filter(ativa=True)
    if ano_filtro:
        turmas = turmas.filter(ano_letivo=ano_filtro)
    if turno_filtro:
        turmas = turmas.filter(turno=turno_filtro)

    turmas = turmas.order_by('-ano_letivo', 'nome')

    return render(request, 'turmas/lista_turmas.html', {
        'turmas': turmas,
        'ano_selecionado': ano_filtro,
        'turno_selecionado': turno_filtro,
    })


@login_required
@professor_ou_coordenacao_required
def detalhe_turma_view(request, pk):
    """
    Exibe os estudantes matriculados em uma determinada turma.
    """
    turma = get_object_or_404(Turma, pk=pk)
    matriculas = MatriculaTurma.objects.filter(
        turma=turma,
        situacao=SituacaoMatricula.ATIVA,
        aluno__ativo=True
    ).select_related('aluno').order_by('aluno__nome')

    return render(request, 'turmas/detalhe_turma.html', {
        'turma': turma,
        'matriculas': matriculas,
    })
