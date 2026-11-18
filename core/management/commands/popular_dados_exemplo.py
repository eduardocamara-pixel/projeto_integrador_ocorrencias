from datetime import date
from django.core.management.base import BaseCommand
from django.utils import timezone
from turmas.models import Turma, MatriculaTurma, TurnoTurma, SituacaoMatricula
from alunos.models import Aluno
from usuarios.models import Usuario, PerfilUsuario
from registros.models import CategoriaOcorrencia, Ocorrencia, StatusOcorrencia
from acompanhamento.models import Acompanhamento, HistoricoAlteracao, TipoRegistroAcompanhamento


class Command(BaseCommand):
    help = 'Cadastra turmas, estudantes e ocorrências demonstrativas para testar a navegação por perfil.'

    def handle(self, *args, **options):
        # 1. Turmas
        turma_9a, _ = Turma.objects.get_or_create(
            nome='9º Ano A',
            ano_letivo=2026,
            defaults={'serie': '9º Ano EF', 'turno': TurnoTurma.MATUTINO, 'ativa': True}
        )
        turma_9b, _ = Turma.objects.get_or_create(
            nome='9º Ano B',
            ano_letivo=2026,
            defaults={'serie': '9º Ano EF', 'turno': TurnoTurma.VESPERTINO, 'ativa': True}
        )
        turma_1em, _ = Turma.objects.get_or_create(
            nome='1º Ano EM - Informática',
            ano_letivo=2026,
            defaults={'serie': '1º Ano Médio Integrado', 'turno': TurnoTurma.INTEGRAL, 'ativa': True}
        )
        self.stdout.write(self.style.SUCCESS("[+] Turmas configuradas."))

        # 2. Alunos e Matrículas
        dados_alunos = [
            ('Gabriel Santos Ribeiro', '20260101', date(2011, 4, 15), turma_9a),
            ('Larissa Costa Ferreira', '20260102', date(2011, 7, 22), turma_9a),
            ('Matheus Oliveira Souza', '20260103', date(2011, 2, 9), turma_9a),
            ('Beatriz Lima Mendes', '20260104', date(2011, 11, 30), turma_9b),
            ('Enzo Vinicius Rocha', '20260105', date(2011, 5, 18), turma_9b),
            ('Isabela Duarte Martins', '20260106', date(2010, 9, 12), turma_1em),
            ('Rodrigo Alves Pereira', '20260107', date(2010, 12, 3), turma_1em),
        ]

        for nome, matricula, dt_nasc, turma in dados_alunos:
            aluno, _ = Aluno.objects.get_or_create(
                matricula=matricula,
                defaults={'nome': nome, 'data_nascimento': dt_nasc, 'ativo': True}
            )
            MatriculaTurma.objects.get_or_create(
                aluno=aluno,
                turma=turma,
                defaults={'situacao': SituacaoMatricula.ATIVA, 'data_entrada': date(2026, 2, 1)}
            )
        self.stdout.write(self.style.SUCCESS(f"[+] {len(dados_alunos)} Estudantes e matrículas ativas configuradas."))

        # 3. Ocorrências Demonstrativas
        professor = Usuario.objects.filter(perfil=PerfilUsuario.PROFESSOR).first()
        coordenador = Usuario.objects.filter(perfil=PerfilUsuario.COORDENACAO).first()
        cat_indisciplina = CategoriaOcorrencia.objects.filter(nome__icontains='Indisciplina').first()
        cat_conflito = CategoriaOcorrencia.objects.filter(nome__icontains='Conflito').first()

        if professor and coordenador and cat_indisciplina:
            matr_gabriel = MatriculaTurma.objects.filter(aluno__matricula='20260101').first()
            if matr_gabriel and not Ocorrencia.objects.filter(matricula_turma=matr_gabriel).exists():
                oc1 = Ocorrencia.objects.create(
                    matricula_turma=matr_gabriel,
                    professor=professor,
                    categoria=cat_indisciplina,
                    local='Sala de Aula 04',
                    descricao='O estudante utilizou aparelho celular durante a explicação da matéria e recusou-se a guardá-lo inicialmente.',
                    providencias_iniciais='Diálogo individual com o aluno após o término da aula; orientações sobre o regimento escolar.',
                    status=StatusOcorrencia.EM_ACOMPANHAMENTO
                )
                HistoricoAlteracao.objects.create(
                    usuario=professor,
                    ocorrencia=oc1,
                    acao_realizada='Registro Inicial da Ocorrência',
                    descricao_alteracao='Registro efetuado pelo professor.'
                )
                Acompanhamento.objects.create(
                    ocorrencia=oc1,
                    responsavel=coordenador,
                    tipo_registro=TipoRegistroAcompanhamento.REUNIAO_RESPONSAVEIS,
                    observacao='Reunião realizada com a mãe do estudante. Explicado o regimento e reforçada a importância da atenção nas aulas.',
                    encaminhamento='Termo de compromisso assinado pela responsável. Acompanhamento pedagógico quinzenal.'
                )
                HistoricoAlteracao.objects.create(
                    usuario=coordenador,
                    ocorrencia=oc1,
                    acao_realizada='Alteração de Status para Em Acompanhamento',
                    descricao_alteracao='Reunião com responsáveis realizada com êxito.'
                )
                self.stdout.write(self.style.SUCCESS(f"[+] Ocorrência demonstrativa #{oc1.id} criada."))

            matr_beatriz = MatriculaTurma.objects.filter(aluno__matricula='20260104').first()
            if matr_beatriz and cat_conflito and not Ocorrencia.objects.filter(matricula_turma=matr_beatriz).exists():
                oc2 = Ocorrencia.objects.create(
                    matricula_turma=matr_beatriz,
                    professor=professor,
                    categoria=cat_conflito,
                    local='Pátio no Intervalo',
                    descricao='Divergência verbal entre estudantes durante atividade recreativa no recreio.',
                    providencias_iniciais='Mediação de conflito imediata no pátio com separação dos envolvidos.',
                    status=StatusOcorrencia.REGISTRADA
                )
                HistoricoAlteracao.objects.create(
                    usuario=professor,
                    ocorrencia=oc2,
                    acao_realizada='Registro Inicial da Ocorrência',
                    descricao_alteracao='Registro efetuado pelo professor.'
                )
                self.stdout.write(self.style.SUCCESS(f"[+] Ocorrência demonstrativa #{oc2.id} criada (Pendente de Triagem)."))

        self.stdout.write(self.style.SUCCESS('\nDados de demonstração populados com sucesso!'))
