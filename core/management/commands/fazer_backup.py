import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Executa backup consistente do banco de dados com verificação de integridade.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias-retencao',
            type=int,
            default=7,
            help='Número de dias para reter backups locais (padrão: 7 dias).'
        )

    def handle(self, *args, **options):
        db_settings = settings.DATABASES['default']
        engine = db_settings.get('ENGINE', '')
        dias_retencao = options['dias_retencao']

        backup_dir = settings.BASE_DIR / 'backups'
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if 'sqlite3' in engine:
            db_path = Path(db_settings['NAME'])
            if not db_path.exists():
                self.stderr.write(self.style.ERROR(f"Banco de dados não encontrado em: {db_path}"))
                return

            dest_filename = f"backup_sigoe_{timestamp}.sqlite3"
            dest_path = backup_dir / dest_filename

            self.stdout.write(f"Iniciando backup atômico do SQLite para: {dest_path.name}...")

            # Backup atômico usando a API nativa do SQLite
            try:
                src_conn = sqlite3.connect(str(db_path))
                dest_conn = sqlite3.connect(str(dest_path))
                with dest_conn:
                    src_conn.backup(dest_conn)
                dest_conn.close()
                src_conn.close()

                # Verificação de integridade
                check_conn = sqlite3.connect(str(dest_path))
                cursor = check_conn.cursor()
                cursor.execute("PRAGMA integrity_check;")
                result = cursor.fetchone()
                check_conn.close()

                if result and result[0] == 'ok':
                    tamanho_kb = dest_path.stat().st_size / 1024
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"[OK] Backup concluído com sucesso: {dest_path.name} ({tamanho_kb:.2f} KB) - Integridade: OK"
                        )
                    )
                else:
                    self.stderr.write(
                        self.style.ERROR(f"[ERRO] Falha na integridade do backup: {result}")
                    )
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Erro ao executar backup: {e}"))
                return

        else:
            self.stdout.write(self.style.WARNING("Configuração de backup para PostgreSQL: utilize pg_dump conforme plano_backup_restauracao.md"))

        # Rotatividade de backups antigos
        limite = datetime.now() - timedelta(days=dias_retencao)
        removidos = 0
        for arq in backup_dir.glob("backup_sigoe_*.sqlite3"):
            try:
                mtime = datetime.fromtimestamp(arq.stat().st_mtime)
                if mtime < limite:
                    arq.unlink()
                    removidos += 1
            except Exception:
                pass

        if removidos > 0:
            self.stdout.write(self.style.NOTICE(f"Rotatividade: {removidos} backup(s) com mais de {dias_retencao} dias removido(s)."))
