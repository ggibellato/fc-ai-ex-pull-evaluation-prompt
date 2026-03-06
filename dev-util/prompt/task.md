#### Fase 1 — Setup inicial
**Referência:** Ver seção "Tecnologias obrigatórias" e "VirtualEnv para Python" em `prompt/exercise.md`

**IMPORTANTE:** O repositório base já contém estrutura inicial. Foco em complementar e configurar.

1. **[DONE]** Fazer fork do repositório base da FullCycle: https://github.com/devfullcycle/mba-ia-pull-evaluation-prompt
2. **[DONE]** Criar e ativar o ambiente virtual (`venv`).  
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **[DONE]** Verificar e complementar `requirements.txt` (já existe no fork):
   - ✅ Já inclusos: `langchain`, `langsmith`, `langchain-openai`, `langchain-google-genai`, `python-dotenv`, `pytest`, `pyyaml`
   - ✅ **ADICIONADO:** `langchain-groq==0.2.1` (requisito especial - usar GROQ como LLM principal por custo)
   
4. **[DONE]** Verificar e criar/complementar `.env.example` com variáveis necessárias:
   - ✅ `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, `LANGSMITH_TRACING` (obrigatório)
   - ✅ `GROQ_API_KEY` (principal - requisito especial por custo)
   - ✅ `OPENAI_API_KEY` (opcional - referência)
   - ✅ `LLM_PROVIDER` (para alternar entre providers: "groq", "openai", "google")
   
5. **[DONE]** Instalar dependências e adicionar suporte GROQ:
   ```bash
   pip install -r requirements.txt
   ```
   - ✅ Todas as dependências instaladas (80+ pacotes)
   - ✅ Suporte GROQ adicionado em `src/utils.py` função `get_llm()`
#### Fase 2 — Pull dos prompts ruins
**Referência:** Ver "1. Pull dos Prompt inicial do LangSmith" em `prompt/exercise.md`

**IMPORTANTE:** Script `src/pull_prompts.py` já existe no fork, mas com funções vazias (`...`). Foco em implementar a lógica.

6. **[DONE]** Implementar as funções vazias em `src/pull_prompts.py`:  
   - ✅ Conectar ao LangSmith Prompt Hub usando credenciais do `.env`
   - ✅ Fazer pull de `leonanluppi/bug_to_user_story_v1` (conforme especificado em `exercise.md`)
   - ✅ Usar `langchain.hub.pull()` para obter o prompt
   - ✅ Converter o prompt para formato YAML e salvar em `prompts/bug_to_user_story_v1.yml`
   - ✅ Implementado também `src/push_prompts.py` com validações
   
7. **[TODO]** Testar execução do pull (após configurar API keys):
   ```bash
   python src/pull_prompts.py
   ```
   Verificar:
   - Arquivo `prompts/bug_to_user_story_v1.yml` criado/atualizado
   - Formato YAML válido
   - Presença de campos essenciais (system_prompt, description, metadata)
#### Fase 3 — Análise e otimização de prompt
**Referência:** Ver "2. Otimização do Prompt" em `prompt/exercise.md`

8. **[DONE]** Analisar `bug_to_user_story_v1.yml` e identificar falhas:
   - ✅ Falta de persona/role definition
   - ✅ Imprecisão nas instruções
   - ✅ Ausência de exemplos (few-shot)
   - ✅ Falta de estruturação (skeleton/CoT)
   - ✅ Análise completa documentada em `prompt/context_update.md`
   
9. **[DONE]** Documentar diagnóstico detalhado em `prompt/context_update.md`.  
   - ✅ 6 problemas principais identificados
   - ✅ Métricas esperadas documentadas
   - ✅ Comparação v1 vs v2 criada
   
10. **[DONE]** Criar `prompts/bug_to_user_story_v2.yml` aplicando **5 técnicas** (acima do mínimo de 2):
    - ✅ **Role Prompting:** Product Manager experiente com 10+ anos
    - ✅ **Few-shot Learning:** 3 exemplos completos (simples, médio, complexo)
    - ✅ **Chain of Thought (CoT):** Processo explícito em 3 etapas
    - ✅ **Skeleton of Thought:** 4 seções estruturadas
    - ✅ **Tratamento de edge cases:** 3 cenários especiais cobertos
    
11. **[DONE]** Criar testes completos em `tests/test_prompts.py` validando **todos os requisitos de `exercise.md`**:
    - ✅ `test_prompt_has_system_prompt` - Campo existe e não está vazio
    - ✅ `test_prompt_has_role_definition` - Persona definida (ex: "Você é...")
    - ✅ `test_prompt_mentions_format` - Exige formato Markdown/User Story
    - ✅ `test_prompt_has_few_shot_examples` - Contém exemplos entrada/saída
    - ✅ `test_prompt_no_todos` - Nenhum [TODO] esquecido no texto
    - ✅ `test_minimum_techniques` - Pelo menos 2 técnicas listadas nos metadados YAML
    - ✅ **Resultado:** 9/9 testes passando
    
#### Fase 4 — Push e versionamento
**Referência:** Ver "3. Push e Avaliação" em `prompt/exercise.md`

**IMPORTANTE:** Script `src/push_prompts.py` já está implementado no fork com lógica funcional.

12. **[TODO]** Configurar USERNAME_LANGSMITH_HUB no `.env`:
   - Acessar https://smith.langchain.com/hub
   - Identificar seu username (geralmente parte antes do @ do email Google)
   - Adicionar ao `.env`: `USERNAME_LANGSMITH_HUB=seu_username`
   
13. **[TODO]** Testar execução do push:
   ```bash
   python src/push_prompts.py
   ```
   ```bash
   python src/push_prompts.py
   ```
   Verificar:
   - Prompt publicado com sucesso no LangSmith Hub
   - URL pública do prompt acessível
   - Metadados corretos visíveis no dashboard
#### Fase 5 — Avaliação e iteração
**Referência:** Ver "4. Iteração" e "Critério de Aprovação" em `prompt/exercise.md`

**IMPORTANTE:** 
- Script `src/evaluate.py` já está implementado no fork com lógica completa
- Dataset `datasets/bug_to_user_story.jsonl` já contém 15 exemplos (5 simples, 7 médios, 3 complexos)
- Métricas implementadas em `src/metrics.py`: **Tone Score, Acceptance Criteria Score, User Story Format Score, Completeness Score**
- Foco em executar, analisar e iterar

14. **[TODO]** Executar avaliação inicial do prompt v1 (ruim):
   ```bash
   python src/evaluate.py
   ```
   - Sistema deve automaticamente usar `leonanluppi/bug_to_user_story_v1` do LangSmith Hub
   - Documentar métricas baixas em `prompt/context_update.md`
   - Esperar scores < 0.9 (confirmando que v1 é realmente ruim)
   - Verificar no dashboard LangSmith: dataset criado e execuções registradas
   
15. **[TODO]** Após criar v2, executar avaliação do prompt otimizado:
   ```bash
   python src/evaluate.py
   ```
   - Sistema deve usar `{seu_username}/bug_to_user_story_v2` do LangSmith Hub
   - Analisar métricas e identificar problemas específicos (qual métrica está baixa?)
   
16. **[TODO]** Iteração (espera-se 3-5 ciclos conforme `exercise.md`):
   - Editar `prompts/bug_to_user_story_v2.yml` com melhorias baseadas nas métricas
   - Fazer push atualizado: `python src/push_prompts.py`
   - Avaliar novamente: `python src/evaluate.py`
   - Repetir até **TODAS** as 4 métricas >= 0.9
   - **IMPORTANTE:** Não apenas a média, mas TODAS individualmente >= 0.9
   - **Métricas obrigatórias:**
     - **Tone Score** >= 0.9 (tom profissional e empático)
     - **Acceptance Criteria Score** >= 0.9 (critérios de aceitação bem definidos)
     - **User Story Format Score** >= 0.9 (formato correto "Como... Eu quero... Para que...")
     - **Completeness Score** >= 0.9 (completude e contexto técnico)
   
17. **[TODO]** Registrar comparativo final v1 × v2 em `README.md`:
   - Tabela com as 4 métricas lado a lado mostrando evolução
   - Screenshots do dashboard LangSmith mostrando:
     * Dataset com 15 exemplos
     * Execuções do v1 com scores baixos
     * Execuções do v2 com scores >= 0.9
     * Tracing detalhado de pelo menos 3 exemplos
   - Link público do projeto no LangSmith  

#### Fase 6 — Documentação e entrega
**Referência:** Ver "Entregável" e seções obrigatórias do README em `prompt/exercise.md`

18. **[TODO]** Finalizar `README.md` com **três seções obrigatórias** (conforme `exercise.md`):
   
   **A) Seção "Técnicas Aplicadas (Fase 2)":**
   - Quais técnicas avançadas você escolheu (ex: Few-shot, CoT, Role Prompting)
   - Justificativa clara de por que escolheu cada técnica
   - Exemplos práticos de como aplicou cada técnica no prompt v2
   
   **B) Seção "Resultados Finais":**
   - Link público do dashboard LangSmith mostrando avaliações
   - Screenshots das avaliações com notas >= 0.9 atingidas
   - Tabela comparativa: prompts ruins (v1) vs otimizados (v2)
   - Evidências de >= 15 exemplos no dataset de avaliação
   - Tracing detalhado de pelo menos 3 exemplos
   
   **C) Seção "Como Executar":**
   - Instruções claras e detalhadas passo a passo
   - Pré-requisitos e dependências (Python 3.9+, venv, etc.)
   - Comandos para cada fase: pull → otimização → push → avaliação
   - Configuração do `.env` necessária

19. **[TODO]** Publicar evidências no LangSmith (conforme requisitos de `exercise.md`):
   - Dashboard público configurado
   - Dataset com >= 15 exemplos (5 simples, 7 médios, 3 complexos)
   - Execuções do prompt v1 com notas baixas visíveis
   - Execuções do prompt v2 com notas >= 0.9 visíveis
   - Tracing detalhado de pelo menos 3 exemplos

20. **[TODO]** Conferir checklist final antes da entrega:
   - [ ] Todos os arquivos obrigatórios presentes (conforme estrutura em `exercise.md`)
   - [ ] Prompt v2 100% preenchido e funcional
   - [ ] Testes passando: `pytest tests/test_prompts.py`
   - [ ] README.md completo com as 3 seções obrigatórias
   - [ ] Link público do LangSmith funcionando
   - [ ] Screenshots salvos e referenciados
   - [ ] Repositório público no GitHub
   - [ ] Todas as 4 métricas >= 0.9 confirmadas
***

## Notas Importantes

### Referências ao Exercício Oficial
Cada fase acima está **explicitamente referenciada** ao documento oficial `prompt/exercise.md`. Sempre consulte esse arquivo para:
- Requisitos formais e critérios de avaliação
- Estrutura obrigatória de arquivos
- Métricas e thresholds específicos (todas >= 0.9)
- Formato dos entregáveis (YAML, README sections, etc.)

### Requisitos Especiais do Projeto
- **LLM Principal:** GROQ (por questões de custo) - lembre-se de adicionar `GROQ_API_KEY` no `.env.example`
- **Alternativa:** OpenAI pode ser usada como referência opcional
- **Critério de Aprovação:** TODAS as 4 métricas >= 0.9 (não apenas média)
- **Iteração Esperada:** 3-5 ciclos de otimização normalmente necessários

### Workflow de Execução
1. **Nunca avance para próxima fase** sem revisão e confirmação explícita
2. **Atualize `prompt/context_update.md`** após cada tarefa concluída
3. **Marque tasks como [DONE]** em `prompt/task.md` após confirmação
4. **Commits e git são responsabilidade do aluno** (apenas sugira comandos)

### Arquivos Auxiliares Criados
- `prompt/context_update.md` - Histórico e progresso do projeto
- `prompt/infra.md` - Detalhes técnicos (pacotes, modelos, APIs)
- `prompt/standards.md` - Convenções de código e documentação

---

Essas revisões deixam o `task.md` **mais instrumentado**, **avaliável**, e **claramente incremental** — cada fase adiciona uma funcionalidade testável e documenta o resultado, refletindo diretamente nos critérios de avaliação do exercício oficial.