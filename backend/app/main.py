from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_auth, routes_patient, routes_doctor, routes_predict

app = FastAPI(title="Leukemia Detection Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_auth.router, prefix="/auth", tags=["auth"])
app.include_router(routes_patient.router, prefix="/patient", tags=["patient"])
app.include_router(routes_doctor.router, prefix="/doctor", tags=["doctor"])
app.include_router(routes_predict.router, prefix="/predict", tags=["predict"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}