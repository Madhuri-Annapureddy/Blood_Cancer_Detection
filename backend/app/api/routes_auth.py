from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
def login() -> dict[str, str]:
    return {"message": "not implemented"}


@router.post("/register")
def register() -> dict[str, str]:
    return {"message": "not implemented"}
