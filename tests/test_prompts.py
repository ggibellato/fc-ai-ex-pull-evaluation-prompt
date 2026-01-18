"""
Testes automatizados para validação de prompts.

Conforme requisitos do exercise.md, implementa 6 testes obrigatórios:
1. test_prompt_has_system_prompt
2. test_prompt_has_role_definition
3. test_prompt_mentions_format
4. test_prompt_has_few_shot_examples
5. test_prompt_no_todos
6. test_minimum_techniques
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

# Caminho para o prompt v2 otimizado
PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture
def prompt_v2():
    """Fixture que carrega o prompt v2 para os testes."""
    if not PROMPT_FILE.exists():
        pytest.skip(f"Arquivo {PROMPT_FILE} não encontrado")
    
    data = load_prompts(PROMPT_FILE)
    prompt_key = "bug_to_user_story_v2"
    
    if prompt_key not in data:
        pytest.fail(f"Chave '{prompt_key}' não encontrada no arquivo YAML")
    
    return data[prompt_key]


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_v2):
        """
        Teste 1: Verifica se o campo 'system_prompt' existe e não está vazio.
        
        Critério:
        - Campo 'system_prompt' deve existir
        - Não pode ser None
        - Não pode ser string vazia ou apenas whitespace
        """
        assert "system_prompt" in prompt_v2, "Campo 'system_prompt' não encontrado no prompt"
        
        system_prompt = prompt_v2["system_prompt"]
        assert system_prompt is not None, "Campo 'system_prompt' está None"
        assert isinstance(system_prompt, str), "Campo 'system_prompt' deve ser uma string"
        assert system_prompt.strip(), "Campo 'system_prompt' está vazio ou contém apenas espaços"
        
        # Verificar tamanho mínimo (deve ser substancial, não apenas uma linha)
        assert len(system_prompt.strip()) > 100, "Campo 'system_prompt' muito curto (< 100 caracteres)"

    def test_prompt_has_role_definition(self, prompt_v2):
        """
        Teste 2: Verifica se o prompt define uma persona clara.
        
        Critério:
        - Deve conter frases como "Você é um..." ou "Você é uma..."
        - Deve definir expertise/contexto do agente
        
        Exemplos aceitos:
        - "Você é um Product Manager experiente"
        - "Você é uma especialista em..."
        - "Você atua como..."
        """
        system_prompt = prompt_v2.get("system_prompt", "").lower()
        
        role_indicators = [
            "você é um",
            "você é uma",
            "você atua como",
            "seu papel é",
            "sua função é"
        ]
        
        has_role = any(indicator in system_prompt for indicator in role_indicators)
        assert has_role, (
            f"Prompt não define uma persona clara. "
            f"Esperado frases como: {', '.join(role_indicators)}"
        )

    def test_prompt_mentions_format(self, prompt_v2):
        """
        Teste 3: Verifica se o prompt exige formato específico.
        
        Critério:
        - Deve mencionar "Markdown" ou formatação específica
        - Deve mencionar "User Story" ou formato padrão
        - Deve especificar estrutura esperada (ex: "Como... Eu quero... Para que...")
        """
        full_prompt = (
            prompt_v2.get("system_prompt", "") + " " + 
            prompt_v2.get("user_prompt", "")
        ).lower()
        
        format_indicators = [
            "markdown",
            "user story",
            "como.*eu quero.*para que",
            "formato",
            "estrutura",
            "## ",  # Indicador de formatação Markdown
            "**",   # Indicador de formatação Markdown
        ]
        
        has_format = any(indicator in full_prompt for indicator in format_indicators)
        assert has_format, (
            "Prompt não especifica formato de saída esperado. "
            "Deve mencionar 'Markdown', 'User Story' ou estrutura específica"
        )

    def test_prompt_has_few_shot_examples(self, prompt_v2):
        """
        Teste 4: Verifica se o prompt contém exemplos (Few-shot Learning).
        
        Critério:
        - Deve conter pelo menos 2 exemplos completos
        - Exemplos devem ter entrada (Input/Bug Report) e saída (Output/User Story)
        - Deve usar palavras como "Exemplo", "Input", "Output"
        """
        system_prompt = prompt_v2.get("system_prompt", "").lower()
        
        # Verificar presença de indicadores de exemplos
        example_indicators = ["exemplo", "example", "input", "output"]
        has_example_keywords = sum(
            system_prompt.count(indicator) for indicator in example_indicators
        )
        
        assert has_example_keywords >= 4, (
            f"Prompt não contém exemplos suficientes (Few-shot Learning). "
            f"Encontrados {has_example_keywords} indicadores, esperado >= 4 "
            f"(para pelo menos 2 exemplos com Input/Output)"
        )
        
        # Verificar se há múltiplos exemplos (pelo menos 2)
        exemplo_count = system_prompt.count("exemplo")
        example_count = system_prompt.count("example")
        total_examples = exemplo_count + example_count
        
        assert total_examples >= 2, (
            f"Prompt deve conter pelo menos 2 exemplos. Encontrados: {total_examples}"
        )

    def test_prompt_no_todos(self, prompt_v2):
        """
        Teste 5: Garante que não há TODOs pendentes no prompt.
        
        Critério:
        - Não pode conter strings como "[TODO]", "TODO:", "FIXME", "XXX"
        - Valida em system_prompt, user_prompt e description
        """
        fields_to_check = {
            "system_prompt": prompt_v2.get("system_prompt", ""),
            "user_prompt": prompt_v2.get("user_prompt", ""),
            "description": prompt_v2.get("description", ""),
        }
        
        todo_markers = ["[todo]", "todo:", "fixme", "xxx", "hack:", "temp:"]
        
        for field_name, content in fields_to_check.items():
            content_lower = str(content).lower()
            for marker in todo_markers:
                assert marker not in content_lower, (
                    f"Campo '{field_name}' contém marcador pendente: '{marker}'. "
                    f"Remova todos os TODOs antes de finalizar o prompt."
                )

    def test_minimum_techniques(self, prompt_v2):
        """
        Teste 6: Verifica se pelo menos 2 técnicas foram documentadas.
        
        Critério:
        - Deve existir campo 'techniques' nos metadados
        - Deve conter lista com pelo menos 2 técnicas
        - Técnicas esperadas: Few-shot, CoT, Role Prompting, Skeleton, etc.
        
        Conforme exercise.md: "Aplicar pelo menos duas das seguintes técnicas..."
        """
        assert "techniques" in prompt_v2, (
            "Campo 'techniques' não encontrado nos metadados do prompt. "
            "Adicione uma lista documentando as técnicas aplicadas."
        )
        
        techniques = prompt_v2["techniques"]
        assert isinstance(techniques, list), "Campo 'techniques' deve ser uma lista"
        assert len(techniques) >= 2, (
            f"Prompt deve aplicar pelo menos 2 técnicas. "
            f"Encontradas: {len(techniques)}"
        )
        
        # Validar que cada técnica tem descrição mínima
        for i, technique in enumerate(techniques, 1):
            assert technique.strip(), f"Técnica {i} está vazia"
            assert len(technique.strip()) > 10, (
                f"Técnica {i} muito curta: '{technique}'. "
                f"Forneça descrição mais detalhada."
            )


class TestPromptMetadata:
    """Testes adicionais para validar metadados do prompt."""
    
    def test_has_version(self, prompt_v2):
        """Verifica se o prompt possui campo de versão."""
        assert "version" in prompt_v2, "Campo 'version' não encontrado"
        assert prompt_v2["version"] in ["v2", "2", "2.0"], (
            f"Versão incorreta: {prompt_v2['version']}. Esperado: v2"
        )
    
    def test_has_tags(self, prompt_v2):
        """Verifica se o prompt possui tags descritivas."""
        assert "tags" in prompt_v2, "Campo 'tags' não encontrado"
        tags = prompt_v2["tags"]
        assert isinstance(tags, list), "Campo 'tags' deve ser uma lista"
        assert len(tags) >= 3, f"Prompt deve ter pelo menos 3 tags. Encontradas: {len(tags)}"
    
    def test_has_description(self, prompt_v2):
        """Verifica se o prompt possui descrição."""
        assert "description" in prompt_v2, "Campo 'description' não encontrado"
        description = prompt_v2["description"]
        assert description.strip(), "Campo 'description' está vazio"
        assert len(description) > 50, "Descrição muito curta (< 50 caracteres)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
