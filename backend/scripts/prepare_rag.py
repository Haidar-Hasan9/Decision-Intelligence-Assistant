"""
prepare_rag.py
-------------
Loads the Twitter customer support dataset, filters inbound tweets,
samples, and creates a Chroma vector store out of the tweet text.
Each tweet is a single chunk/document.
"""

import os
import logging
import warnings
import sys

# Suppress HuggingFace warnings BEFORE importing sentence_transformers
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_HTTP_WARNING"] = "1"

# Filter out specific HuggingFace warnings
warnings.filterwarnings("ignore", message=".*unauthenticated requests.*")
warnings.filterwarnings("ignore", message=".*HF Hub.*")

import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

# Suppress HF warning by setting token via environment
os.environ["HF_TOKEN"] = "dummy_token_suppress_warning"

# Suppress huggingface_hub loggers
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==================== CONFIG ====================
# Process ALL cleaned data (no sampling)
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), '..', 'chroma_db')
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
COLLECTION_NAME = 'tweets'
BATCH_SIZE = 512  # For embedding generation

# ==================== 1. Load and clean dataset ====================
logger.info("Loading dataset from project data folder...")
# Use relative path from project root 
file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'twcs.csv')

df_raw = pd.read_csv(file_path)
logger.info(f"Raw dataset shape: {df_raw.shape}")

# Filter inbound tweets and drop empty text
df = df_raw[df_raw['inbound'] == True].copy()
df = df[df['text'].notna() & (df['text'].str.strip() != '')]
logger.info(f"After inbound filter and dropping empty: {df.shape}")

# Use ALL cleaned data (no sampling)
df = df.reset_index(drop=True)
logger.info(f"Processing ALL {len(df)} documents (no sampling)")

# ==================== 2. Prepare documents and IDs ====================
# We'll use the tweet_id as unique id (convert to string)
ids = df['tweet_id'].astype(str).tolist()
documents = df['text'].tolist()

# ==================== 3. Load embedding model ====================
logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# ==================== 4. Generate embeddings in batches and store in Chroma ====================
logger.info("Initialising Chroma persistent client...")
client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

# If collection already exists, we might want to recreate it (or skip)
try:
    client.delete_collection(COLLECTION_NAME)
except:
    pass

collection = client.create_collection(name=COLLECTION_NAME)

# Generate embeddings and add in batches to avoid memory issues
total_docs = len(documents)
for start in range(0, total_docs, BATCH_SIZE):
    end = min(start + BATCH_SIZE, total_docs)
    batch_ids = ids[start:end]
    batch_docs = documents[start:end]
    # Generate embeddings
    embeddings = model.encode(batch_docs, show_progress_bar=False)
    # Add to Chroma
    collection.add(
        ids=batch_ids,
        documents=batch_docs,
        embeddings=embeddings.tolist()
    )
    logger.info(f"  Processed {end}/{total_docs} documents")

logger.info(f"Vector store created at {CHROMA_PERSIST_DIR}")
logger.info(f"Collection '{COLLECTION_NAME}' contains {collection.count()} items")