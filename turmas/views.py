from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Turma, MatriculaTurma, SituacaoMatricula
from .forms import TurmaForm, MatriculaTurmaForm
from usuarios.decorators import professor_ou_coordenacao_required, coordenacao_required


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


@login_required
@coordenacao_required
def cadastrar_turma_view(request):
    """
    Formulário para cadastro de uma nova turma escolar.
    """
    if request.method == 'POST':
        form = TurmaForm(request.POST)
        if form.is_valid():
            turma = form.save()
            messages.success(request, f"Turma '{turma.nome}' ({turma.ano_letivo}) cadastrada com sucesso!")
            return redirect('turmas:detalhe_turma', pk=turma.pk)
        else:
            messages.error(request, "Por favor, corrija os erros no formulário de turma.")
    else:
        form = TurmaForm()

    return render(request, 'turmas/form_turma.html', {
        'form': form,
        'titulo': 'Cadastrar Nova Turma',
        'subtitulo': 'Configure o nome, série, turno e ano letivo da turma escolar.'
    })


@login_required
@coordenacao_required
def editar_turma_view(request, pk):
    """
    Formulário para edição dos dados de uma turma existente.
    """
    turma = get_object_or_404(Turma, pk=pk)

    if request.method == 'POST':
        form = TurmaForm(request.POST, instance=turma)
        if form.is_valid():
            form.save()
            messages.success(request, f"Dados da turma '{turma.nome}' atualizados com sucesso!")
            return redirect('turmas:detalhe_turma', pk=turma.pk)
        else:
            messages.error(request, "Por favor, corrija os erros no formulário de edição de turma.")
    else:
        form = TurmaForm(instance=turma)

    return render(request, 'turmas/form_turma.html', {
        'form': form,
        'turma': turma,
        'titulo': f'Editar Turma: {turma.nome}',
        'subtitulo': 'Atualize as informações da turma.'
    })


@login_required
@coordenacao_required
def matricular_aluno_view(request, pk):
    """
    Realiza a enturmação (matrícula) de um estudante na turma informada.
    """
    turma = get_object_or_404(Turma, pk=pk)

    if request.method == 'POST':
        form = MatriculaTurmaForm(request.POST, turma=turma)
        if form.is_valid():
            matricula = form.save(commit=False)
            matricula.turma = turma
            matricula.save()
            messages.success(
                request,
                f"Estudante '{matricula.aluno.nome}' matriculado(a) com sucesso na turma '{turma.nome}'!"
            )
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
            for field, errors in form.errors.items():
                if field != '__all__':
                    messages.error(request, f"{field}: {errors[0]}")

    return redirect('turmas:detalhe_turma', pk=turma.pk)
