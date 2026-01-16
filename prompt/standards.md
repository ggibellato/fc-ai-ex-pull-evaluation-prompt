# Padrões de Código e Documentação

## Convenções de Código Python

### Estilo Geral
- **Guia:** PEP 8 (Python Enhancement Proposal 8)
- **Indentação:** 4 espaços (sem tabs)
- **Comprimento de linha:** Máximo 88 caracteres (compatível com Black formatter)
- **Encoding:** UTF-8

### Nomenclatura

#### Variáveis e Funções
```python
# snake_case para funções e variáveis
def pull_prompts_from_hub():
    api_key = get_api_key()
    user_prompt = load_prompt_template()
```

#### Classes
```python
# PascalCase para classes
class PromptEvaluator:
    def __init__(self, model_name: str):
        self.model_name = model_name
```

#### Constantes
```python
# UPPER_SNAKE_CASE para constantes
MINIMUM_SCORE_THRESHOLD = 0.9
DEFAULT_MODEL_NAME = "mixtral-8x7b-32768"
```

### Type Hints
```python
# Sempre usar type hints para clareza
def evaluate_prompt(
    prompt: str, 
    dataset: list[dict], 
    model: str
) -> dict[str, float]:
    """
    Avalia um prompt usando dataset e retorna métricas.
    
    Args:
        prompt: Template do prompt a ser avaliado
        dataset: Lista de exemplos para teste
        model: Nome do modelo LLM
    
    Returns:
        Dicionário com scores das métricas
    """
    pass
```

## Estrutura de Arquivos

### Scripts Python (src/)
Cada script deve ter:
1. **Docstring no topo** explicando o propósito
2. **Imports organizados** (stdlib → third-party → local)
3. **Função main()** com `if __name__ == "__main__":`
4. **Error handling** apropriado

```python
"""
Script para fazer pull de prompts do LangSmith Hub.

Este módulo conecta ao LangSmith usando credenciais do .env
e baixa prompts específicos para otimização local.
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain import hub


def main():
    """Função principal de execução."""
    try:
        # Lógica principal
        pass
    except Exception as e:
        print(f"Erro: {e}")
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
```

### Arquivos YAML (prompts/)

```yaml
# Metadados obrigatórios
_metadata:
  version: "2.0"
  author: "seu_username"
  techniques:
    - "Few-shot Learning"
    - "Chain of Thought"
    - "Role Prompting"
  description: "Prompt otimizado para conversão de bugs em user stories"

# System prompt com contexto e persona
system: |
  Você é um Product Manager experiente...

# User prompt com template de variáveis
user: |
  Analise o seguinte bug e converta em user story:
  
  Bug: {bug_description}
```

## Documentação

### Comentários no Código
- **Quando usar:**
  - Explicar lógica complexa ou não-óbvia
  - Documentar workarounds ou decisões técnicas
  - Marcar TODOs temporários (evitar em código final)

```python
# BOM: Explica o "porquê"
# Usamos retry exponencial porque GROQ tem rate limit de 60 req/min
retry_strategy = ExponentialBackoff(max_retries=3)

# EVITAR: Redundante com o código
# Incrementa contador
counter += 1
```

### Docstrings (Padrão Google)
```python
def evaluate_with_metrics(prompt_name: str, dataset: list) -> dict:
    """
    Executa avaliação completa de um prompt usando dataset.
    
    Args:
        prompt_name: Nome do prompt no formato 'username/prompt_v2'
        dataset: Lista de dicionários com campos 'bug' e 'expected_story'
    
    Returns:
        Dicionário contendo:
            - tone_score: float (0-1)
            - criteria_score: float (0-1)
            - format_score: float (0-1)
            - completeness_score: float (0-1)
            - mean_score: float (0-1)
    
    Raises:
        ValueError: Se prompt_name não existir no LangSmith
        APIError: Se houver falha na comunicação com LLM
    """
    pass
```

## Testes

### Estrutura de Testes (tests/)
```python
import pytest
from pathlib import Path


class TestPromptValidation:
    """Suite de testes para validação de prompts."""
    
    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system' existe e não está vazio."""
        # Given
        prompt = load_prompt("prompts/bug_to_user_story_v2.yml")
        
        # When / Then
        assert "system" in prompt
        assert len(prompt["system"].strip()) > 0
    
    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona clara."""
        # Given
        prompt = load_prompt("prompts/bug_to_user_story_v2.yml")
        
        # When
        system_text = prompt["system"].lower()
        
        # Then
        role_indicators = ["você é", "você atua como", "seu papel"]
        assert any(indicator in system_text for indicator in role_indicators)
```

### Nomenclatura de Testes
- Prefixo `test_` obrigatório
- Nome descritivo do comportamento esperado
- Padrão: `test_<componente>_<cenário>_<resultado_esperado>`

## README.md

### Estrutura Obrigatória

```markdown
# Pull, Otimização e Avaliação de Prompts

## Visão Geral
[Descrição breve do projeto]

## Técnicas Aplicadas (Fase 2)
### 1. Few-shot Learning
**Por quê:** [Justificativa]
**Como aplicado:** [Exemplo prático]

### 2. Chain of Thought
**Por quê:** [Justificativa]
**Como aplicado:** [Exemplo prático]

## Resultados Finais
### Métricas Atingidas
| Métrica | v1 (ruim) | v2 (otimizado) | Status |
|---------|-----------|----------------|--------|
| Tone    | 0.45      | 0.94           | ✓      |
| ...     | ...       | ...            | ...    |

### Evidências
- [Link do Dashboard LangSmith](https://smith.langchain.com/...)
- Screenshots: [pasta /docs]

## Como Executar
### Pré-requisitos
[Lista de dependências e requisitos]

### Instalação
```bash
[Comandos passo a passo]
```

### Execução
```bash
[Comandos para cada fase]
```
```

## Git e Versionamento

### Mensagens de Commit
```bash
# Formato: <tipo>: <descrição breve>

feat: adiciona script de pull de prompts do LangSmith
fix: corrige validação de YAML em test_prompts.py
docs: atualiza README com seção de técnicas aplicadas
test: adiciona teste de few-shot examples
refactor: otimiza prompt v2 com role prompting
```

### Branch Strategy
- `main`: código estável e testado
- Feature branches: `feature/fase-<n>-<nome-descritivo>`

## Ferramentas Recomendadas

### Formatação e Linting
```bash
# Black - formatação automática
pip install black
black src/ tests/

# Flake8 - verificação de estilo
pip install flake8
flake8 src/ tests/ --max-line-length=88

# isort - organização de imports
pip install isort
isort src/ tests/
```

### Type Checking
```bash
pip install mypy
mypy src/ --ignore-missing-imports
```

---

**Última atualização:** 16/01/2026  
**Baseado em:** PEP 8, Google Python Style Guide, LangChain Best Practices
