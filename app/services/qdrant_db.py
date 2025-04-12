from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure environment variables are set
QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')

if not QDRANT_URL or not QDRANT_API_KEY:
    raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set in the environment")

# Initialize the Qdrant client
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

try:
    # Create the collection
    client.create_collection(
        collection_name="job_embeddings",
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )
    print("✅ Collection created.")
except Exception as e:
    print(f"❌ Error creating collection: {e}")