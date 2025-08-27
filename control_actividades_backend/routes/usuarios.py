from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def listar_usuarios():
    return {"usuarios": ["Juan", "Maria", "Pedro"]}

@router.post("/")
def crear_usuarios(nombre: str):
    return {"mensaje": f"Usuario {nombre} creado con exito"}
