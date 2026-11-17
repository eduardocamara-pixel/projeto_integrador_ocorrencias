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
