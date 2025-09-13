import fastapi

router = fastapi.APIRouter()

@router.get("/health")
async def health():
    return fastapi.Response(status_code=fastapi.status.HTTP_200_OK)

