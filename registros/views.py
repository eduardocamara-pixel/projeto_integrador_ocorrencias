from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
from .models import Ocorrencia, StatusOcorrencia, CategoriaOcorrencia
from .forms import OcorrenciaForm, CategoriaOcorrenciaForm
from turmas.models import Turma
from usuarios.models import Usuario, PerfilUsuario
from acompanhamento.models import HistoricoAlteracao
from usuarios.decorators import professor_required, coordenacao_required, admin_required


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


# ==========================================
# GESTÃO DE CATEGORIAS DE OCORRÊNCIA
# ==========================================

@login_required
@coordenacao_required
def lista_categorias_view(request):
    """
    Interface para listagem e consulta das Categorias de Ocorrência.
    Exibe a contagem de ocorrências associadas e status de ativação.
    """
    busca = request.GET.get('busca', '').strip()
    categorias = CategoriaOcorrencia.objects.annotate(
        total_ocorrencias=Count('ocorrencias')
    ).order_by('nome')

    if busca:
        categorias = categorias.filter(
            Q(nome__icontains=busca) | Q(descricao__icontains=busca)
        )

    form_cadastro = CategoriaOcorrenciaForm()

    return render(request, 'registros/categorias.html', {
        'categorias': categorias,
        'busca': busca,
        'form_cadastro': form_cadastro,
        'total_ativas': CategoriaOcorrencia.objects.filter(ativo=True).count(),
        'total_inativas': CategoriaOcorrencia.objects.filter(ativo=False).count(),
    })


@login_required
@coordenacao_required
def cadastrar_categoria_view(request):
    """
    Criação de uma nova categoria de ocorrência.
    """
    if request.method == 'POST':
        form = CategoriaOcorrenciaForm(request.POST)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f"Categoria '{cat.nome}' criada com sucesso!")
            return redirect('registros:lista_categorias')
        else:
            messages.error(request, "Por favor, corrija os erros no formulário de categoria.")
    else:
        form = CategoriaOcorrenciaForm()

    return render(request, 'registros/form_categoria.html', {
        'form': form,
        'titulo': 'Nova Categoria de Ocorrência',
        'subtitulo': 'Defina o nome e os critérios pedagógicos para esta categoria.'
    })


@login_required
@coordenacao_required
def editar_categoria_view(request, pk):
    """
    Edição de uma categoria de ocorrência existente.
    """
    categoria = get_object_or_404(CategoriaOcorrencia, pk=pk)

    if request.method == 'POST':
        form = CategoriaOcorrenciaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f"Categoria '{categoria.nome}' atualizada com sucesso!")
            return redirect('registros:lista_categorias')
        else:
            messages.error(request, "Por favor, corrija os erros no formulário de edição.")
    else:
        form = CategoriaOcorrenciaForm(instance=categoria)

    return render(request, 'registros/form_categoria.html', {
        'form': form,
        'categoria': categoria,
        'titulo': f'Editar Categoria: {categoria.nome}',
        'subtitulo': 'Atualize a descrição ou o status de disponibilidade.'
    })


@login_required
@coordenacao_required
def toggle_categoria_view(request, pk):
    """
    Ativa ou inativa uma categoria de ocorrência.
    """
    categoria = get_object_or_404(CategoriaOcorrencia, pk=pk)
    categoria.ativo = not categoria.ativo
    categoria.save()

    status_str = "ativada" if categoria.ativo else "inativada"
    messages.success(request, f"Categoria '{categoria.nome}' foi {status_str} com sucesso.")
    return redirect('registros:lista_categorias')


# ==========================================
# LISTAGEM E CONSULTA GERAL DE OCORRÊNCIAS (RF08)
# ==========================================

@login_required
def consulta_ocorrencias_view(request):
    """
    Consulta multidimensional e abrangente de ocorrências escolares (RF08).
    Permite filtros avançados por:
    - Aluno / Matrícula
    - Turma
    - Categoria
    - Status da tramitação
    - Professor relator
    - Período (Data inicial e Data final)
    Professores visualizam as ocorrências por si registradas, enquanto Coordenação
    e Administradores possuem visão unificada de toda a instituição escolar.
    """
    user = request.user
    if user.is_admin or user.is_coordenacao:
        ocorrencias = Ocorrencia.objects.all()
    else:
        ocorrencias = Ocorrencia.objects.filter(professor=user)

    # Parâmetros de filtro
    busca = request.GET.get('busca', '').strip()
    turma_id = request.GET.get('turma', '')
    categoria_id = request.GET.get('categoria', '')
    status_filtro = request.GET.get('status', '')
    professor_id = request.GET.get('professor', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')

    if busca:
        ocorrencias = ocorrencias.filter(
            Q(matricula_turma__aluno__nome__icontains=busca) |
            Q(matricula_turma__aluno__matricula__icontains=busca) |
            Q(local__icontains=busca) |
            Q(descricao__icontains=busca)
        )

    if turma_id:
        ocorrencias = ocorrencias.filter(matricula_turma__turma_id=turma_id)

    if categoria_id:
        ocorrencias = ocorrencias.filter(categoria_id=categoria_id)

    if status_filtro:
        ocorrencias = ocorrencias.filter(status=status_filtro)

    if professor_id and (user.is_admin or user.is_coordenacao):
        ocorrencias = ocorrencias.filter(professor_id=professor_id)

    if data_inicio:
        d_inicio = parse_date(data_inicio)
        if d_inicio:
            ocorrencias = ocorrencias.filter(data_ocorrencia__date__gte=d_inicio)

    if data_fim:
        d_fim = parse_date(data_fim)
        if d_fim:
            ocorrencias = ocorrencias.filter(data_ocorrencia__date__lte=d_fim)

    # Otimização ORM
    ocorrencias = ocorrencias.select_related(
        'matricula_turma__aluno',
        'matricula_turma__turma',
        'categoria',
        'professor'
    ).order_by('-data_ocorrencia')

    # Totalizador
    total_filtrado = ocorrencias.count()

    # Paginação (15 ocorrências por página)
    paginator = Paginator(ocorrencias, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Dados para popular os selects de filtro
    turmas = Turma.objects.filter(ativa=True).order_by('-ano_letivo', 'nome')
    categorias = CategoriaOcorrencia.objects.all().order_by('nome')
    professores = Usuario.objects.filter(perfil=PerfilUsuario.PROFESSOR, ativo=True).order_by('nome')

    context = {
        'page_obj': page_obj,
        'total_filtrado': total_filtrado,
        'turmas': turmas,
        'categorias': categorias,
        'professores': professores,
        'status_choices': StatusOcorrencia.choices,
        # Filtros atuais
        'busca': busca,
        'turma_selecionada': turma_id,
        'categoria_selecionada': categoria_id,
        'status_selecionado': status_filtro,
        'professor_selecionado': professor_id,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    }
    return render(request, 'registros/consulta_ocorrencias.html', context)
