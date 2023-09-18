from fastapi import FastAPI

from admin_service.core.const import (
    OPEN_API_DESCRIPTION,
    OPEN_API_TITLE,
)
from admin_service.endpoints import (
    auth,
    admin_users,
    tg_accounts,
    gpt_accounts,
    categories,
    tg_users,
    messages
)
from admin_service.version import __version__

app = FastAPI(
    title=OPEN_API_TITLE,
    description=OPEN_API_DESCRIPTION,
    version=__version__,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)

app.include_router(auth.router)
app.include_router(admin_users.router)
app.include_router(tg_accounts.router)
app.include_router(gpt_accounts.router)
app.include_router(categories.router)
app.include_router(tg_users.router)
app.include_router(messages.router)
