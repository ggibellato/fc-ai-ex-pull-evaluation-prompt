"""
Script para fazer upload do dataset local para o LangSmith.

Este script:
1. Carrega exemplos do arquivo .jsonl local
2. Conecta ao LangSmith
3. Cria ou atualiza o dataset especificado
4. Faz upload de todos os exemplos

Uso:
    python src/dataset_upload.py
"""

import os
import json
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client

load_dotenv()


def load_dataset_from_jsonl(jsonl_path: str) -> List[Dict[str, Any]]:
    """
    Carrega exemplos de um arquivo JSONL.
    
    Args:
        jsonl_path: Caminho para o arquivo JSONL
        
    Returns:
        Lista de exemplos (dicts com 'inputs' e 'outputs')
    """
    examples = []

    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:  # Ignorar linhas vazias
                    try:
                        example = json.loads(line)
                        
                        # Validar estrutura do exemplo
                        if "inputs" not in example or "outputs" not in example:
                            print(f"   ⚠️  Linha {line_num}: Exemplo sem 'inputs' ou 'outputs', pulando...")
                            continue
                        
                        examples.append(example)
                    except json.JSONDecodeError as e:
                        print(f"   ⚠️  Linha {line_num}: Erro ao parsear JSON - {e}")
                        continue

        return examples

    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {jsonl_path}")
        return []
    except Exception as e:
        print(f"❌ Erro ao carregar dataset: {e}")
        return []


def upload_dataset_to_langsmith(
    client: Client,
    dataset_name: str,
    examples: List[Dict[str, Any]],
    overwrite: bool = False
) -> bool:
    """
    Faz upload de exemplos para um dataset no LangSmith.
    
    Args:
        client: Cliente do LangSmith
        dataset_name: Nome do dataset
        examples: Lista de exemplos para upload
        overwrite: Se True, recria o dataset (apaga e cria novo)
        
    Returns:
        True se sucesso, False caso contrário
    """
    try:
        # Verificar se dataset já existe
        datasets = list(client.list_datasets(dataset_name=dataset_name))
        existing_dataset = None
        
        for ds in datasets:
            if ds.name == dataset_name:
                existing_dataset = ds
                break
        
        if existing_dataset:
            if overwrite:
                print(f"   🗑️  Dataset '{dataset_name}' existe, apagando para recriar...")
                client.delete_dataset(dataset_id=existing_dataset.id)
                existing_dataset = None
            else:
                print(f"   ℹ️  Dataset '{dataset_name}' já existe.")
                
                # Contar exemplos existentes
                existing_examples = list(client.list_examples(dataset_id=existing_dataset.id))
                print(f"   📊 Exemplos existentes: {len(existing_examples)}")
                
                response = input("   ❓ Deseja adicionar novos exemplos (A), substituir todos (S) ou cancelar (C)? [A/S/C]: ").strip().upper()
                
                if response == 'C':
                    print("   ❌ Upload cancelado.")
                    return False
                elif response == 'S':
                    print(f"   🗑️  Apagando dataset existente...")
                    client.delete_dataset(dataset_id=existing_dataset.id)
                    existing_dataset = None
                elif response != 'A':
                    print("   ❌ Opção inválida. Upload cancelado.")
                    return False
        
        # Criar dataset se não existe
        if not existing_dataset:
            print(f"   ✨ Criando novo dataset: {dataset_name}")
            
            # Adicionar descrição para melhorar visibilidade
            dataset = client.create_dataset(
                dataset_name=dataset_name,
                description="Dataset de avaliação: Bug reports convertidos em User Stories"
            )
            print(f"   ✓ Dataset criado com ID: {dataset.id}")
        else:
            dataset = existing_dataset
            print(f"   ✓ Usando dataset existente (ID: {dataset.id})")
        
        # Fazer upload dos exemplos
        print(f"   📤 Fazendo upload de {len(examples)} exemplos...")
        
        for i, example in enumerate(examples, 1):
            try:
                client.create_example(
                    dataset_id=dataset.id,
                    inputs=example["inputs"],
                    outputs=example["outputs"]
                )
                
                # Mostrar progresso a cada 5 exemplos
                if i % 5 == 0 or i == len(examples):
                    print(f"      [{i}/{len(examples)}] exemplos enviados...")
                    
            except Exception as e:
                print(f"      ⚠️  Erro ao enviar exemplo {i}: {e}")
                continue
        
        print(f"   ✅ Upload concluído! {len(examples)} exemplos no dataset '{dataset_name}'")
        print(f"\n   🔗 Acesse o dataset diretamente em:")
        print(f"      https://smith.langchain.com/datasets/{dataset.id}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao fazer upload do dataset: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False


def main():
    """Função principal."""
    print("=" * 70)
    print("UPLOAD DE DATASET PARA LANGSMITH")
    print("=" * 70 + "\n")
    
    # Verificar API key
    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        print("❌ LANGSMITH_API_KEY não configurada no .env")
        print("\nConfigure a variável de ambiente antes de continuar:")
        print("  LANGSMITH_API_KEY=seu_token_aqui")
        return 1
    
    # Configurações
    dataset_name = "bug_to_user_story_v2_dataset"
    jsonl_path = "datasets/bug_to_user_story.jsonl"
    
    print(f"Dataset destino: {dataset_name}")
    print(f"Arquivo fonte: {jsonl_path}\n")
    
    # Verificar se arquivo existe
    if not Path(jsonl_path).exists():
        print(f"❌ Arquivo não encontrado: {jsonl_path}")
        print("\nCertifique-se de que o arquivo existe antes de continuar.")
        return 1
    
    # Carregar exemplos do arquivo local
    print(f"📂 Carregando exemplos do arquivo local...")
    examples = load_dataset_from_jsonl(jsonl_path)
    
    if not examples:
        print("❌ Nenhum exemplo válido carregado do arquivo .jsonl")
        return 1
    
    print(f"   ✓ Carregados {len(examples)} exemplos válidos\n")
    
    # Conectar ao LangSmith
    print(f"🔗 Conectando ao LangSmith...")
    try:
        client = Client()
        print(f"   ✓ Conectado com sucesso\n")
    except Exception as e:
        print(f"   ❌ Erro ao conectar: {e}")
        return 1
    
    # Fazer upload
    print(f"📤 Iniciando upload para '{dataset_name}'...")
    success = upload_dataset_to_langsmith(
        client=client,
        dataset_name=dataset_name,
        examples=examples,
        overwrite=False  # Não sobrescrever automaticamente
    )
    
    if success:
        print("\n" + "=" * 70)
        print("✅ UPLOAD CONCLUÍDO COM SUCESSO!")
        print("=" * 70)
        print(f"\n✓ Acesse o dataset em:")
        print(f"  https://smith.langchain.com/datasets")
        print(f"\n✓ Agora você pode executar avaliações:")
        print(f"  python src/evaluate.py")
        return 0
    else:
        print("\n" + "=" * 70)
        print("❌ UPLOAD FALHOU")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
