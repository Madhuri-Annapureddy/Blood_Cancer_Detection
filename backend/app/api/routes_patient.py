from fastapi import APIRouter

router = APIRouter()


@router.post("/upload")
def upload() -> dict[str, str]:
    return {"message": "not implemented"}


@router.get("/results")
def view_results() -> dict[str, str]:
    return {"message": "not implemented"}


@router.get("/history")
def view_history() -> dict[str, str]:
    return {"message": "not implemented"}
