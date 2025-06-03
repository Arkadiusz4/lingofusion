from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.predict import router as predict_router

app = FastAPI(title="MT+LoRA API")


@app.on_event("startup")
async def load_all_models():
    import app.models.translator


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict_router, prefix="/api")
