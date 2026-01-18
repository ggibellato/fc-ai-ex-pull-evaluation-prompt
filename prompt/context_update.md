# Context Update

## Histórico de Atualizações

### 16/01/2026 - Análise Completa do Fork

#### ✅ Análise do Repositório Base Concluída

**Status:** ANÁLISE COMPLETA

**Descobertas importantes:**

**1. Estrutura já implementada no fork:**
- ✅ Todos os diretórios criados: `src/`, `tests/`, `prompts/`, `datasets/`
- ✅ Scripts base existem: `pull_prompts.py`, `push_prompts.py`, `evaluate.py`, `metrics.py`, `utils.py`
- ✅ Testes base: `tests/test_prompts.py` (esqueleto criado, precisa implementar)
- ✅ Dataset completo: `datasets/bug_to_user_story.jsonl` com 15 exemplos
  - 5 simples (IDs: botão carrinho, validação email, iOS landscape, contagem users, imagens Safari)
  - 7 médios (webhook, relatório lento, permissões, pipeline desconto, app trava, carrinho estoque, modal z-index)
  - 3 complexos (checkout múltiplas falhas, relatórios performance, app offline sync)
- ✅ Prompt v1 exemplo: `prompts/bug_to_user_story_v1.yml` (será sobrescrito no pull real)
- ✅ `requirements.txt` já existe com pacotes principais

**2. O que precisa ser complementado:**
- ❌ **ADICIONAR `langchain-groq`** ao `requirements.txt`
- ❌ Verificar/criar `.env.example` com `GROQ_API_KEY`
- ❌ Implementar funções vazias (marcadas com `...`) nos scripts:
  - `src/pull_prompts.py` - função `pull_prompts_from_langsmith()` e `main()`
  - `src/push_prompts.py` - funções `push_prompt_to_langsmith()`, `validate_prompt()` e `main()`
- ❌ Implementar testes em `tests/test_prompts.py` (6 testes obrigatórios)
- ❌ Criar `prompts/bug_to_user_story_v2.yml` com prompt otimizado

**3. Métricas implementadas (em `src/metrics.py`):**
O código já implementa **7 métricas completas**:

**Métricas gerais (3):**
1. `evaluate_f1_score()` - F1-Score (precision + recall)
2. `evaluate_clarity()` - Clareza e estrutura
3. `evaluate_precision()` - Informações corretas e relevantes

**Métricas específicas para Bug to User Story (4):**
4. `evaluate_tone_score()` - Tom profissional e empático
5. `evaluate_acceptance_criteria_score()` - Qualidade dos critérios de aceitação
6. `evaluate_user_story_format_score()` - Formato correto (Como... Eu quero... Para que...)
7. `evaluate_completeness_score()` - Completude e contexto técnico

**Critério de aprovação (conforme `exercise.md`):**
- ✅ Tone Score >= 0.9
- ✅ Acceptance Criteria Score >= 0.9
- ✅ User Story Format Score >= 0.9
- ✅ Completeness Score >= 0.9
- ✅ MÉDIA das 4 >= 0.9
- **IMPORTANTE:** TODAS as 4 devem estar >= 0.9 individualmente!

**4. Suporte multi-provider implementado:**
O código em `src/utils.py` já suporta múltiplos providers:
- ✅ OpenAI (gpt-4o, gpt-4o-mini)
- ✅ Google Gemini (gemini-1.5-flash, gemini-1.5-pro)
- ❌ **GROQ precisa ser adicionado** (usando `langchain-groq`)

Configuração via `.env`:
```bash
LLM_PROVIDER=groq  # ou "openai" ou "google"
```

**5. Dataset de avaliação:**
- ✅ 15 exemplos já prontos em `datasets/bug_to_user_story.jsonl`
- ✅ Formato JSONL correto: `{"inputs": {...}, "outputs": {...}, "metadata": {...}}`
- ✅ Complexidade balanceada: 5 simples + 7 médios + 3 complexos
- ✅ Domínios variados: e-commerce, SaaS, mobile, CRM, ERP
- ✅ Tipos variados: UI/UX, segurança, performance, lógica de negócio, integração

**Ações realizadas:**
- ✅ Análise completa de todos os arquivos principais do fork
- ✅ Identificação das funções que precisam ser implementadas
- ✅ Atualização do `prompt/task.md` com contexto real do fork
- ✅ Documentação das métricas implementadas
- ✅ Mapeamento do que está pronto vs. o que precisa ser feito

**Próximos passos (Fase 1):**
1. ✅ Adicionar `langchain-groq` ao `requirements.txt`
2. ✅ Verificar/complementar `.env.example` com GROQ_API_KEY
3. ✅ Criar ambiente virtual e instalar dependências
4. ✅ Adicionar suporte GROQ no código `src/utils.py`

---

### 16/01/2026 - Fase 1: Setup Inicial CONCLUÍDA ✅

**Status:** FASE 1 COMPLETA

**Ações realizadas:**

1. ✅ **Adicionado `langchain-groq==0.2.1`** ao `requirements.txt`
   - Pacote necessário para usar GROQ como provider LLM

2. ✅ **Atualizado `.env.example`** com configuração completa:
   - Adicionado `GROQ_API_KEY` (provider recomendado)
   - Organizado por provider: GROQ (recomendado), Google (free), OpenAI (pago)
   - Configuração padrão: GROQ com `mixtral-8x7b-32768`
   - Comentários explicativos sobre cada opção

3. ✅ **Adicionado suporte GROQ** em `src/utils.py`:
   - Implementado bloco `elif provider == 'groq'` na função `get_llm()`
   - Importa `ChatGroq` de `langchain_groq`
   - Valida `GROQ_API_KEY` do `.env`
   - Retorna instância configurada de ChatGroq
   - Atualizada mensagem de erro para incluir 'groq' como opção válida

4. ✅ **Criado ambiente virtual** (`venv/`):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. ✅ **Instaladas todas as dependências**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
   - Todos os pacotes instalados com sucesso
   - `langchain-groq` instalado e pronto para uso
   - Total de 80+ pacotes incluindo dependências transitivas

**Arquivos modificados:**
- ✅ `requirements.txt` - Adicionado langchain-groq
- ✅ `.env.example` - Configuração completa com GROQ
- ✅ `src/utils.py` - Suporte GROQ na função get_llm()

**Próximos passos (Fase 2):**
1. ✅ Copiar `.env.example` para `.env` e configurar API keys
2. ✅ Implementar funções vazias em `src/pull_prompts.py`
3. ⏳ Testar pull do prompt v1 do LangSmith Hub (após configurar LANGSMITH_API_KEY)
4. ⏳ Verificar arquivo `prompts/bug_to_user_story_v1.yml` gerado

---

### 16/01/2026 - Fase 2: Pull de Prompts IMPLEMENTADA ✅

**Status:** CÓDIGO IMPLEMENTADO - AGUARDANDO CONFIGURAÇÃO DE API KEYS

**Ações realizadas:**

1. ✅ **Criado arquivo `.env`** baseado no template:
   ```bash
   cp .env.example .env
   ```
   - Usuário vai configurar suas API keys manualmente
   - Arquivo já no `.gitignore` (segurança)

2. ✅ **Implementado `src/pull_prompts.py`** - Funções completas:
   - `pull_prompts_from_langsmith()` - Faz pull do Hub e converte para YAML
   - `main()` - Função principal com validações e feedback
   - Lógica para extrair system_prompt e user_prompt do objeto prompt
   - Tratamento de erros e mensagens informativas
   - Salva em `prompts/bug_to_user_story_v1.yml`

3. ✅ **Implementado `src/push_prompts.py`** - Funções completas:
   - `push_prompt_to_langsmith()` - Publica prompt no Hub (público)
   - `validate_prompt()` - Valida estrutura e campos obrigatórios
   - `main()` - Fluxo completo: carregar → validar → push
   - Suporte para USERNAME_LANGSMITH_HUB do `.env`
   - Cria ChatPromptTemplate e faz push com `new_repo_is_public=True`

**Validações implementadas em `validate_prompt()`:**
- ✅ Campos obrigatórios: system_prompt, description, version
- ✅ system_prompt não pode estar vazio
- ✅ Não pode conter TODOs
- ✅ Mínimo de 2 técnicas aplicadas (se campo existir)

**Arquivos implementados:**
- ✅ `src/pull_prompts.py` - Pull completo
- ✅ `src/push_prompts.py` - Push e validação completos
- ✅ `.env` - Criado (usuário vai configurar)

**Próximos passos (Fase 3):**
1. Usuário configura API keys no `.env` (LANGSMITH_API_KEY, GROQ_API_KEY)
2. Executar `python src/pull_prompts.py` para baixar prompt v1
3. Analisar `prompts/bug_to_user_story_v1.yml` e identificar problemas
4. Criar `prompts/bug_to_user_story_v2.yml` com otimizações
5. Aplicar pelo menos 2 técnicas: Few-shot, CoT, Role Prompting, etc.

---

### 16/01/2026 - Fase 1 Iniciada

#### ✅ Item 1 Completo - Fork e Clone do Repositório

**Status:** CONCLUÍDO

**Ações realizadas:**
- Fork criado com sucesso de https://github.com/devfullcycle/mba-ia-pull-evaluation-prompt
- Repositório clonado em `/home/gleison/dev/fullcycle-mba-ai/exercicios/fc-ai-ex-pull-evaluation-prompt`
- Arquivos auxiliares copiados da pasta `prompt/` para o fork
- Estrutura confirmada: `src/`, `tests/`, `prompts/`, `datasets/` já existentes no repositório base

**Observações importantes:**
- Repositório base já possui `.env.example` e `requirements.txt` - verificar se precisa complementar com GROQ
- Trabalho daqui para frente será exclusivamente no diretório do fork
- Diretório de planejamento original será removido após setup completo

**Próximo passo:**
- Item 2: Criar e ativar ambiente virtual (venv)
- Verificar e complementar `requirements.txt` (adicionar langchain-groq)
- Verificar e complementar `.env.example` (adicionar GROQ_API_KEY)

**Contexto técnico:**
- Instrução especial: uso de GROQ como LLM principal por questões de custo
- Todas as tarefas executadas de forma iterativa com aprovação entre etapas

---

### 16/01/2026 - Inicialização do Projeto

**Status:** Arquivos auxiliares criados

**Ações realizadas:**
- Criação da estrutura de documentação auxiliar
- Arquivos inicializados: `context_update.md`, `infra.md`, `standards.md`
- Ajuste do `task.md` para incluir referências explícitas ao `exercise.md`

---

### 18/01/2026 - Fase 2: Pull dos Prompts CONCLUÍDA ✅

**Status:** PULL EXECUTADO COM SUCESSO

**Ações realizadas:**

1. ✅ **Configuração do LangSmith validada**
   - LANGSMITH_API_KEY configurado e funcional
   - LANGSMITH_PROJECT criado: `fc-ai-ex-pull-evaluation-prompt`
   - Credenciais validadas com sucesso

2. ✅ **Pull do prompt v1 executado**
   ```bash
   python src/pull_prompts.py
   ```
   - Prompt `leonanluppi/bug_to_user_story_v1` baixado com sucesso
   - Salvo em `prompts/bug_to_user_story_v1.yml`
   - Formato YAML válido

**Conteúdo do prompt v1 baixado:**
```yaml
system_prompt: "Você é um assistente que ajuda a transformar relatos de bugs..."
user_prompt: "{bug_report}"
```

**Próxima fase:** Fase 3 - Análise e Otimização

---

### 18/01/2026 - Fase 3: Análise do Prompt v1

**Status:** ANÁLISE COMPLETA

**Problemas identificados no prompt v1:**

1. **❌ Role Definition genérica e vaga**
   - Apenas "assistente que ajuda" - muito genérico
   - Sem persona específica (Product Manager, Analista de Negócio)
   - Sem contexto de expertise ou experiência
   - Sem definir responsabilidades claras

2. **❌ Instruções imprecisas**
   - "crie uma user story" - sem especificar formato
   - Não menciona estrutura "Como... Eu quero... Para que..."
   - Sem exigir critérios de aceitação
   - Sem orientações sobre formato Markdown
   - Sem definir nível de detalhe esperado

3. **❌ Zero exemplos (Few-shot Learning ausente)**
   - Nenhum exemplo de entrada/saída
   - Modelo não tem referência de qualidade esperada
   - Sem exemplos de diferentes complexidades
   - Dificulta calibração do modelo

4. **❌ Falta de estruturação (Skeleton/CoT)**
   - Sem guiar o raciocínio passo a passo
   - Sem instruções de etapas claras (análise → estruturação → geração)
   - Sem orientações sobre análise de impacto
   - Sem mencionar priorização

5. **❌ Tratamento de edge cases inexistente**
   - Sem orientações para bugs complexos
   - Sem instruções para bugs vagos ou incompletos
   - Sem lidar com informações faltantes
   - Sem estratégia para ambiguidades

6. **❌ Tom e formato não especificados**
   - Sem definir tom profissional/empático
   - Sem exigir Markdown
   - Sem padrões de formatação
   - Sem definir audience (desenvolvedores vs. stakeholders)

**Métricas esperadas para o prompt v1:**
- Tone Score: ~0.4-0.5 (tom muito genérico)
- Acceptance Criteria Score: ~0.3-0.4 (não menciona critérios)
- User Story Format Score: ~0.3-0.5 (não especifica formato padrão)
- Completeness Score: ~0.4-0.5 (faltam detalhes técnicos)

**Objetivo da otimização:**
- ✅ Tone Score >= 0.9
- ✅ Acceptance Criteria Score >= 0.9
- ✅ User Story Format Score >= 0.9
- ✅ Completeness Score >= 0.9

**Próximo passo:** Criar prompt v2 com técnicas avançadas

---

### 18/01/2026 - Fase 3: Otimização do Prompt CONCLUÍDA ✅

**Status:** PROMPT V2 CRIADO E VALIDADO

**Ações realizadas:**

1. ✅ **Criação do prompt v2 otimizado**
   - Arquivo: `prompts/bug_to_user_story_v2.yml`
   - Tamanho: ~14KB (vs. ~500B do v1)
   - Estrutura completa e profissional

2. ✅ **Técnicas aplicadas (5 técnicas - acima do mínimo de 2):**
   - **Role Prompting:** Product Manager experiente com 10+ anos, domínio em metodologias ágeis
   - **Few-shot Learning:** 3 exemplos completos (simples, médio, complexo)
   - **Chain of Thought:** Processo explícito em 3 etapas (Análise → Identificação → Estruturação)
   - **Skeleton of Thought:** 4 seções estruturadas (User Story, Contexto Técnico, Critérios, Impacto)
   - **Tratamento de edge cases:** Instruções para bugs vagos, críticos e multi-sistema

3. ✅ **Melhorias implementadas:**
   - ✅ Definição clara de persona e expertise
   - ✅ Formato Markdown padronizado com seções
   - ✅ Critérios de aceitação específicos e testáveis
   - ✅ Análise de impacto e prioridade estruturada
   - ✅ Tom empático e orientado a valor
   - ✅ Instruções de boas práticas e antipadrões
   - ✅ Exemplos cobrindo 3 níveis de complexidade

4. ✅ **Implementação dos 6 testes obrigatórios**
   - Arquivo: `tests/test_prompts.py`
   - Testes implementados:
     1. `test_prompt_has_system_prompt` ✅
     2. `test_prompt_has_role_definition` ✅
     3. `test_prompt_mentions_format` ✅
     4. `test_prompt_has_few_shot_examples` ✅
     5. `test_prompt_no_todos` ✅
     6. `test_minimum_techniques` ✅
   - Testes adicionais: metadata, versão, tags, descrição
   - **Resultado:** 9/9 testes PASSOU ✅

**Comparação v1 vs v2:**

| Aspecto | v1 (Original) | v2 (Otimizado) |
|---------|---------------|----------------|
| Tamanho | ~500 bytes | ~14KB |
| Role Definition | Genérica | Product Manager experiente (detalhado) |
| Instruções | Vagas | Processo passo a passo explícito |
| Exemplos | 0 | 3 (simples, médio, complexo) |
| Formato | Não especificado | Markdown padronizado com seções |
| Critérios de aceitação | Não mencionado | Instruções detalhadas |
| Edge cases | Ausente | 3 cenários cobertos |
| Técnicas aplicadas | 0 | 5 técnicas documentadas |
| Testes | 0 | 9 testes passando |

**Próxima fase:** Fase 4 - Push do prompt otimizado para o LangSmith Hub

---
