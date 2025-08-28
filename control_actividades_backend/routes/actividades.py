from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from db import get_connection

router = APIRouter()

# Schema para crear actividad
class ActividadCreate(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=100)
    descripcion: str | None = None
    fecha_entrega: str  # formato: "2025-09-05"
    hora_entrega: str   # formato: "23:59:00"
    id_clase: int
    valor_maximo: float = Field(..., ge=0, le=10)


@router.get("/")
def listar_actividades():
    connection = get_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM actividad")
    actividades = cursor.fetchall()

    cursor.close()
    connection.close()
    return {"actividades": actividades}


@router.post("/")
def crear_actividad(data: ActividadCreate):
    connection = get_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")

    cursor = connection.cursor()

    # Combinar fecha y hora
    fecha_entrega_completa = f"{data.fecha_entrega} {data.hora_entrega}"
    fecha_creacion = datetime.now()

    query = """
        INSERT INTO actividad (titulo, descripcion, fecha_creacion, fecha_entrega, id_clase, valor_maximo)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (
        data.titulo,
        data.descripcion,
        fecha_creacion,
        fecha_entrega_completa,
        data.id_clase,
        data.valor_maximo,
    )

    cursor.execute(query, values)
    connection.commit()
    id_actividad = cursor.lastrowid

    cursor.close()
    connection.close()

    return {"mensaje": "Actividad creada con éxito", "id_actividad": id_actividad}