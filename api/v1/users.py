from fastapi import APIRouter

router = APIRouter()

@router.get("/users/health")
def users_health():
    return {"status": "ok"}
