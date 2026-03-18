"""
Script de diagnóstico para problemas com prompts no LangSmith Hub.

Este script ajuda a identificar e resolver problemas como:
- Prompts que existem mas não aparecem na UI
- Conflitos de nomes
- Problemas de namespace/permissões
- Prompts públicos vs privados

Uso:
    python src/prompt_debug.py
"""

import os
from dotenv import load_dotenv
from langsmith import Client
from langchain import hub

load_dotenv()


def list_all_prompts(client: Client):
    """Lista todos os prompts no workspace/hub."""
    print("\n" + "=" * 70)
    print("📋 LISTANDO SEUS PROMPTS NO LANGSMITH")
    print("=" * 70 + "\n")
    
    try:
        username = os.getenv('USERNAME_LANGSMITH_HUB', '')
        
        # client.list_prompts() retorna um objeto ListPromptsResponse com atributos .repos e .total
        prompts_response = client.list_prompts()
        
        prompts_list = prompts_response.repos
        total = prompts_response.total
        
        # Filtrar apenas prompts do usuário
        if username:
            my_prompts = [p for p in prompts_list if getattr(p, 'owner', None) == username]
            print(f"   Seu username: {username}")
            print(f"   Total de prompts públicos no hub: {total}")
            print(f"   Seus prompts: {len(my_prompts)}\n")
        else:
            my_prompts = prompts_list
            print(f"   ⚠️  USERNAME_LANGSMITH_HUB não configurado - mostrando todos")
            print(f"   Total de prompts no hub: {total}\n")
        
        if not my_prompts:
            print("   ℹ️  Você ainda não criou nenhum prompt.")
            print("   💡 Para criar um prompt:")
            print("      1. Use python src/push_prompts.py")
            print("      2. Ou crie manualmente no LangSmith Hub")
            return
        
        print("   " + "=" * 66)
        for i, prompt in enumerate(my_prompts, 1):
            # Atributos chave do prompt
            handle = getattr(prompt, 'repo_handle', getattr(prompt, 'full_name', 'N/A'))
            full_name = getattr(prompt, 'full_name', handle)
            desc = getattr(prompt, 'description', 'N/A')
            is_public = getattr(prompt, 'is_public', 'N/A')
            created = getattr(prompt, 'created_at', 'N/A')
            commits = getattr(prompt, 'num_commits', 0)
            downloads = getattr(prompt, 'num_downloads', 0)
            
            print(f"\n   {i}. {full_name}")
            print(f"      Descrição: {desc[:80]}..." if desc and len(str(desc)) > 80 else f"      Descrição: {desc}")
            print(f"      Público: {is_public}")
            print(f"      Criado em: {created}")
            print(f"      Commits: {commits} | Downloads: {downloads}")
            print(f"      URL: https://smith.langchain.com/hub/{full_name}")
            print("      " + "-" * 62)
            
    except Exception as e:
        print(f"   ❌ Erro ao listar prompts: {e}")
        print(f"   💡 Tipo do erro: {type(e).__name__}")
        import traceback
        print(f"   Stack trace:")
        traceback.print_exc()


def delete_prompt(client: Client, handle: str):
    """
    Deleta um prompt do LangSmith Hub.
    
    Args:
        client: Cliente do LangSmith
        handle: Handle do prompt (ex: 'username/prompt-name' ou 'prompt-name')
    """
    print("\n" + "=" * 70)
    print(f"🗑️  DELETAR PROMPT: {handle}")
    print("=" * 70 + "\n")
    
    try:
        # Primeiro verificar se o prompt existe
        prompts_response = client.list_prompts()
        prompts_list = prompts_response.repos
        
        username = os.getenv('USERNAME_LANGSMITH_HUB', '')
        found = None
        found_handle = None
        found_full_name = None
        
        for prompt in prompts_list:
            prompt_handle = getattr(prompt, 'repo_handle', None)
            prompt_full_name = getattr(prompt, 'full_name', None)
            prompt_owner = getattr(prompt, 'owner', None)
            
            # Verificar se corresponde (com ou sem username)
            matches = False
            if prompt_full_name == handle:
                matches = True
            elif prompt_handle == handle:
                matches = True
            elif prompt_full_name and prompt_full_name.endswith(f"/{handle}"):
                matches = True
            
            if matches:
                # Verificar se é do usuário
                if prompt_owner != username:
                    print(f"   ⚠️  Este prompt pertence a '{prompt_owner}', não a você ('{username}')!")
                    print(f"   Você só pode deletar seus próprios prompts.")
                    return
                
                found = prompt
                found_handle = prompt_handle
                found_full_name = prompt_full_name
                break
        
        if not found:
            print(f"   ❌ Prompt '{handle}' não encontrado.")
            print(f"   💡 Use a opção 1 para listar seus prompts.")
            return
        
        # Mostrar informações do prompt
        print(f"   Prompt encontrado:")
        print(f"   Nome: {found_handle}")
        print(f"   Full name: {found_full_name}")
        print(f"   Descrição: {getattr(found, 'description', 'N/A')}")
        print(f"   Commits: {getattr(found, 'num_commits', 0)}")
        print(f"   Downloads: {getattr(found, 'num_downloads', 0)}")
        
        # Pedir confirmação
        print(f"\n   ⚠️  ATENÇÃO: Esta ação não pode ser desfeita!")
        confirmation = input(f"\n   Digite 'DELETE' para confirmar a exclusão: ").strip()
        
        if confirmation != 'DELETE':
            print(f"\n   ℹ️  Operação cancelada.")
            return
        
        # Deletar o prompt
        print(f"\n   Deletando prompt...")
        
        # Usar o método do client
        prompt_owner = getattr(found, 'owner', username)
        
        # O delete_prompt aceita owner/repo_handle ou apenas o repo_handle
        # Vamos tentar com o full_name primeiro
        try:
            print(f"   Debug: Tentando deletar '{found_full_name}'")
            client.delete_prompt(found_full_name)
            print(f"   ✅ Prompt deletado com sucesso!")
            print(f"   O prompt '{found_full_name}' foi removido do LangSmith Hub.")
        except Exception as delete_error:
            print(f"   ❌ Erro ao deletar prompt: {delete_error}")
            print(f"   💡 Você pode tentar deletar manualmente em:")
            print(f"      https://smith.langchain.com/hub/{found_full_name}")
            
    except Exception as e:
        print(f"   ❌ Erro ao deletar prompt: {e}")
        import traceback
        traceback.print_exc()


def list_all_public_prompts(client: Client, limit: int = 100):
    """Lista os primeiros N prompts públicos do hub."""
    print("\n" + "=" * 70)
    print(f"📋 LISTANDO PROMPTS PÚBLICOS (primeiros {limit})")
    print("=" * 70 + "\n")
    
    try:
        # client.list_prompts() retorna um objeto ListPromptsResponse com atributos .repos e .total
        prompts_response = client.list_prompts()
        
        prompts_list = prompts_response.repos[:limit]
        total = prompts_response.total
        
        print(f"   Total de prompts públicos no hub: {total}")
        print(f"   Mostrando os primeiros {len(prompts_list)} prompts:\n")
        
        for i, prompt in enumerate(prompts_list, 1):
            handle = getattr(prompt, 'repo_handle', getattr(prompt, 'full_name', 'N/A'))
            full_name = getattr(prompt, 'full_name', handle)
            owner = getattr(prompt, 'owner', 'N/A')
            desc = getattr(prompt, 'description', 'N/A')
            downloads = getattr(prompt, 'num_downloads', 0)
            
            print(f"   {i}. {full_name}")
            print(f"      Owner: {owner}")
            if desc and desc != 'N/A':
                print(f"      Descrição: {desc[:60]}..." if len(str(desc)) > 60 else f"      Descrição: {desc}")
            print(f"      Downloads: {downloads}")
            print()
            
    except Exception as e:
        print(f"   ❌ Erro ao listar prompts: {e}")
        import traceback
        traceback.print_exc()


def find_prompt_by_handle(client: Client, handle: str):
    """
    Busca um prompt específico por handle.
    
    Args:
        client: Cliente do LangSmith
        handle: Handle do prompt (ex: 'username/prompt-name' ou 'prompt-name')
    """
    print("\n" + "=" * 70)
    print(f"🔍 BUSCANDO PROMPT: {handle}")
    print("=" * 70 + "\n")
    
    try:
        # Obter lista de prompts do LangSmith
        prompts_response = client.list_prompts()
        prompts_list = prompts_response.repos
        
        found = None
        found_handle = None
        
        for prompt in prompts_list:
            # Obter handle do prompt
            prompt_handle = getattr(prompt, 'repo_handle', getattr(prompt, 'full_name', None))
            
            if prompt_handle and (prompt_handle == handle or prompt_handle.endswith(f"/{handle}")):
                found = prompt
                found_handle = prompt_handle
                break
        
        if not found:
            print(f"   ❌ Prompt '{handle}' não encontrado via client.list_prompts().")
            print(f"\n   💡 Tentando fazer pull direto do Hub...")
            
            try:
                # Tentar pull direto
                pulled_prompt = hub.pull(handle)
                print(f"   ✅ Prompt encontrado via hub.pull()!")
                print(f"   Isso significa que o prompt existe mas pode não estar visível")
                print(f"   no seu workspace atual ou pode ser de outro usuário.")
                print(f"\n   📝 Detalhes do prompt pulado:")
                print(f"      Type: {type(pulled_prompt).__name__}")
                if hasattr(pulled_prompt, 'messages'):
                    print(f"      Messages: {len(pulled_prompt.messages)}")
                if hasattr(pulled_prompt, 'metadata'):
                    print(f"      Metadata: {pulled_prompt.metadata}")
            except Exception as pull_error:
                print(f"   ❌ Também não foi possível fazer pull: {pull_error}")
                print(f"\n   💡 Possíveis causas:")
                print(f"      - O handle está incorreto")
                print(f"      - O prompt não existe")
                print(f"      - Você não tem permissão para acessar")
            
            return None
        
        print(f"   ✅ Prompt encontrado!")
        print(f"   Handle: {found_handle}")
        print(f"   ID: {getattr(found, 'id', 'N/A')}")
        print(f"   Descrição: {getattr(found, 'description', 'N/A') or 'N/A'}")
        print(f"   Público: {getattr(found, 'is_public', 'N/A')}")
        print(f"   Criado em: {getattr(found, 'created_at', 'N/A')}")
        print(f"   Modificado em: {getattr(found, 'updated_at', 'N/A')}")
        print(f"   Commits: {getattr(found, 'num_commits', 0)}")
        print(f"   Tags: {getattr(found, 'tags', [])}")
        
        return found
        
    except Exception as e:
        print(f"   ❌ Erro ao buscar prompt: {e}")
        print(f"   💡 Tipo do erro: {type(e).__name__}")
        return None


def check_prompt_hub_connection():
    """Verifica a conexão com o LangSmith Hub."""
    print("\n" + "=" * 70)
    print("🔌 VERIFICANDO CONEXÃO COM LANGSMITH HUB")
    print("=" * 70 + "\n")
    
    # Verificar variáveis de ambiente
    api_key = os.getenv('LANGSMITH_API_KEY')
    username = os.getenv('USERNAME_LANGSMITH_HUB')
    
    print("   Variáveis de Ambiente:")
    print(f"   LANGSMITH_API_KEY: {'✓ Configurada' if api_key else '✗ Não configurada'}")
    print(f"   USERNAME_LANGSMITH_HUB: {username if username else '✗ Não configurada'}")
    
    if not api_key:
        print(f"\n   ⚠️  LANGSMITH_API_KEY não encontrada!")
        print(f"   Configure no arquivo .env")
        return False
    
    # Verificar conexão
    try:
        client = Client()
        print(f"\n   ✅ Conexão estabelecida com sucesso!")
        return True
    except Exception as e:
        print(f"\n   ❌ Erro ao conectar: {e}")
        return False


def diagnose_prompt_issue(prompt_name: str):
    """
    Diagnóstico completo de um problema com prompt.
    
    Args:
        prompt_name: Nome do prompt para diagnosticar
    """
    print("\n" + "=" * 70)
    print(f"🔬 DIAGNÓSTICO COMPLETO: {prompt_name}")
    print("=" * 70)
    
    try:
        client = Client()
        username = os.getenv('USERNAME_LANGSMITH_HUB', '')
        
        # Testar diferentes variações do nome
        variations = [
            prompt_name,
            f"{username}/{prompt_name}" if username else None,
            prompt_name.replace('_', '-'),
            f"{username}/{prompt_name.replace('_', '-')}" if username else None,
        ]
        variations = [v for v in variations if v]  # Remover None
        
        print(f"\n   Testando {len(variations)} variações de nome:")
        for var in variations:
            print(f"      - {var}")
        
        print(f"\n   Resultados:")
        
        found_any = False
        for variation in variations:
            print(f"\n   Testando: {variation}")
            
            # Testar via list_prompts
            try:
                prompts_response = client.list_prompts()
                prompts_list = prompts_response.repos
                
                matches = []
                
                for prompt in prompts_list:
                    # Obter handle do prompt
                    prompt_handle = getattr(prompt, 'repo_handle', getattr(prompt, 'full_name', None))
                    
                    if prompt_handle and (prompt_handle == variation or prompt_handle.endswith(f"/{variation}")):
                        matches.append((prompt_handle, prompt))
                
                if matches:
                    print(f"      ✅ Encontrado via list_prompts()")
                    found_any = True
                    for repo_handle, prompt in matches:
                        print(f"         Handle: {repo_handle}")
                        print(f"         Público: {getattr(prompt, 'is_public', 'N/A')}")
                else:
                    print(f"      ✗ Não encontrado via list_prompts()")
            except Exception as e:
                print(f"      ⚠️  Erro ao listar: {e}")
            
            # Testar via hub.pull
            try:
                pulled = hub.pull(variation)
                print(f"      ✅ Encontrado via hub.pull()")
                print(f"         Type: {type(pulled).__name__}")
                found_any = True
            except Exception as e:
                print(f"      ✗ Não encontrado via hub.pull(): {str(e)[:50]}...")
        
        if not found_any:
            print(f"\n   ❌ Prompt não encontrado em nenhuma variação")
            print(f"\n   💡 Possíveis soluções:")
            print(f"      1. Verifique se o nome está correto")
            print(f"      2. Verifique se USERNAME_LANGSMITH_HUB está correto no .env")
            print(f"      3. Tente criar o prompt com um nome diferente")
            print(f"      4. Verifique se você está no workspace correto")
        else:
            print(f"\n   ✅ Prompt existe! Mas pode não estar visível na UI")
            print(f"\n   💡 Possíveis causas:")
            print(f"      1. Prompt foi criado em outro workspace")
            print(f"      2. Prompt é público mas não aparece filtrado")
            print(f"      3. Cache da UI do LangSmith")
            print(f"      4. Permissões de visualização")
            
    except Exception as e:
        print(f"\n   ❌ Erro durante diagnóstico: {e}")


def main():
    """Função principal com menu interativo."""
    print("=" * 70)
    print("🔧 FERRAMENTA DE DEBUG DE PROMPTS - LANGSMITH HUB")
    print("=" * 70)
    
    # Verificar conexão primeiro
    if not check_prompt_hub_connection():
        print("\n❌ Não foi possível conectar ao LangSmith. Verifique suas credenciais.")
        return 1
    
    client = Client()
    
    while True:
        print("\n" + "=" * 70)
        print("MENU DE OPÇÕES")
        print("=" * 70)
        print("1. Listar MEUS prompts")
        print("2. Buscar prompt por nome/handle")
        print("3. Diagnosticar problema com prompt específico")
        print("4. Verificar conexão")
        print("5. Listar TODOS os prompts públicos (primeiros 100)")
        print("6. 🗑️  Deletar um prompt")
        print("0. Sair")
        print("=" * 70)
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == "1":
            list_all_prompts(client)
            
        elif choice == "2":
            handle = input("Digite o handle do prompt (ex: username/prompt-name): ").strip()
            if handle:
                find_prompt_by_handle(client, handle)
            
        elif choice == "3":
            prompt_name = input("Digite o nome do prompt para diagnosticar: ").strip()
            if prompt_name:
                diagnose_prompt_issue(prompt_name)
            
        elif choice == "4":
            check_prompt_hub_connection()
            
        elif choice == "5":
            list_all_public_prompts(client)
            
        elif choice == "6":
            handle = input("Digite o handle do prompt para deletar (ex: username/prompt-name): ").strip()
            if handle:
                delete_prompt(client, handle)
            
        elif choice == "0":
            print("\n👋 Até logo!")
            break
            break
            
        else:
            print("\n⚠️  Opção inválida!")
    
    return 0


if __name__ == "__main__":
    exit(main())
