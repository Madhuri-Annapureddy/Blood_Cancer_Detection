from fastapi import APIRouter

router = APIRouter()


@router.get("/queue")
def review_queue() -> dict[str, str]:
    return {"message": "not implemented"}


@router.post("/approve")
def approve() -> dict[str, str]:
    return {"message": "not implemented"}


@router.post("/override")
def override() -> dict[str, str]:
    return {"message": "not implemented"}


@router.post("/retest")
def retest() -> dict[str, str]:
    return {"message": "not implemented"}
