"""
Script COMPLETO para avaliar prompts otimizados.

Este script:
1. Carrega dataset de avaliação de arquivo .jsonl (datasets/bug_to_user_story.jsonl)
2. Cria/atualiza dataset no LangSmith
3. Puxa prompts otimizados do LangSmith Hub (fonte única de verdade)
4. Executa prompts contra o dataset
5. Calcula 5 métricas (Helpfulness, Correctness, F1-Score, Clarity, Precision)
6. Publica resultados no dashboard do LangSmith
7. Exibe resumo no terminal

Suporta múltiplos providers de LLM:
- OpenAI (gpt-4o, gpt-4o-mini)
- Google Gemini (gemini-1.5-flash, gemini-1.5-pro)

Configure o provider no arquivo .env através da variável LLM_PROVIDER.
"""

import os
import sys
import json
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configurar ambiente LangSmith ANTES de importar qualquer módulo LangChain
# Isso garante que TODOS os traces (incluindo evaluators) vão para o mesmo projeto
project_name = os.getenv("LANGSMITH_PROJECT", "fc-ai-ex-pull-evaluation-prompt")

# Mapear variáveis LANGSMITH_* para LANGCHAIN_*
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
if langsmith_api_key:
    os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key

langsmith_endpoint = os.getenv("LANGSMITH_ENDPOINT")
if langsmith_endpoint:
    os.environ["LANGCHAIN_ENDPOINT"] = langsmith_endpoint

# Configurar projeto e tracing ANTES dos imports
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = project_name

# Agora importar módulos LangChain/LangSmith
from langsmith import Client, evaluate
from langsmith.schemas import Run, Example
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import check_env_vars, format_score, print_section_header, get_llm as get_configured_llm
from metrics import evaluate_f1_score, evaluate_clarity, evaluate_precision


def get_llm():
    return get_configured_llm(temperature=0)


def load_dataset_from_jsonl(jsonl_path: str) -> List[Dict[str, Any]]:
    examples = []

    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:  # Ignorar linhas vazias
                    example = json.loads(line)
                    examples.append(example)

        return examples

    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {jsonl_path}")
        print("\nCertifique-se de que o arquivo datasets/bug_to_user_story.jsonl existe.")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao parsear JSONL: {e}")
        return []
    except Exception as e:
        print(f"❌ Erro ao carregar dataset: {e}")
        return []


def create_evaluation_dataset(client: Client, dataset_name: str, jsonl_path: str) -> str:
    print(f"Criando dataset de avaliação: {dataset_name}...")

    examples = load_dataset_from_jsonl(jsonl_path)

    if not examples:
        print("❌ Nenhum exemplo carregado do arquivo .jsonl")
        return dataset_name

    print(f"   ✓ Carregados {len(examples)} exemplos do arquivo {jsonl_path}")

    try:
        datasets = client.list_datasets(dataset_name=dataset_name)
        existing_dataset = None

        for ds in datasets:
            if ds.name == dataset_name:
                existing_dataset = ds
                break

        if existing_dataset:
            print(f"   ✓ Dataset '{dataset_name}' já existe, usando existente")
            return dataset_name
        else:
            dataset = client.create_dataset(dataset_name=dataset_name)

            for example in examples:
                client.create_example(
                    dataset_id=dataset.id,
                    inputs=example["inputs"],
                    outputs=example["outputs"]
                )

            print(f"   ✓ Dataset criado com {len(examples)} exemplos")
            return dataset_name

    except Exception as e:
        print(f"   ⚠️  Erro ao criar dataset: {e}")
        return dataset_name


def pull_prompt_from_langsmith(prompt_name: str) -> ChatPromptTemplate:
    try:
        print(f"   Puxando prompt do LangSmith Hub: {prompt_name}")
        prompt = hub.pull(prompt_name)
        print(f"   ✓ Prompt carregado com sucesso")
        return prompt

    except Exception as e:
        error_msg = str(e).lower()

        print(f"\n{'=' * 70}")
        print(f"❌ ERRO: Não foi possível carregar o prompt '{prompt_name}'")
        print(f"{'=' * 70}\n")

        if "not found" in error_msg or "404" in error_msg:
            print("⚠️  O prompt não foi encontrado no LangSmith Hub.\n")
            print("AÇÕES NECESSÁRIAS:")
            print("1. Verifique se você já fez push do prompt otimizado:")
            print(f"   python src/push_prompts.py")
            print()
            print("2. Confirme se o prompt foi publicado com sucesso em:")
            print(f"   https://smith.langchain.com/prompts")
            print()
            print(f"3. Certifique-se de que o nome do prompt está correto: '{prompt_name}'")
            print()
            print("4. Se você alterou o prompt no YAML, refaça o push:")
            print(f"   python src/push_prompts.py")
        else:
            print(f"Erro técnico: {e}\n")
            print("Verifique:")
            print("- LANGSMITH_API_KEY está configurada corretamente no .env")
            print("- Você tem acesso ao workspace do LangSmith")
            print("- Sua conexão com a internet está funcionando")

        print(f"\n{'=' * 70}\n")
        raise


def create_target_function(prompt_template: ChatPromptTemplate, llm: Any):
    """
    Cria a função target que será avaliada pelo LangSmith evaluate().
    Esta função recebe inputs e retorna o output do modelo.
    """
    def predict(inputs: Dict[str, Any]) -> Dict[str, Any]:
        chain = prompt_template | llm
        response = chain.invoke(inputs)
        return {"output": response.content}
    
    return predict


def create_evaluator(eval_name: str, eval_function):
    """
    Cria um evaluator customizado para langsmith.evaluate().
    Retorna um dict com key e score que o evaluate() espera.
    """
    def evaluator(run: Run, example: Example) -> Dict[str, Any]:
        try:
            # Extrair dados do run e example
            prediction = run.outputs.get("output", "") if run.outputs else ""
            reference = example.outputs.get("reference", "") if example.outputs else ""
            
            # Extrair question dos inputs
            inputs = example.inputs if example.inputs else {}
            question = inputs.get("question", inputs.get("bug_report", inputs.get("pr_title", "N/A")))
            
            # Executar a função de avaliação customizada
            result = eval_function(question, prediction, reference)
            
            return {
                "key": eval_name,
                "score": result["score"]
            }
        except Exception as e:
            print(f"      ⚠️  Erro em {eval_name}: {e}")
            return {
                "key": eval_name,
                "score": 0.0
            }
    
    return evaluator


def evaluate_prompt(
    prompt_name: str,
    dataset_name: str,
    client: Client
) -> Dict[str, float]:
    print(f"\n🔍 Avaliando: {prompt_name}")

    try:
        prompt_template = pull_prompt_from_langsmith(prompt_name)
        llm = get_llm()

        # Get dataset info for counting
        examples = list(client.list_examples(dataset_name=dataset_name))
        total_examples = len(examples)
        
        if total_examples == 0:
            print(f"   ⚠️  Nenhum exemplo encontrado no dataset '{dataset_name}'")
            return {
                "helpfulness": 0.0,
                "correctness": 0.0,
                "f1_score": 0.0,
                "clarity": 0.0,
                "precision": 0.0
            }

        # Create target function for evaluate()
        target_function = create_target_function(prompt_template, llm)

        # Create evaluators
        evaluators = [
            create_evaluator("f1_score", evaluate_f1_score),
            create_evaluator("clarity", evaluate_clarity),
            create_evaluator("precision", evaluate_precision),
        ]

        print(f"   Executando avaliação de {total_examples} exemplos com langsmith.evaluate()...")
        print("   ")

        # Run evaluate() - creates experiment automatically
        import io
        import contextlib
        import time
        
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            results = evaluate(
                target_function,
                data=dataset_name,
                evaluators=evaluators,
                experiment_prefix=prompt_name,
                max_concurrency=1,
                client=client,
            )

        # Get experiment name
        experiment_name = getattr(results, 'experiment_name', '')
        
        # Wait a moment for feedback to be processed
        time.sleep(3)
        
        # Fetch experiment runs with feedback
        experiment_runs = list(client.list_runs(
            project_name=experiment_name,
            is_root=True,
            limit=total_examples * 2
        ))
        
        # Filter to target runs and reverse for chronological order
        target_runs = [r for r in experiment_runs if r.name == "Target"][:total_examples]
        target_runs = list(reversed(target_runs))
        
        # Collect scores for averaging
        f1_scores = []
        clarity_scores = []
        precision_scores = []
        
        # Display per-example metrics
        for i, run in enumerate(target_runs, 1):
            # Get feedback for this run
            feedbacks = list(client.list_feedback(run_ids=[run.id]))
            
            f1_score = 0.0
            clarity_score = 0.0
            precision_score = 0.0
            
            for feedback in feedbacks:
                if feedback.key == "f1_score":
                    f1_score = feedback.score or 0.0
                elif feedback.key == "clarity":
                    clarity_score = feedback.score or 0.0
                elif feedback.key == "precision":
                    precision_score = feedback.score or 0.0
            
            # Store for averaging
            f1_scores.append(f1_score)
            clarity_scores.append(clarity_score)
            precision_scores.append(precision_score)
            
            print(f"      [{i}/{total_examples}] F1:{f1_score:.2f} Clarity:{clarity_score:.2f} Precision:{precision_score:.2f}")

        print(f"\n   ✓ Avaliação concluída")

        # Calculate averages from collected scores
        avg_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0
        avg_clarity = sum(clarity_scores) / len(clarity_scores) if clarity_scores else 0.0
        avg_precision = sum(precision_scores) / len(precision_scores) if precision_scores else 0.0

        avg_helpfulness = (avg_clarity + avg_precision) / 2
        avg_correctness = (avg_f1 + avg_precision) / 2

        return {
            "helpfulness": round(avg_helpfulness, 4),
            "correctness": round(avg_correctness, 4),
            "f1_score": round(avg_f1, 4),
            "clarity": round(avg_clarity, 4),
            "precision": round(avg_precision, 4),
            "experiment_name": experiment_name
        }

    except Exception as e:
        print(f"   ❌ Erro na avaliação: {e}")
        import traceback
        traceback.print_exc()
        return {
            "helpfulness": 0.0,
            "correctness": 0.0,
            "f1_score": 0.0,
            "clarity": 0.0,
            "precision": 0.0
        }


def display_results(prompt_name: str, scores: Dict[str, float]) -> bool:
    print("\n" + "=" * 50)
    print(f"Prompt: {prompt_name}")
    print("=" * 50)

    experiment_name = scores.get("experiment_name", "")
    
    print("\nMétricas LangSmith:")
    print(f"  - Helpfulness: {format_score(scores['helpfulness'], threshold=0.9)}")
    print(f"  - Correctness: {format_score(scores['correctness'], threshold=0.9)}")

    print("\nMétricas Customizadas:")
    print(f"  - F1-Score: {format_score(scores['f1_score'], threshold=0.9)}")
    print(f"  - Clarity: {format_score(scores['clarity'], threshold=0.9)}")
    print(f"  - Precision: {format_score(scores['precision'], threshold=0.9)}")

    average_score = sum(v for v in scores.values() if v is not None and isinstance(v, (int, float))) / 5

    print("\n" + "-" * 50)
    print(f"📊 MÉDIA GERAL: {average_score:.4f}")
    print("-" * 50)

    passed = average_score >= 0.9

    if passed:
        print(f"\n✅ STATUS: APROVADO (média >= 0.9)")
    else:
        print(f"\n❌ STATUS: REPROVADO (média < 0.9)")
        print(f"⚠️  Média atual: {average_score:.4f} | Necessário: 0.9000")

    return passed


def main():
    print_section_header("AVALIAÇÃO DE PROMPTS OTIMIZADOS")

    provider = os.getenv("LLM_PROVIDER", "openai")
    llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    eval_model = os.getenv("EVAL_MODEL", "gpt-4o")

    print(f"Provider: {provider}")
    print(f"Modelo Principal: {llm_model}")
    print(f"Modelo de Avaliação: {eval_model}\n")

    required_vars = ["LANGSMITH_API_KEY", "LLM_PROVIDER"]
    if provider == "openai":
        required_vars.append("OPENAI_API_KEY")
    elif provider in ["google", "gemini"]:
        required_vars.append("GOOGLE_API_KEY")
    elif provider == "Anthropic":
        required_vars.append("ANTHROPIC_API_KEY")

    if not check_env_vars(required_vars):
        return 1

    # Client já configurado com as variáveis de ambiente no início do arquivo
    client = Client()
    
    print(f"📊 LangSmith Project: {project_name}")
    print(f"🧪 Using langsmith.evaluate() to create EXPERIMENTS")
    print(f"🔗 View at: https://smith.langchain.com/")
    print(f"   Navigate to: Projects → {project_name} → Experiments tab")
    print(f"   All traces (including evaluators) will go to: {project_name}\n")

    # Usar o dataset já carregado no LangSmith
    dataset_name = "bug_to_user_story_v2_dataset"
    
    # Verificar se o dataset existe
    try:
        datasets = list(client.list_datasets(dataset_name=dataset_name))
        if datasets:
            print(f"✓ Usando dataset existente: {dataset_name}")
            print(f"  Dataset ID: {datasets[0].id}\n")
        else:
            print(f"❌ Dataset '{dataset_name}' não encontrado no LangSmith")
            print(f"\nPor favor, faça upload do dataset primeiro:")
            print(f"  python src/tools/dataset_upload.py")
            return 1
    except Exception as e:
        print(f"❌ Erro ao verificar dataset: {e}")
        return 1

    print("\n" + "=" * 70)
    print("PROMPTS PARA AVALIAR")
    print("=" * 70)
    print("\nEste script irá puxar prompts do LangSmith Hub.")
    print("Certifique-se de ter feito push dos prompts antes de avaliar:")
    print("  python src/push_prompts.py\n")

    prompts_to_evaluate = [
        "bug_to_user_story_v2",
    ]

    all_passed = True
    evaluated_count = 0
    results_summary = []

    for prompt_name in prompts_to_evaluate:
        evaluated_count += 1

        try:
            scores = evaluate_prompt(prompt_name, dataset_name, client)

            passed = display_results(prompt_name, scores)
            all_passed = all_passed and passed

            results_summary.append({
                "prompt": prompt_name,
                "scores": scores,
                "passed": passed
            })

        except Exception as e:
            print(f"\n❌ Falha ao avaliar '{prompt_name}': {e}")
            all_passed = False

            results_summary.append({
                "prompt": prompt_name,
                "scores": {
                    "helpfulness": 0.0,
                    "correctness": 0.0,
                    "f1_score": 0.0,
                    "clarity": 0.0,
                    "precision": 0.0
                },
                "passed": False
            })

    print("\n" + "=" * 50)
    print("RESUMO FINAL")
    print("=" * 50 + "\n")

    if evaluated_count == 0:
        print("⚠️  Nenhum prompt foi avaliado")
        return 1

    print(f"Prompts avaliados: {evaluated_count}")
    print(f"Aprovados: {sum(1 for r in results_summary if r['passed'])}")
    print(f"Reprovados: {sum(1 for r in results_summary if not r['passed'])}\n")

    if all_passed:
        print("✅ Todos os prompts atingiram média >= 0.9!")
        print(f"\n✓ Confira os traces em:")
        print(f"  https://smith.langchain.com/ → Tracing")
        print("\nPróximos passos:")
        print("1. Documente o processo no README.md")
        print("2. Capture screenshots das avaliações")
        print("3. Faça commit e push para o GitHub")
        return 0
    else:
        print("⚠️  Alguns prompts não atingiram média >= 0.9")
        print("\nPróximos passos:")
        print("1. Refatore os prompts com score baixo")
        print("2. Faça push novamente: python src/push_prompts.py")
        print("3. Execute: python src/evaluate.py novamente")
        return 1

if __name__ == "__main__":
    sys.exit(main())

