# Infraestrutura e Configuração

## Versões e Ambiente

### Python
- **Versão mínima:** Python 3.9+
- **Ambiente virtual:** `venv` (gestão isolada de dependências)

## Pacotes Python

### Core Framework
```python
langchain          # Framework principal para LLM applications
langsmith          # Cliente e avaliação LangSmith
langchain-openai   # Integração com OpenAI (GPT)
langchain-groq     # Integração com GROQ (alternativa econômica)
```

### Utilitários
```python
python-dotenv      # Gestão de variáveis de ambiente
pyyaml            # Manipulação de arquivos YAML
```

### Testes e Qualidade
```python
pytest            # Framework de testes
pytest-cov        # Cobertura de testes
```

## Modelos de IA

### GROQ (Principal - Custo-benefício) ⭐ RECOMENDADO

**Status:** ❌ Precisa ser adicionado ao código

- **Provider ID:** `groq` (para variável `LLM_PROVIDER`)
- **Modelo de resposta:** `mixtral-8x7b-32768` ou `llama2-70b-4096`
- **Modelo de avaliação:** `mixtral-8x7b-32768`
- **API Key:** Requer `GROQ_API_KEY` no `.env`
- **Vantagem:** Mais econômico que OpenAI, velocidade alta
- **Limites:** Consultar documentação oficial
- **Documentação:** https://console.groq.com/docs
- **Como obter API Key:** https://console.groq.com/keys

**Pacote necessário:**
```bash
pip install langchain-groq
```

**Uso no código:**
```python
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="mixtral-8x7b-32768",
    temperature=0.0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)
```

### OpenAI (Opcional/Referência)
- **Provider ID:** `openai` (para variável `LLM_PROVIDER`)
- **Modelo de resposta:** `gpt-4o-mini`
- **Modelo de avaliação:** `gpt-4o`
- **API Key:** Requer `OPENAI_API_KEY` no `.env`
- **Custo estimado:** ~$1-5 USD para completar o desafio
- **Documentação:** https://platform.openai.com/docs

### Google Gemini (Opcional/Free)
- **Provider ID:** `google` (para variável `LLM_PROVIDER`)
- **Modelo de resposta:** `gemini-1.5-flash`
- **Modelo de avaliação:** `gemini-1.5-pro` ou `gemini-1.5-flash`
- **API Key:** Requer `GOOGLE_API_KEY` no `.env`
- **Limite:** 15 req/min, 1500 req/dia (free tier)
- **Documentação:** https://ai.google.dev/

## Plataformas e Serviços

### LangSmith
- **Função:** Gestão de prompts, tracing e avaliação
- **Configuração necessária:**
  - `LANGSMITH_API_KEY`: API key da plataforma
  - `LANGSMITH_PROJECT`: Nome do projeto no LangSmith
- **URL:** https://smith.langchain.com/
- **Prompt Hub:** Repositório de prompts (`hub.pull()` e `hub.push()`)

## Estrutura de Variáveis de Ambiente

### Arquivo `.env` (template)
```bash
# LangSmith Configuration (OBRIGATÓRIO)
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=bug-to-user-story-optimization
LANGSMITH_TRACING=true

# LLM Provider Selection
# Opções: "groq", "openai", "google"
LLM_PROVIDER=groq

# GROQ Configuration (Principal - RECOMENDADO)
GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL=mixtral-8x7b-32768
EVAL_MODEL=mixtral-8x7b-32768

# OpenAI Configuration (Opcional)
# OPENAI_API_KEY=your_openai_api_key_here
# LLM_MODEL=gpt-4o-mini
# EVAL_MODEL=gpt-4o

# Google Configuration (Opcional)
# GOOGLE_API_KEY=your_google_api_key_here
# LLM_MODEL=gemini-1.5-flash
# EVAL_MODEL=gemini-1.5-flash
```

### Como obter as API Keys:

**LangSmith (obrigatório):**
1. Acesse https://smith.langchain.com/
2. Crie uma conta (use GitHub ou email)
3. Vá em Settings → API Keys
4. Crie uma nova API Key
5. Copie e cole no `.env`

**GROQ (recomendado):**
1. Acesse https://console.groq.com/
2. Crie uma conta
3. Vá em API Keys
4. Crie uma nova key
5. Copie e cole no `.env`

**OpenAI (opcional):**
1. Acesse https://platform.openai.com/api-keys
2. Crie uma conta e adicione créditos
3. Crie uma nova API Key
4. Copie e cole no `.env`

**Google (opcional):**
1. Acesse https://aistudio.google.com/app/apikey
2. Crie uma API Key
3. Copie e cole no `.env`

## Dependências do Sistema

### Linux/Ubuntu
```bash
python3-venv      # Para criar ambientes virtuais
python3-pip       # Gerenciador de pacotes Python
```

### Comandos de Instalação
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-venv python3-pip

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

## Formato de Dados

### Prompts
- **Formato:** YAML (`.yml`)
- **Localização:** `prompts/` directory
- **Versionamento:** v1 (original), v2 (otimizado)

### Datasets
- **Formato:** Python lists/dicts ou YAML
- **Conteúdo:** 15 exemplos de bugs (5 simples, 7 médios, 3 complexos)
- **Localização:** `src/dataset.py`

## Métricas de Avaliação

### Implementação Customizada
Localização: `src/metrics.py`

1. **Tone Score** (>= 0.9)
2. **Acceptance Criteria Score** (>= 0.9)
3. **User Story Format Score** (>= 0.9)
4. **Completeness Score** (>= 0.9)

**Critério de aprovação:** TODAS as métricas >= 0.9 (não apenas a média)

---

**Última atualização:** 16/01/2026
