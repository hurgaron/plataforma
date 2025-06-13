from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.usuario import Usuario
from fastapi import Cookie

# Configurações JWT
SECRET_KEY = "sua_chave_secreta_123"  # troque por uma chave segura
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Segurança da senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verificar_senha(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def autenticar_usuario(db: Session, email: str, senha: str):
    usuario = db.query(Usuario).filter(Usuario.usuemail == email).first()
    if not usuario or not verificar_senha(senha, usuario.ususenha):
        return None
    return usuario

def criar_token(dados: dict, expires_delta: timedelta = None):
    to_encode = dados.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def obter_usuario_logado(
    token: str = Cookie(default=None, alias="access_token"),
    db: Session = Depends(get_db)
):
    credenciais_excecao = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não autorizado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credenciais_excecao

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usucod: int = int(payload.get("sub"))
        if usucod is None:
            raise credenciais_excecao
    except JWTError:
        raise credenciais_excecao

    usuario = db.query(Usuario).filter(Usuario.usucod == usucod).first()
    if usuario is None:
        raise credenciais_excecao

    return usuario
