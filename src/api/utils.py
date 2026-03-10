import requests


def get_model_price(model_name: str):

    url = "https://openrouter.ai/api/v1/models"
    res = requests.get(url)
    data = res.json()["data"]

    for model in data:
        if model["id"] == model_name:
            return {
                "input": float(model["pricing"]["prompt"]),
                "output": float(model["pricing"]["completion"]),
            }
