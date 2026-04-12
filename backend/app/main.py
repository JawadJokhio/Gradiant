import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Import Routers
from app.api.history_routes import router as history_router
from app.api.geography_map_routes import router as map_router
from app.api.routes_papers import router as papers_router
from app.api.geography_image_routes import router as image_analysis_router

app = FastAPI(title=settings.app_name)

# Enable CORS for frontend
origins = ["*"] # Broaden for development, tighten later if needed

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(history_router)
app.include_router(map_router)
app.include_router(papers_router)
app.include_router(image_analysis_router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
