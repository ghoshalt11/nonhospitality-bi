import yaml
import os

def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def load_all_schemas():
    base = "schemas"

    return {
        "descriptive": load_yaml(f"{base}/monthly_service_kpis.yaml"),
        "forecast": load_yaml(f"{base}/monthly_service_kpis_forecasts.yaml"),
        "market": load_yaml(f"{base}/market_data_schema.yaml"),
        "semantic": load_yaml(f"{base}/semantic_model_business.yaml"),
    }
