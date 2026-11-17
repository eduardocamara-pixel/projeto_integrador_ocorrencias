from django.core.management.base import BaseCommand
from registros.models import CategoriaOcorrencia


CATEGORIAS_PADRAO = [
    {
        'nome': 'Indisciplina',
        'descricao': 'Comportamentos que infringem regras de convivência em sala de aula ou no ambiente escolar.'
    },
    {
        'nome': 'Conflitos entre estudantes',
        'descricao': 'Desentendimentos verbais, atritos ou divergências interpessoais entre alunos.'
    },
    {
        'nome': 'Desrespeito às normas escolares',
        'descricao': 'Descumprimento de horários, uso indevido de aparelhos eletrônicos ou normas regimentais.'
    },
    {
        'nome': 'Danos ao patrimônio',
        'descricao': 'Avarias ou depredação intencional de bens materiais ou instalações da escola.'
    },
    {
        'nome': 'Dificuldades de convivência',
        'descricao': 'Desafios na integração social, isolamento ou dinâmicas grupais que demandam acolhimento pedagógico.'
    },
    {
        'nome': 'Situações positivas / Atitudes de colaboração',
        'descricao': 'Ações de solidariedade, mediação pacífica, proatividade ou destaque em convivência cidadã.'
    },
    {
        'nome': 'Outras',
        'descricao': 'Outras situações relevantes para o acompanhamento pedagógico não categorizadas anteriormente.'
    },
]


class Command(BaseCommand):
    help = 'Cadastra as categorias padrão de ocorrências escolares especificadas no Documento Norteador.'

    def handle(self, *args, **options):
        criadas = 0
        existentes = 0

        for cat_data in CATEGORIAS_PADRAO:
            obj, created = CategoriaOcorrencia.objects.get_or_create(
                nome=cat_data['nome'],
                defaults={
                    'descricao': cat_data['descricao'],
                    'ativo': True
                }
            )
            if created:
                criadas += 1
                self.stdout.write(self.style.SUCCESS(f"[+] Categoria criada: '{obj.nome}'"))
            else:
                existentes += 1
                self.stdout.write(f"[-] Categoria já existente: '{obj.nome}'")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nProcesso concluído: {criadas} categorias inseridas, {existentes} já existentes."
            )
        )
