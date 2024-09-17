import time
import threading
from fastapi import APIRouter, Response, Depends
from core.dependencies import PermissionDependency, AllowAll
from modules.users.services import router as user_router
from modules.transactions.services import router as transaction_router

router = APIRouter(
     prefix="/api/v1"
)

# Health check endpoint
@router.head("/health", dependencies=[Depends(PermissionDependency([AllowAll]))], tags=["Health-Check"])
async def health_check():
    start_time = time.time()
    process_time = time.time() - start_time
    return {
    "status":"Healthy",
    "totalTimeTaken":str(process_time),
    "entities":[]
}


router.include_router(user_router)
router.include_router(transaction_router)


__all__ = ["router"]