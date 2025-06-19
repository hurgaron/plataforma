from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from app.database import engine
from app.models import empresa, usuario
from app.routers import empresa_router, usuario_router
# from app.routers import login_router
from app.routers import jovem_router
from app.routers import adulto_router
from app.routers import fornecedor_router
from app.routers import doc_router
from app.routers import auth_router, dashboard_router
from app.routers import logout_router
from app.routers import mensalidade_router
from app.routers import relatorio_mensalidades_router
from app.routers import conta_router
from app.routers import fluxo_router
from app.routers import almoxarifado_router
from app.routers import movimentacao_router
from app.routers import calendario_router
from app.routers import certificados_router
from app.routers import certificado_numeracao_router
from app.routers import atividade_admin_router
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.add_middleware(SessionMiddleware, secret_key="sua_chave_secreta_segura")

# Incluindo routers
app.include_router(empresa_router.router)
app.include_router(usuario_router.router)
# app.include_router(login_router.router)
app.include_router(jovem_router.router)
app.include_router(adulto_router.router)
app.include_router(fornecedor_router.router)
app.include_router(doc_router.router)
app.include_router(auth_router.router)
app.include_router(dashboard_router.router)
app.include_router(logout_router.router)
app.include_router(mensalidade_router.router)
app.include_router(relatorio_mensalidades_router.router)
app.include_router(conta_router.router)
app.include_router(fluxo_router.router)
app.include_router(almoxarifado_router.router)
app.include_router(movimentacao_router.router)
app.include_router(calendario_router.router)
app.include_router(certificados_router.router)
app.include_router(certificado_numeracao_router.router)
app.include_router(atividade_admin_router.router)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/login")