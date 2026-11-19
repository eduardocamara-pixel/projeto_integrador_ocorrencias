from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Aluno
from .forms import AlunoForm
from registros.models import Ocorrencia, StatusOcorrencia
from turmas.models import MatriculaTurma, SituacaoMatricula
from usuarios.decorators import coordenacao_required


@login_required
@coordenacao_required
def lista_alunos_view(request):
    """
    Lista todos os estudantes para consulta da Coordenação e Gestores.
    Permite busca por nome ou matrícula.
    """
    busca = request.GET.get('busca', '').strip()
    alunos = Aluno.objects.filter(ativo=True).prefetch_related('matriculas__turma').order_by('nome')

    if busca:
        alunos = alunos.filter(nome__icontains=busca) | alunos.filter(matricula__icontains=busca)

    return render(request, 'alunos/lista_alunos.html', {
        'alunos': alunos,
        'busca': busca,
    })


@login_required
@coordenacao_required
def prontuario_aluno_view(request, pk):
    """
    Prontuário Pedagógico Individual do Estudante (RF07).
    Apresenta histórico de matrículas, todas as ocorrências vinculadas,
    intervenções pedagógicas e indicadores comportamentais do discente.
    """
    aluno = get_object_or_404(Aluno, pk=pk)

    # Matrículas
    matriculas = MatriculaTurma.objects.filter(aluno=aluno).select_related('turma').order_by('-data_entrada')

    # Todas as ocorrências do estudante através de suas matrículas
    ocorrencias = Ocorrencia.objects.filter(
        matricula_turma__aluno=aluno
    ).select_related(
        'matricula_turma__turma',
        'categoria',
        'professor'
    ).prefetch_related('acompanhamentos').order_by('-data_ocorrencia')

    # Métricas pedagógicas do aluno
    total_ocorrencias = ocorrencias.count()
    ocorrencias_em_aberto = ocorrencias.exclude(status=StatusOcorrencia.CONCLUIDA).count()
    ocorrencias_concluidas = ocorrencias.filter(status=StatusOcorrencia.CONCLUIDA).count()

    return render(request, 'alunos/prontuario_aluno.html', {
        'aluno': aluno,
        'matriculas': matriculas,
        'ocorrencias': ocorrencias,
        'total_ocorrencias': total_ocorrencias,
        'ocorrencias_em_aberto': ocorrencias_em_aberto,
        'ocorrencias_concluidas': ocorrencias_concluidas,
    })


@login_required
@coordenacao_required
def cadastrar_aluno_view(request):
    """
    Formulário para cadastrar um novo discente na instituição.
    """
    if request.method == 'POST':
        form = AlunoForm(request.POST)
        if form.is_valid():
            aluno = form.save()
            messages.success(request, f"Estudante '{aluno.nome}' (Matrícula: {aluno.matricula}) cadastrado(a) com sucesso!")
            return redirect('alunos:prontuario_aluno', pk=aluno.pk)
        else:
            messages.error(request, "Por favor, corrija os erros no formulário de cadastro de aluno.")
    else:
        form = AlunoForm()

    return render(request, 'alunos/form_aluno.html', {
        'form': form,
        'titulo': 'Cadastrar Novo Estudante',
        'subtitulo': 'Preencha os dados cadastrais básicos do estudante.'
    })


@login_required
@coordenacao_required
def editar_aluno_view(request, pk):
    """
    Formulário para editar dados de um discente já existente.
    """
    aluno = get_object_or_404(Aluno, pk=pk)

    if request.method == 'POST':
        form = AlunoForm(request.POST, instance=aluno)
        if form.is_valid():
            form.save()
            messages.success(request, f"Cadastro do estudante '{aluno.nome}' atualizado com sucesso!")
            return redirect('alunos:prontuario_aluno', pk=aluno.pk)
        else:
            messages.error(request, "Por favor, corrija os erros no formulário de edição de aluno.")
    else:
        form = AlunoForm(instance=aluno)

    return render(request, 'alunos/form_aluno.html', {
        'form': form,
        'aluno': aluno,
        'titulo': f'Editar Estudante: {aluno.nome}',
        'subtitulo': 'Atualize os dados acadêmicos ou cadastrais do estudante.'
    })
