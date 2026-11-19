# Plano de Backup e Restauração de Dados — SIGOE

> **Sistema Integrado de Gestão de Ocorrências Escolares (SIGOE)**  
> **Objetivo:** Estabelecer a política, rotina técnica, periodicidade e plano de contingência para backup e restauração dos dados escolares.

---

## 1. Objetivos de Recuperação

| Métrica | Meta | Descrição |
| :--- | :--- | :--- |
| **RPO (Recovery Point Objective)** | < 24 horas | Perda máxima tolerável de dados em caso de sinistro (backups diários automáticos). |
| **RTO (Recovery Time Objective)** | < 1 hora | Tempo máximo para restabelecer a operação completa do sistema a partir de um backup. |

---

## 2. Estratégia de Backup (Regra 3-2-1)

1. **3 Cópias:** Manter pelo menos 3 cópias de todos os dados críticos (1 de produção + 2 backups).
2. **2 Mídias Diferentes:** Armazenamento em volumes ou serviços distintos (ex: disco do servidor e storage em nuvem/S3).
3. **1 Cópia Offsite:** Pelo menos uma cópia fora do servidor principal de aplicação.

---

## 3. Política de Periodicidade e Retenção

- **Diário:** Executado toda madrugada (às 02:00 BRT). Retenção por **7 dias**.
- **Semanal:** Consolidado aos domingos. Retenção por **4 semanas**.
- **Mensal:** Consolidado no primeiro dia do mês. Retenção por **12 meses**.
- **Anual:** Backup de encerramento do ano letivo. Retenção histórica por **5 anos**.

---

## 4. Rotinas Técnicas de Backup

### 4.1 Ambiente com SQLite (Desenvolvimento / Homologação)

O SQLite requer cópia atômica e verificação de integridade antes de arquivar:

```bash
# Execução via comando customizado do Django:
python manage.py fazer_backup

# Ou manualmente via SQLite vacuum into (consistente e sem bloquear escritas):
sqlite3 db.sqlite3 "VACUUM INTO 'backups/backup_sigoe_$(date +%Y%m%d_%H%M%S).sqlite3'"

# Verificação de integridade do arquivo gerado:
sqlite3 backups/backup_sigoe_AAAAMMDD.sqlite3 "PRAGMA integrity_check;"
```

### 4.2 Ambiente com PostgreSQL (Produção)

Em produção, o backup relacional é executado via `pg_dump`:

```bash
# Dump custom comprimido do banco
pg_dump -U postgres -h localhost -F c -b -v -f "backups/sigoe_prod_$(date +%Y%m%d_%H%M%S).dump" sigoe_db

# Encriptação com chave simétrica GPG (para proteção em nuvem)
gpg --symmetric --cipher-algo AES256 "backups/sigoe_prod_$(date +%Y%m%d_%H%M%S).dump"
```

---

## 5. Procedimento de Restauração (Runbook de Contingência)

Em caso de falha de hardware, corrupção ou necessidade de rollback:

### 5.1 Restauração em SQLite
1. Interromper o serviço da aplicação (`python manage.py runserver` / serviço systemd / gunicorn).
2. Isolar o banco comprometido renomeando-o para `db.sqlite3.corrupted_[TIMESTAMP]`.
3. Validar a integridade da cópia de backup escolhida:
   ```bash
   sqlite3 [ARQUIVO_BACKUP.sqlite3] "PRAGMA integrity_check;"
   # Saída esperada: "ok"
   ```
4. Restaurar a cópia como banco ativo:
   ```bash
   cp [ARQUIVO_BACKUP.sqlite3] db.sqlite3
   ```
5. Executar validação de migrações:
   ```bash
   python manage.py showmigrations
   ```
6. Reiniciar os serviços e validar o acesso de usuários e registros.

### 5.2 Restauração em PostgreSQL
1. Encerrar conexões ativas com o banco:
   ```sql
   SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'sigoe_db' AND pid <> pg_backend_pid();
   ```
2. Recriar o banco limpo:
   ```bash
   dropdb -U postgres sigoe_db
   createdb -U postgres -O sigoe_user sigoe_db
   ```
3. Restaurar os dados via `pg_restore`:
   ```bash
   pg_restore -U postgres -d sigoe_db -v "backups/sigoe_prod_AAAAMMDD.dump"
   ```
4. Executar verificação de consistência e iniciar o Django.

---

## 6. Testes Periódicos de Restauração
- A cada **30 dias**, um backup aleatório deve ser restaurado em ambiente isolado (staging) para garantir que as mídias não estejam corrompidas e que o procedimento de recuperação continue funcional.
