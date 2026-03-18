"""
Script de diagnóstico para problemas com datasets no LangSmith.

Este script ajuda a identificar e resolver problemas como:
- Datasets que existem mas não aparecem na UI
- Conflitos de nomes
- Datasets com exemplos faltando

Uso:
    python src/dataset_debug.py
"""

import os
from dotenv import load_dotenv
from langsmith import Client

load_dotenv()


def list_all_datasets(client: Client):
    """Lista todos os datasets no workspace."""
    print("\n" + "=" * 70)
    print("📋 LISTANDO TODOS OS DATASETS")
    print("=" * 70 + "\n")
    
    try:
        datasets = list(client.list_datasets())
        
        if not datasets:
            print("   ℹ️  Nenhum dataset encontrado no workspace.")
            return
        
        print(f"   Encontrados {len(datasets)} dataset(s):\n")
        
        for i, ds in enumerate(datasets, 1):
            print(f"   {i}. Nome: {ds.name}")
            print(f"      ID: {ds.id}")
            print(f"      Descrição: {ds.description or 'N/A'}")
            print(f"      Criado em: {ds.created_at}")
            
            # Contar exemplos
            try:
                examples = list(client.list_examples(dataset_id=ds.id))
                print(f"      Exemplos: {len(examples)}")
            except Exception as e:
                print(f"      Exemplos: Erro ao contar - {e}")
            
            print()
            
    except Exception as e:
        print(f"   ❌ Erro ao listar datasets: {e}")


def find_dataset_by_name(client: Client, name: str):
    """Busca um dataset específico por nome."""
    print("\n" + "=" * 70)
    print(f"🔍 BUSCANDO DATASET: {name}")
    print("=" * 70 + "\n")
    
    try:
        datasets = list(client.list_datasets(dataset_name=name))
        
        found = None
        for ds in datasets:
            if ds.name == name:
                found = ds
                break
        
        if not found:
            print(f"   ❌ Dataset '{name}' não encontrado.")
            print(f"   💡 Tente listar todos os datasets para ver o que existe.")
            return None
        
        print(f"   ✅ Dataset encontrado!")
        print(f"   Nome: {found.name}")
        print(f"   ID: {found.id}")
        print(f"   Descrição: {found.description or 'N/A'}")
        print(f"   Criado em: {found.created_at}")
        print(f"   Modificado em: {found.modified_at}")
        
        # Listar exemplos
        try:
            examples = list(client.list_examples(dataset_id=found.id))
            print(f"   Exemplos: {len(examples)}")
            
            if examples and len(examples) <= 5:
                print(f"\n   📝 Exemplos encontrados:")
                for i, ex in enumerate(examples, 1):
                    print(f"      {i}. ID: {ex.id}")
                    print(f"         Inputs keys: {list(ex.inputs.keys()) if ex.inputs else 'N/A'}")
                    print(f"         Outputs keys: {list(ex.outputs.keys()) if ex.outputs else 'N/A'}")
            elif examples:
                print(f"   📝 Primeiros 3 exemplos:")
                for i, ex in enumerate(examples[:3], 1):
                    print(f"      {i}. ID: {ex.id}")
                    
        except Exception as e:
            print(f"   ⚠️  Erro ao listar exemplos: {e}")
        
        return found
        
    except Exception as e:
        print(f"   ❌ Erro ao buscar dataset: {e}")
        return None


def delete_dataset_by_name(client: Client, name: str):
    """Apaga um dataset por nome."""
    print("\n" + "=" * 70)
    print(f"🗑️  APAGAR DATASET: {name}")
    print("=" * 70 + "\n")
    
    # Primeiro encontrar o dataset
    dataset = find_dataset_by_name(client, name)
    
    if not dataset:
        return False
    
    print(f"\n   ⚠️  ATENÇÃO: Esta ação é IRREVERSÍVEL!")
    print(f"   Dataset: {dataset.name}")
    print(f"   ID: {dataset.id}")
    
    confirm = input(f"\n   ❓ Tem certeza que deseja apagar este dataset? [S/N]: ").strip().upper()
    
    if confirm != 'S':
        print("   ❌ Operação cancelada.")
        return False
    
    try:
        client.delete_dataset(dataset_id=dataset.id)
        print(f"   ✅ Dataset '{name}' apagado com sucesso!")
        return True
    except Exception as e:
        print(f"   ❌ Erro ao apagar dataset: {e}")
        return False


def check_dataset_health(client: Client, name: str):
    """Verifica a saúde de um dataset."""
    print("\n" + "=" * 70)
    print(f"🏥 DIAGNÓSTICO DO DATASET: {name}")
    print("=" * 70 + "\n")
    
    dataset = find_dataset_by_name(client, name)
    
    if not dataset:
        print("\n   💡 DIAGNÓSTICO:")
        print("   - Dataset não existe ou nome está incorreto")
        print("   - Use a opção 1 para listar todos os datasets disponíveis")
        return
    
    print("\n   ✓ Dataset existe e está acessível")
    
    # Verificar exemplos
    try:
        examples = list(client.list_examples(dataset_id=dataset.id))
        
        if not examples:
            print("   ⚠️  Dataset não tem exemplos!")
            print("   💡 Use dataset_upload.py para adicionar exemplos")
        else:
            print(f"   ✓ Dataset tem {len(examples)} exemplo(s)")
            
            # Verificar estrutura dos exemplos
            invalid_count = 0
            for ex in examples:
                if not ex.inputs or not ex.outputs:
                    invalid_count += 1
            
            if invalid_count > 0:
                print(f"   ⚠️  {invalid_count} exemplo(s) com estrutura inválida (sem inputs ou outputs)")
            else:
                print(f"   ✓ Todos os exemplos têm estrutura válida")
            
    except Exception as e:
        print(f"   ❌ Erro ao verificar exemplos: {e}")


def main():
    """Função principal com menu interativo."""
    print("=" * 70)
    print("🔧 FERRAMENTA DE DIAGNÓSTICO - LANGSMITH DATASETS")
    print("=" * 70 + "\n")
    
    # Verificar API key
    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        print("❌ LANGSMITH_API_KEY não configurada no .env")
        return 1
    
    # Conectar ao LangSmith
    print("🔗 Conectando ao LangSmith...")
    try:
        client = Client()
        print("   ✓ Conectado com sucesso\n")
    except Exception as e:
        print(f"   ❌ Erro ao conectar: {e}")
        return 1
    
    # Menu interativo
    while True:
        print("\n" + "=" * 70)
        print("MENU DE OPÇÕES")
        print("=" * 70)
        print("1. Listar todos os datasets")
        print("2. Buscar dataset específico por nome")
        print("3. Verificar saúde de um dataset")
        print("4. Apagar dataset por nome")
        print("5. Sair")
        print("=" * 70)
        
        choice = input("\nEscolha uma opção [1-5]: ").strip()
        
        if choice == "1":
            list_all_datasets(client)
            
        elif choice == "2":
            name = input("\nDigite o nome do dataset: ").strip()
            if name:
                find_dataset_by_name(client, name)
            else:
                print("   ❌ Nome não pode ser vazio")
                
        elif choice == "3":
            name = input("\nDigite o nome do dataset: ").strip()
            if name:
                check_dataset_health(client, name)
            else:
                print("   ❌ Nome não pode ser vazio")
                
        elif choice == "4":
            name = input("\nDigite o nome do dataset: ").strip()
            if name:
                delete_dataset_by_name(client, name)
            else:
                print("   ❌ Nome não pode ser vazio")
                
        elif choice == "5":
            print("\n👋 Até logo!")
            break
            
        else:
            print("\n   ❌ Opção inválida. Escolha 1-5.")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
