from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
import uuid

# .env file se URL aur API key load karo
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# Qdrant se connect hone ke liye client banao
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

# Ye model text ko "embedding" (numbers) mein convert karta hai
model = SentenceTransformer('all-MiniLM-L6-v2')

COLLECTION_NAME = "mail_memory"


def setup_collection():
    """
    Collection banata hai agar already nahi hai toh
    """
    collections = client.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)
    
    if not exists:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        print(f"Collection '{COLLECTION_NAME}' ban gayi ✅")
    else:
        print(f"Collection '{COLLECTION_NAME}' pehle se hai ✅")


def reset_collection():
    """
    Purani collection delete karke nayi banata hai
    Sirf testing/cleanup ke liye use karo
    """
    collections = client.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)
    
    if exists:
        client.delete_collection(COLLECTION_NAME)
        print("Purani collection delete ho gayi 🗑️")
    
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )
    print("Nayi collection ban gayi ✅")


def save_memory(text, metadata=None, similarity_threshold=0.9):
    """
    Naya fact/memory save karta hai
    Pehle check karta hai ki milta julta fact already toh nahi hai — 
    agar hai, toh duplicate save nahi karta
    """
    embedding = model.encode(text).tolist()
    
    existing = client.query_points(
        collection_name=COLLECTION_NAME,
        query=embedding,
        limit=1
    ).points
    
    if existing and existing[0].score >= similarity_threshold:
        print(f"Already saved hai, skip kar diya: '{text}'")
        return
    
    point = PointStruct(
        id=str(uuid.uuid4()),
        vector=embedding,
        payload={
            "text": text,
            **(metadata or {})
        }
    )
    
    client.upsert(collection_name=COLLECTION_NAME, points=[point])
    print(f"Memory save ho gayi: '{text}'")


def search_memory(query, limit=3):
    """
    Query se milta julta purana fact dhoondta hai
    """
    query_embedding = model.encode(query).tolist()
    
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=limit
    ).points
    
    return [
        {"text": r.payload.get("text"), "score": r.score}
        for r in results
    ]
COLLECTION_NAME = "mail_memory" 
EMAIL_COLLECTION_NAME = "email_memory"


def setup_email_collection():
    """
    Email collection banata hai agar already nahi hai toh
    """
    collections = client.get_collections().collections
    exists = any(c.name == EMAIL_COLLECTION_NAME for c in collections)

    if not exists:
        client.create_collection(
            collection_name=EMAIL_COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        print(f"Collection '{EMAIL_COLLECTION_NAME}' ban gayi ✅")
    else:
        print(f"Collection '{EMAIL_COLLECTION_NAME}' pehle se hai ✅")


def index_email(email):
    """
    Ek email ko Qdrant mein save/update karta hai.
    Gmail ka message id hi point id ban jaata hai — isse duplicate
    check karne ki zaroorat nahi, same email dobara aaya toh
    bas overwrite (upsert) ho jayega.
    """
    # Subject + snippet dono milake ek text banate hain jisse embedding banegi
    text = f"From: {email['from']} | Subject: {email['subject']} | {email['snippet']}"

    embedding = model.encode(text).tolist()

    # Gmail message id (jaise '18d2f...') ko UUID mein convert karte hain
    # kyunki Qdrant ko UUID ya integer id chahiye
    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, email['id']))

    point = PointStruct(
        id=point_id,
        vector=embedding,
        payload={
            "gmail_id": email['id'],
            "from": email['from'],
            "subject": email['subject'],
            "date": email['date'],
            "snippet": email['snippet'],
            "text": text
        }
    )

    client.upsert(collection_name=EMAIL_COLLECTION_NAME, points=[point])


def search_emails(query, limit=3):
    """
    Query se semantically similar purane emails dhoondta hai
    (exact keyword match nahi, meaning ke basis pe)
    """
    query_embedding = model.encode(query).tolist()

    results = client.query_points(
        collection_name=EMAIL_COLLECTION_NAME,
        query=query_embedding,
        limit=limit
    ).points

    return [
        {
            "from": r.payload.get("from"),
            "subject": r.payload.get("subject"),
            "snippet": r.payload.get("snippet"),
            "date": r.payload.get("date"),
            "score": r.score
        }
        for r in results
    ]


# Test karne ke liye
if __name__ == '__main__':
    reset_collection()
    
    save_memory("Rakesh sir ka email rakesh@company.com hai, unke mail hamesha important hote hain")
    save_memory("Priya ka email priya@example.com hai, wo client hai")
    save_memory("Rakesh sir ka email rakesh@company.com hai, unke mail hamesha important hote hain")  # Ye duplicate hai, skip hona chahiye
    
    print("\n--- Search Test ---")
    results = search_memory("Rakesh")
    for r in results:
        print(f"Score: {r['score']:.3f} — {r['text']}")