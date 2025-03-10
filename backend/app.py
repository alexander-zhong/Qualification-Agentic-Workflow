from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


# Enable Cors TODO DISABLE ALL ORIGINS WHEN IMPLEMENTING
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)


# Load and serve the OpenAPI JSON
@app.get("/openapi.json", include_in_schema=False)
async def get_openapi():
    with open("backend/openapi.json") as f:
        return json.load(f)
    
