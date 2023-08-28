from fastapi import FastAPI

from admin_service.core.const import (
    OPEN_API_DESCRIPTION,
    OPEN_API_TITLE,
)
from admin_service.endpoints import (
    auth,
    users,
    tg_accounts,
    gpt_accounts
)
from admin_service.version import __version__

app = FastAPI(
    title=OPEN_API_TITLE,
    description=OPEN_API_DESCRIPTION,
    version=__version__,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tg_accounts.router)
app.include_router(gpt_accounts.router)
