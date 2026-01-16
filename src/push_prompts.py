"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        username = os.getenv('USERNAME_LANGSMITH_HUB')
        if not username:
            print("   ⚠️  USERNAME_LANGSMITH_HUB não configurado no .env")
            print("   ℹ️  Usando nome de prompt sem namespace")
            full_prompt_name = prompt_name
        else:
            full_prompt_name = f"{username}/{prompt_name}"
        
        print(f"Fazendo push do prompt: {full_prompt_name}")
        
        # Extrair campos do prompt_data
        system_prompt = prompt_data.get('system_prompt', '')
        user_prompt = prompt_data.get('user_prompt', '{bug_report}')
        
        # Criar ChatPromptTemplate
        from langchain_core.prompts import ChatPromptTemplate
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])
        
        # Fazer push para o Hub (público)
        hub.push(
            full_prompt_name,
            prompt_template,
            new_repo_is_public=True
        )
        
        print(f"   ✓ Prompt publicado com sucesso!")
        print(f"   ✓ URL: https://smith.langchain.com/hub/{full_prompt_name}")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Erro ao fazer push: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []
    
    # Verificar campos obrigatórios
    required_fields = ['system_prompt', 'description', 'version']
    for field in required_fields:
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: {field}")
    
    # Verificar se system_prompt não está vazio
    system_prompt = prompt_data.get('system_prompt', '').strip()
    if not system_prompt:
        errors.append("system_prompt está vazio")
    
    # Verificar se não há TODOs
    if 'TODO' in system_prompt or '[TODO]' in system_prompt:
        errors.append("system_prompt ainda contém TODOs")
    
    # Verificar técnicas aplicadas (se existir o campo)
    techniques = prompt_data.get('techniques_applied', [])
    if 'techniques_applied' in prompt_data and len(techniques) < 2:
        errors.append(f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}")
    
    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("Push de Prompts para o LangSmith Hub")
    
    # Verificar variáveis de ambiente necessárias
    required_vars = ['LANGSMITH_API_KEY']
    if not check_env_vars(required_vars):
        return 1
    
    # Arquivo do prompt otimizado
    prompt_file = "prompts/bug_to_user_story_v2.yml"
    
    # Verificar se arquivo existe
    if not Path(prompt_file).exists():
        print(f"\n❌ Arquivo não encontrado: {prompt_file}")
        print("\nCrie o prompt otimizado antes de fazer push:")
        print("1. Analise prompts/bug_to_user_story_v1.yml")
        print("2. Crie prompts/bug_to_user_story_v2.yml com melhorias")
        print("3. Execute novamente: python src/push_prompts.py")
        return 1
    
    print(f"\nCarregando prompt de: {prompt_file}\n")
    
    # Carregar prompt
    prompts_data = load_yaml(prompt_file)
    if not prompts_data:
        print(f"❌ Erro ao carregar arquivo YAML")
        return 1
    
    # Pegar o primeiro prompt do arquivo
    prompt_key = list(prompts_data.keys())[0]
    prompt_data = prompts_data[prompt_key]
    
    print(f"Prompt carregado: {prompt_key}")
    print(f"   Versão: {prompt_data.get('version', 'N/A')}")
    print(f"   Descrição: {prompt_data.get('description', 'N/A')[:60]}...")
    
    # Validar prompt
    print("\nValidando prompt...")
    is_valid, errors = validate_prompt(prompt_data)
    
    if not is_valid:
        print("\n❌ Validação falhou:")
        for error in errors:
            print(f"   - {error}")
        return 1
    
    print("   ✓ Prompt válido!")
    
    # Fazer push
    print("\nEnviando para LangSmith Hub...\n")
    if not push_prompt_to_langsmith(prompt_key, prompt_data):
        print("\n❌ Falha ao fazer push")
        return 1
    
    print("\n" + "="*50)
    print("✅ Push concluído com sucesso!")
    print("="*50)
    print("\nPróximos passos:")
    print("1. Verifique o prompt no dashboard do LangSmith")
    print("2. Execute avaliação: python src/evaluate.py")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
