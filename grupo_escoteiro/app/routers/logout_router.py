from fastapi.responses import RedirectResponse
from fastapi import APIRouter
from starlette.status import HTTP_302_FOUND

router = APIRouter()

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=HTTP_302_FOUND)
    response.delete_cookie("token")  # nome correto do cookie
    return response