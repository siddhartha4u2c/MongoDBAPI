from fastapi import FastAPI
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.encoders import jsonable_encoder
from typing import List

print("1️⃣ Starting FastAPI app")

# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI()

# -----------------------------
# MongoDB connection
# -----------------------------
MONGO_URI = "mongodb+srv://sidd:sidd4u2c@cluster0.pu8mxsz.mongodb.net/?retryWrites=true&w=majority"
print("2️⃣ Mongo URI set:", MONGO_URI)

try:
    client = AsyncIOMotorClient(MONGO_URI)
    db = client["sidd4u2c"]
    collection = db["sidd_collection"]
    print("3️⃣ MongoDB client, DB, and collection initialized")
except Exception as e:
    print("❌ MongoDB connection error:", e)

# -----------------------------
# Pydantic models
# -----------------------------
class EuronData(BaseModel):
    name: str
    phone: int
    city: str
    course: str

class EuronDataResponse(EuronData):
    id: str  # Include MongoDB _id as string

# -----------------------------
# Helper function
# -----------------------------
def euron_helper(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

# -----------------------------
# Root endpoint
# -----------------------------
@app.get("/")
async def root():
    print("✅ Root endpoint called")
    return {"msg": "FastAPI working!"}

# -----------------------------
# Insert endpoint
# -----------------------------
@app.post("/euron/insert", response_model=EuronDataResponse)
async def insert_data(data: EuronData):
    print("📝 Insert endpoint called with:", data.dict())
    result = await collection.insert_one(data.dict())
    inserted_doc = await collection.find_one({"_id": result.inserted_id})
    inserted_doc = euron_helper(inserted_doc)
    print("✔ Inserted document:", inserted_doc)
    return inserted_doc

# -----------------------------
# Get all data endpoint (Swagger-safe)
# -----------------------------
@app.get("/euron/getdata", response_model=List[EuronDataResponse])
async def get_all_data():
    print("📋 Get all data endpoint called")
    try:
        # Fetch all documents as a list (async-safe for Swagger)
        docs = await collection.find({}).to_list(length=1000)  # adjust length as needed
        items = [EuronDataResponse(**euron_helper(doc)) for doc in docs]
        print(f"✔ Retrieved {len(items)} documents")
        return jsonable_encoder(items)
    except Exception as e:
        print("❌ Error fetching documents:", e)
        return []

print("4️⃣ FastAPI app setup complete")

