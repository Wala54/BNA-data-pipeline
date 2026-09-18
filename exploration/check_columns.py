from src.db import run_query

results = run_query("DESCRIBE workspace.credit_analysis.fact_credit")
for r in results:
    print(r)
