from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import date
from usuarios.models import Usuario, PerfilUsuario
from alunos.models import Aluno
from turmas.models import Turma, MatriculaTurma, TurnoTurma, SituacaoMatricula
from registros.models import CategoriaOcorrencia, Ocorrencia, StatusOcorrencia
from acompanhamento.models import Acompanhamento, HistoricoAlteracao, TipoRegistroAcompanhamento


class ModelagemIntegridadeTestCase(TestCase):
    def test_fluxo_completo_entidades(self):
        # 1. Criação de Usuários
        professor = Usuario.objects.create_user(
            email='professor@escola.gov.br',
            nome='Carlos Silva',
            password='senha_segura_123',
            perfil=PerfilUsuario.PROFESSOR
        )
        coordenador = Usuario.objects.create_user(
            email='coord@escola.gov.br',
            nome='Mariana Souza',
            password='senha_segura_123',
            perfil=PerfilUsuario.COORDENACAO
        )

        self.assertEqual(professor.perfil, PerfilUsuario.PROFESSOR)
        self.assertTrue(professor.is_professor)
        self.assertTrue(coordenador.is_coordenacao)

        # 2. Criação de Aluno e Turma
        aluno = Aluno.objects.create(
            nome='Lucas Oliveira',
            matricula='2026001',
            data_nascimento=date(2010, 5, 14)
        )
        turma = Turma.objects.create(
            nome='9º Ano B',
            serie='9º EF',
            turno=TurnoTurma.MATUTINO,
            ano_letivo=2026
        )

        # 3. Associação Aluno-Turma (Matrícula)
        matricula = MatriculaTurma.objects.create(
            aluno=aluno,
            turma=turma,
            situacao=SituacaoMatricula.ATIVA
        )
        self.assertEqual(matricula.aluno, aluno)
        self.assertEqual(matricula.turma, turma)

        # 4. Categoria e Registro de Ocorrência
        categoria = CategoriaOcorrencia.objects.create(
            nome='Indisciplina em Sala',
            descricao='Atitudes de dispersão recorrente'
        )
        ocorrencia = Ocorrencia.objects.create(
            matricula_turma=matricula,
            professor=professor,
            categoria=categoria,
            local='Sala de Aula 10',
            descricao='O aluno conversou e desrespeitou as orientações em sala.',
            providencias_iniciais='Conversa de advertência ao término da aula.',
            status=StatusOcorrencia.REGISTRADA
        )
        self.assertEqual(ocorrencia.aluno, aluno)
        self.assertEqual(ocorrencia.turma, turma)
        self.assertEqual(ocorrencia.status, StatusOcorrencia.REGISTRADA)

        # 5. Acompanhamento Pedagógico da Coordenação
        acompanhamento = Acompanhamento.objects.create(
            ocorrencia=ocorrencia,
            responsavel=coordenador,
            tipo_registro=TipoRegistroAcompanhamento.ORIENTACAO,
            observacao='Diálogo com o estudante para conscientização.',
            encaminhamento='Acompanhar comportamento nas próximas semanas.'
        )
        self.assertEqual(acompanhamento.ocorrencia, ocorrencia)
        self.assertEqual(acompanhamento.responsavel, coordenador)

        # 6. Histórico de Alteração (Auditoria LGPD)
        historico = HistoricoAlteracao.objects.create(
            usuario=coordenador,
            ocorrencia=ocorrencia,
            acao_realizada='Mudança de status para EM_ACOMPANHAMENTO',
            descricao_alteracao='Acolhimento pedagógico iniciado.'
        )
        self.assertEqual(historico.ocorrencia, ocorrencia)
        self.assertEqual(historico.usuario, coordenador)


class AutenticacaoNavegacaoTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create_user(
            email='prof.ana@escola.gov.br',
            nome='Ana Paula Santos',
            password='SenhaValida@2026',
            perfil=PerfilUsuario.PROFESSOR
        )

    def test_tela_login_renderiza_com_sucesso(self):
        """Verifica se a tela de login responde com HTTP 200 e carrega os templates corretos."""
        response = self.client.get(reverse('usuarios:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/login.html')
        self.assertTemplateUsed(response, 'base.html')
        self.assertContains(response, 'SIGOE')
        self.assertContains(response, 'E-mail Institucional')
        self.assertContains(response, 'Senha de Acesso')
        self.assertContains(response, 'Entrar no Sistema')

    def test_login_sucesso(self):
        """Verifica autenticação bem-sucedida por e-mail e senha com redirecionamento."""
        response = self.client.post(reverse('usuarios:login'), {
            'email': 'prof.ana@escola.gov.br',
            'password': 'SenhaValida@2026',
            'lembrar_me': True
        })
        self.assertRedirects(response, reverse('core:home'))

    def test_login_credenciais_invalidas(self):
        """Verifica que credenciais inválidas não logam e mostram mensagem de erro."""
        response = self.client.post(reverse('usuarios:login'), {
            'email': 'prof.ana@escola.gov.br',
            'password': 'senha_errada_aqui',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'E-mail ou senha incorretos')

    def test_redirecionamento_usuario_anonimo(self):
        """Verifica que a rota principal redireciona usuário anônimo para o login."""
        response = self.client.get(reverse('core:home'))
        self.assertRedirects(response, f"{reverse('usuarios:login')}?next=/")

    def test_painel_principal_autenticado(self):
        """Verifica que o usuário autenticado acessa a home com a navbar personalizada."""
        self.client.login(username='prof.ana@escola.gov.br', password='SenhaValida@2026')
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertContains(response, 'Ana Paula Santos')
        self.assertContains(response, 'Professor')
        self.assertContains(response, 'Sair do Sistema')

    def test_logout(self):
        """Verifica o encerramento seguro da sessão."""
        self.client.login(username='prof.ana@escola.gov.br', password='SenhaValida@2026')
        response = self.client.post(reverse('usuarios:logout'))
        self.assertRedirects(response, reverse('usuarios:login'))


class NavegacaoPorPerfilTestCase(TestCase):
    """
    Testes de Controle de Acesso Baseado em Papéis (RBAC) e Navegação por Perfil.
    """
    def setUp(self):
        self.client = Client()

        # Criação de usuários com os 3 perfis
        self.professor = Usuario.objects.create_user(
            email='prof.roberto@escola.gov.br',
            nome='Prof. Roberto Mendes',
            password='SenhaProfessor123',
            perfil=PerfilUsuario.PROFESSOR
        )
        self.coordenadora = Usuario.objects.create_user(
            email='coord.claudia@escola.gov.br',
            nome='Claudia Coordenadora',
            password='SenhaCoord123',
            perfil=PerfilUsuario.COORDENACAO
        )
        self.admin = Usuario.objects.create_user(
            email='admin.marcos@escola.gov.br',
            nome='Marcos Admin',
            password='SenhaAdmin123',
            perfil=PerfilUsuario.ADMIN,
            is_staff=True,
            is_superuser=True
        )

        # Dados base para teste de registro
        self.aluno = Aluno.objects.create(
            nome='Beatriz Lima',
            matricula='2026099',
            data_nascimento=date(2011, 3, 20)
        )
        self.turma = Turma.objects.create(
            nome='8º Ano A',
            serie='8º EF',
            turno=TurnoTurma.MATUTINO,
            ano_letivo=2026
        )
        self.matricula = MatriculaTurma.objects.create(
            aluno=self.aluno,
            turma=self.turma,
            situacao=SituacaoMatricula.ATIVA
        )
        self.categoria = CategoriaOcorrencia.objects.create(
            nome='Conflito Interpessoal',
            descricao='Discussões e divergências'
        )

    def test_navegacao_perfil_professor(self):
        """O Professor deve acessar suas telas específicas e ser bloqueado nas restritas à Coordenação/Admin."""
        self.client.login(username='prof.roberto@escola.gov.br', password='SenhaProfessor123')

        # Acessos permitidos ao Professor
        res_minhas = self.client.get(reverse('registros:minhas_ocorrencias'))
        self.assertEqual(res_minhas.status_code, 200)

        res_nova = self.client.get(reverse('registros:nova_ocorrencia'))
        self.assertEqual(res_nova.status_code, 200)

        res_turmas = self.client.get(reverse('turmas:lista_turmas'))
        self.assertEqual(res_turmas.status_code, 200)

        # Acessos PROIBIDOS ao Professor (403)
        res_triagem = self.client.get(reverse('acompanhamento:triagem'))
        self.assertEqual(res_triagem.status_code, 403)
        self.assertTemplateUsed(res_triagem, '403.html')

        res_admin_painel = self.client.get(reverse('usuarios:painel_admin'))
        self.assertEqual(res_admin_painel.status_code, 403)

    def test_navegacao_perfil_coordenacao(self):
        """A Coordenação deve acessar triagem, prontuários e turmas, mas não o painel admin exclusivo."""
        self.client.login(username='coord.claudia@escola.gov.br', password='SenhaCoord123')

        # Acessos permitidos à Coordenação
        res_triagem = self.client.get(reverse('acompanhamento:triagem'))
        self.assertEqual(res_triagem.status_code, 200)

        res_alunos = self.client.get(reverse('alunos:lista_alunos'))
        self.assertEqual(res_alunos.status_code, 200)

        res_turmas = self.client.get(reverse('turmas:lista_turmas'))
        self.assertEqual(res_turmas.status_code, 200)

        # Acesso PROIBIDO à Coordenação (painel exclusivo do Admin)
        res_admin_painel = self.client.get(reverse('usuarios:painel_admin'))
        self.assertEqual(res_admin_painel.status_code, 403)

    def test_navegacao_perfil_admin(self):
        """O Administrador possui acesso irrestrito a todas as áreas do sistema."""
        self.client.login(username='admin.marcos@escola.gov.br', password='SenhaAdmin123')

        self.assertEqual(self.client.get(reverse('usuarios:painel_admin')).status_code, 200)
        self.assertEqual(self.client.get(reverse('acompanhamento:triagem')).status_code, 200)
        self.assertEqual(self.client.get(reverse('registros:nova_ocorrencia')).status_code, 200)
        self.assertEqual(self.client.get(reverse('alunos:lista_alunos')).status_code, 200)
        self.assertEqual(self.client.get(reverse('turmas:lista_turmas')).status_code, 200)

    def test_fluxo_registro_e_tramitacao_interativo(self):
        """Simula o fluxo completo: Professor registra, Coordenação tramita e audita."""
        # 1. Professor registra ocorrência
        self.client.login(username='prof.roberto@escola.gov.br', password='SenhaProfessor123')
        post_data = {
            'matricula_turma': self.matricula.id,
            'categoria': self.categoria.id,
            'data_ocorrencia': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'local': 'Pátio Central',
            'descricao': 'Estudante se exaltou durante o intervalo.',
            'providencias_iniciais': 'Orientação verbal imediata.'
        }
        res_post = self.client.post(reverse('registros:nova_ocorrencia'), post_data)
        self.assertRedirects(res_post, reverse('registros:minhas_ocorrencias'))

        ocorrencia = Ocorrencia.objects.filter(matricula_turma=self.matricula).first()
        self.assertIsNotNone(ocorrencia)
        self.assertEqual(ocorrencia.status, StatusOcorrencia.REGISTRADA)
        self.assertEqual(ocorrencia.professor, self.professor)

        # 2. Coordenação faz login, acessa triagem e tramita para EM_ANALISE
        self.client.login(username='coord.claudia@escola.gov.br', password='SenhaCoord123')
        res_triagem = self.client.get(reverse('acompanhamento:triagem'))
        self.assertEqual(res_triagem.status_code, 200)
        self.assertContains(res_triagem, 'Beatriz Lima')

        # Tramita status para EM_ANALISE
        res_status = self.client.post(
            reverse('acompanhamento:detalhe_ocorrencia', kwargs={'pk': ocorrencia.id}),
            {
                'action': 'mudar_status',
                'novo_status': StatusOcorrencia.EM_ANALISE,
                'justificativa': 'Iniciando escuta dos envolvidos.'
            }
        )
        self.assertRedirects(res_status, reverse('acompanhamento:detalhe_ocorrencia', kwargs={'pk': ocorrencia.id}))
        ocorrencia.refresh_from_db()
        self.assertEqual(ocorrencia.status, StatusOcorrencia.EM_ANALISE)

        # Registra intervenção pedagógica
        res_acomp = self.client.post(
            reverse('acompanhamento:detalhe_ocorrencia', kwargs={'pk': ocorrencia.id}),
            {
                'action': 'novo_acompanhamento',
                'tipo_registro': TipoRegistroAcompanhamento.ORIENTACAO,
                'observacao': 'Estudante acolhida na coordenação, reconheceu o erro.',
                'encaminhamento': 'Termo de convivência pactuado.'
            }
        )
        self.assertRedirects(res_acomp, reverse('acompanhamento:detalhe_ocorrencia', kwargs={'pk': ocorrencia.id}))

        # Verifica histórico de intervenções e auditoria
        self.assertEqual(ocorrencia.acompanhamentos.count(), 1)
        self.assertTrue(HistoricoAlteracao.objects.filter(ocorrencia=ocorrencia).count() >= 2)


class NovasTelasSIGOETestCase(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_superuser(
            email='admin.sistema@escola.gov.br',
            nome='Diretora Administradora',
            password='AdminPassword123'
        )
        self.coordenador = Usuario.objects.create_user(
            email='coord.geral@escola.gov.br',
            nome='Coordenadora Geral',
            password='CoordPassword123',
            perfil=PerfilUsuario.COORDENACAO
        )
        self.professor = Usuario.objects.create_user(
            email='prof.roberto@escola.gov.br',
            nome='Roberto Docente',
            password='ProfPassword123',
            perfil=PerfilUsuario.PROFESSOR
        )

    def test_gestao_usuario_edicao(self):
        self.client.login(username='admin.sistema@escola.gov.br', password='AdminPassword123')
        # Acessa edição do professor
        res = self.client.get(reverse('usuarios:editar_usuario', kwargs={'pk': self.professor.id}))
        self.assertEqual(res.status_code, 200)

        # Atualiza nome
        post_data = {
            'nome': 'Roberto Docente Atualizado',
            'email': self.professor.email,
            'perfil': PerfilUsuario.PROFESSOR,
            'ativo': True,
        }
        res_post = self.client.post(reverse('usuarios:editar_usuario', kwargs={'pk': self.professor.id}), post_data)
        self.assertRedirects(res_post, reverse('usuarios:painel_admin'))
        self.professor.refresh_from_db()
        self.assertEqual(self.professor.nome, 'Roberto Docente Atualizado')

    def test_cadastro_e_edicao_aluno(self):
        self.client.login(username='coord.geral@escola.gov.br', password='CoordPassword123')

        # Acessa form de cadastro
        res_get = self.client.get(reverse('alunos:cadastrar_aluno'))
        self.assertEqual(res_get.status_code, 200)

        # Cadastra novo aluno
        post_data = {
            'nome': 'Mariana Souza Dias',
            'matricula': '2026-MAT01',
            'data_nascimento': '2011-04-10',
            'ativo': True
        }
        res_post = self.client.post(reverse('alunos:cadastrar_aluno'), post_data)
        novo_aluno = Aluno.objects.filter(matricula='2026-MAT01').first()
        self.assertIsNotNone(novo_aluno)
        self.assertRedirects(res_post, reverse('alunos:prontuario_aluno', kwargs={'pk': novo_aluno.pk}))

        # Edita aluno
        res_edit = self.client.post(
            reverse('alunos:editar_aluno', kwargs={'pk': novo_aluno.pk}),
            {
                'nome': 'Mariana Souza Dias Ramos',
                'matricula': '2026-MAT01',
                'data_nascimento': '2011-04-10',
                'ativo': True
            }
        )
        self.assertRedirects(res_edit, reverse('alunos:prontuario_aluno', kwargs={'pk': novo_aluno.pk}))
        novo_aluno.refresh_from_db()
        self.assertEqual(novo_aluno.nome, 'Mariana Souza Dias Ramos')

    def test_cadastro_e_edicao_turma_e_matricula(self):
        self.client.login(username='coord.geral@escola.gov.br', password='CoordPassword123')

        # Cadastra turma
        turma_data = {
            'nome': '1º Ano Informática B',
            'serie': '1º Ano Técnico',
            'turno': TurnoTurma.VESPERTINO,
            'ano_letivo': 2026,
            'ativa': True
        }
        res_post = self.client.post(reverse('turmas:cadastrar_turma'), turma_data)
        turma = Turma.objects.filter(nome='1º Ano Informática B').first()
        self.assertIsNotNone(turma)
        self.assertRedirects(res_post, reverse('turmas:detalhe_turma', kwargs={'pk': turma.pk}))

        # Cria aluno e realiza matrícula via view matricular_aluno
        aluno = Aluno.objects.create(
            nome='Eduardo Lima',
            matricula='2026-ED01',
            data_nascimento=date(2009, 3, 12)
        )
        res_matr = self.client.post(
            reverse('turmas:matricular_aluno', kwargs={'pk': turma.pk}),
            {
                'aluno': aluno.id,
                'data_entrada': date.today().strftime('%Y-%m-%d'),
                'situacao': SituacaoMatricula.ATIVA
            }
        )
        self.assertRedirects(res_matr, reverse('turmas:detalhe_turma', kwargs={'pk': turma.pk}))
        self.assertTrue(MatriculaTurma.objects.filter(aluno=aluno, turma=turma).exists())

    def test_gestao_categorias(self):
        self.client.login(username='coord.geral@escola.gov.br', password='CoordPassword123')

        # Listagem
        res_lista = self.client.get(reverse('registros:lista_categorias'))
        self.assertEqual(res_lista.status_code, 200)

        # Cadastro de categoria
        res_cat = self.client.post(
            reverse('registros:cadastrar_categoria'),
            {
                'nome': 'Dificuldade de Foco / Distração',
                'descricao': 'Comportamentos dispersivos recorrentes.',
                'ativo': True
            }
        )
        self.assertRedirects(res_cat, reverse('registros:lista_categorias'))
        cat = CategoriaOcorrencia.objects.filter(nome='Dificuldade de Foco / Distração').first()
        self.assertIsNotNone(cat)

        # Toggle status
        self.client.get(reverse('registros:toggle_categoria', kwargs={'pk': cat.id}))
        cat.refresh_from_db()
        self.assertFalse(cat.ativo)

    def test_consulta_multidimensional_ocorrencias(self):
        self.client.login(username='coord.geral@escola.gov.br', password='CoordPassword123')
        res_consulta = self.client.get(reverse('registros:consulta_ocorrencias'))
        self.assertEqual(res_consulta.status_code, 200)
        self.assertContains(res_consulta, 'Consulta e Listagem de Ocorrências')
