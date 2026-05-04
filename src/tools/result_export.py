from langsmith import Client
from datetime import datetime
import argparse
import json
from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("--project", default="fc-ai-ex-pull-evaluation-prompt")
parser.add_argument("--from-time", required=True,
                   help="ISO format, e.g. 2026-05-04T14:30:00")
parser.add_argument("--output", default="traces.json")

args = parser.parse_args()

client = Client()

start_time = datetime.fromisoformat(args.from_time)

runs = client.list_runs(
    project_name=args.project,
    start_time=start_time
)

data = []

for run in runs:
    data.append({
        "id": str(run.id),
        "start_time": str(run.start_time),
        "inputs": run.inputs,
        "outputs": run.outputs,
        "error": run.error
    })

with open(args.output, "w") as f:
    json.dump(data, f, indent=2)

print(f"Exported {len(data)} traces to {args.output}")