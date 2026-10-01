from fastapi import APIRouter

router = APIRouter()


@router.post("/")
def predict() -> dict[str, str]:
    return {"message": "not implemented"}
