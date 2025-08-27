from fastapi import APIRouter


router = APIRouter()

@router.get("/")
def listar_actividades():
    return {"actividades": ["Examen", "Tareas"]}

@router.post("/")
def crear_actividades(nombre: str):
    return {"mensaje": f"Actividad {nombre} creada con exito"}