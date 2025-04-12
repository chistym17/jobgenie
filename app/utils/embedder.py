import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("HUGGINGFACE_API_URL")
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY") 

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

def get_embedding(text: str) -> list[float] | None:
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": text})
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list) and all(isinstance(x, float) for x in data):
            return data
        else:
            print("Unexpected response format:", data)
            return None

    except requests.exceptions.RequestException as e:
        print("HTTP error occurred:", e)
        return None
    except ValueError as e:
        print("Failed to parse JSON:", e)
        return None
    except Exception as e:
        print("Unexpected error:", e)
        return None


if __name__ == "__main__":
    text = "Qdrant is a vector database for embeddings."
    embedding = get_embedding(text)
    if embedding:
        print("Embedding successful! First 10 values:", embedding[:10])
    else:
        print("Embedding failed.")
