from prefect import serve
from pipeline_prefect import flow_all

if __name__ == "__main__":
    deployment_all = flow_all.to_deployment(
        name="ml-pipeline-all",
        cron="0 6 * * *",  # tous les jours à 6h00
    )
    serve(deployment_all)
