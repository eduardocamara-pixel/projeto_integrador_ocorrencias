# Política de Retenção, Descarte e Proteção de Dados — SIGOE

> **Sistema Integrado de Gestão de Ocorrências Escolares (SIGOE)**  
> **Fundamentação Legal:** Lei Geral de Proteção de Dados Pessoais (LGPD - Lei nº 13.709/2018), Estatuto da Criança e do Adolescente (ECA - Lei nº 8.069/1990) e Diretrizes da Educação Básica (MEC/CNE).

---

## 1. Princípios Norteadores

1. **Princípio do Melhor Interesse da Criança e do Adolescente (ECA, Art. 100):** O tratamento de dados pessoais de estudantes menores de idade é feito estritamente em seu melhor interesse, para acompanhamento pedagógico, acolhimento e garantia do direito à educação em ambiente seguro.
2. **Princípio da Finalidade e Adequação:** Os registros de ocorrências escolares e acompanhamentos devem restringir-se aos fatos observados, sem rótulos pejorativos, juízos morais ou diagnósticos clínicos não qualificados.
3. **Princípio da Necessidade e Minimização:** Coleta estritamente dos dados necessários para a atuação pedagógica e resolução de conflitos no âmbito escolar.
4. **Princípio da Segurança e Confidencialidade:** O acesso às ocorrências e pareceres pedagógicos é restrito a profissionais autorizados (RBAC).

---

## 2. Tabela de Ciclo de Vida e Prazos de Retenção

| Entidade / Dado | Finalidade | Prazo de Retenção Ativa | Prazo de Retenção Histórica (Arquivo Passivo) | Destinação Final |
| :--- | :--- | :--- | :--- | :--- |
| **Aluno** (`Aluno`) | Identificação institucional e vínculo acadêmico | Enquanto durar a matrícula ativa na instituição | 5 anos após a conclusão ou transferência escolar | Anonimização dos dados de contato; preservação do histórico de matrícula |
| **Turma e Matrícula** (`Turma`, `MatriculaTurma`) | Organização pedagógica e comprovação de frequência | Durante o ano letivo correspondente | Permanente (composição do histórico escolar da instituição) | Guarda permanente conforme normas educacionais |
| **Ocorrências Escolares** (`Ocorrencia`) | Registro de fatos e intervenção imediata | Durante o ano letivo do fato até conclusão do ciclo | Até o término do ciclo escolar do estudante na instituição (máx. 3 a 5 anos) | **Expurgo / Descarte definitivo** dos relatos fáticos após a desvinculação do aluno |
| **Acompanhamento Pedagógico** (`Acompanhamento`) | Pareceres pedagógicos, termos e atas de reuniões | Durante a permanência do estudante na escola | 3 anos após saída do estudante | Destruição segura e descarte digital |
| **Histórico de Auditoria** (`HistoricoAlteracao`) | Rastreabilidade, conformidade legal e auditoria LGPD | 5 anos a contar da data de registro da ação | Não aplicável | Expurgo automático |
| **Usuários** (`Usuario`) | Acesso e controle de operadores do sistema | Enquanto durar o vínculo funcional do profissional | 5 anos após desligamento institucional (fins trabalhistas/auditoria) | Inativação imediata (`ativo=False`) e posterior anonimização |

---

## 3. Protocolos de Descarte Seguro

1. **Expurgo Lógico vs. Físico:**
   - Durante a vida escolar do estudante, registros inativos ou corrigidos são marcados como inativos ou atualizados via trilha de auditoria.
   - Ao término do prazo regulamentar de retenção, a coordenação/administração executa o expurgo de dados sensíveis e narrativas de ocorrências, mantendo apenas dados estatísticos consolidados e anonimizados para fins de relatórios institucionais (sem identificação de nomes, CPFs ou matrículas).
2. **Destruição Segura de Mídias e Backups:**
   - Backups que excedem a política de retenção (7 dias diários, 4 semanas, 12 meses) são sobrescritos ou apagados com exclusão segura (zeroing ou descarte criptográfico).
   - Impressões físicas de ocorrências ou relatórios devem ser trituradas em fragmentadoras de corte cruzado após o cumprimento de sua finalidade.

---

## 4. Medidas Técnicas e Administrativas de Proteção

1. **Controle de Acesso Baseado em Perfis (RBAC):**
   - **Professores:** Visualizam e registram ocorrências das turmas e ocorrências sob sua autoria. Não possuem acesso a pareceres confidenciais externos (Conselho Tutelar, laudos médicos).
   - **Coordenação Pedagógica:** Acesso completo a despachos, encaminhamentos e tramitação de status.
   - **Administradores:** Gestão de usuários e parâmetros de sistema, sem permissão para adulterar o histórico de auditoria.
2. **Criptografia e Senhas:**
   - Senhas protegidas com algoritmos de hash robustos (`PBKDF2` com `SHA-256` / `Argon2`).
   - Sessões protegidas com cookies HttpOnly, SameSite e proteção contra Cross-Site Scripting (XSS) e CSRF ativos no Django.
3. **Auditoria Contínua:**
   - O modelo `HistoricoAlteracao` garante que nenhuma exclusão, alteração ou tramitação de status ocorra de maneira anônima.
