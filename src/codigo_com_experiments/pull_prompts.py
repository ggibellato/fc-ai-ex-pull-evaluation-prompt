"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    """
    Faz pull do prompt do LangSmith Hub e salva localmente.
    
    Returns:
        bool: True se sucesso, False caso contrário
    """
    prompt_hub_name = "leonanluppi/bug_to_user_story_v1"
    output_file = "prompts/bug_to_user_story_v1.yml"
    
    try:
        print(f"Fazendo pull do prompt: {prompt_hub_name}")
        
        # Fazer pull do prompt do Hub
        prompt = hub.pull(prompt_hub_name)
        
        print(f"   ✓ Prompt obtido com sucesso do LangSmith Hub")
        
        # Converter prompt para dicionário YAML
        prompt_data = {
            "bug_to_user_story_v1": {
                "description": f"Prompt original do LangSmith Hub: {prompt_hub_name}",
                "system_prompt": "",
                "user_prompt": "{bug_report}",
                "version": "v1",
                "created_at": "2025-01-15",
                "tags": ["bug-analysis", "user-story", "product-management"],
            }
        }
        
        # Extrair system_prompt e user_prompt do objeto prompt
        if hasattr(prompt, 'messages'):
            for message in prompt.messages:
                if hasattr(message, 'prompt'):
                    if 'system' in message.__class__.__name__.lower():
                        prompt_data["bug_to_user_story_v1"]["system_prompt"] = message.prompt.template
                    elif 'human' in message.__class__.__name__.lower():
                        prompt_data["bug_to_user_story_v1"]["user_prompt"] = message.prompt.template
        elif hasattr(prompt, 'template'):
            # Se for um prompt simples
            prompt_data["bug_to_user_story_v1"]["system_prompt"] = prompt.template
        
        # Salvar em YAML
        if save_yaml(prompt_data, output_file):
            print(f"   ✓ Prompt salvo em: {output_file}")
            return True
        else:
            print(f"   ✗ Erro ao salvar arquivo YAML")
            return False
            
    except Exception as e:
        print(f"   ✗ Erro ao fazer pull do prompt: {e}")
        return False


def main():
    """Função principal"""
    print_section_header("Pull de Prompts do LangSmith Hub")
    
    # Verificar variáveis de ambiente necessárias
    required_vars = ['LANGSMITH_API_KEY']
    if not check_env_vars(required_vars):
        return 1
    
    print("\nIniciando pull dos prompts...\n")
    
    # Fazer pull do prompt v1 (ruim)
    if not pull_prompts_from_langsmith():
        print("\n❌ Falha ao fazer pull do prompt")
        return 1
    
    print("\n" + "="*50)
    print("✅ Pull concluído com sucesso!")
    print("="*50)
    print("\nPróximos passos:")
    print("1. Analise o prompt em prompts/bug_to_user_story_v1.yml")
    print("2. Crie uma versão otimizada em prompts/bug_to_user_story_v2.yml")
    print("3. Execute: python src/push_prompts.py")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
