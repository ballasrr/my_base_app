from routers.items import router as items_router
from fastapi import  FastAPI

app = FastAPI()

app.include_router(items_router, prefix='/items')
