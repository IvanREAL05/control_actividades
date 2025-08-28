from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from db import get_connection
import pymysql
from datetime import datetime, time

router = APIRouter()

# Modelos Pydantic
class Grupo(BaseModel):
    nombre: str
    turno: str
    nivel: Optional[str] = None

class Clase(BaseModel):
    nombre_clase: str
    materia: str
    profesor: str
    grupo: str
    dia_semana: str
    hora_inicio: str  # Formato "HH:MM"
    hora_fin: str     # Formato "HH:MM"
    nrc: str

class ImportarClasesRequest(BaseModel):
    grupos: List[Grupo]
    clases: List[Clase]

# Función auxiliar
def convertir_hora(hora_str: str) -> time:
    """Convierte "HH:MM" a objeto time"""
    return datetime.strptime(hora_str, "%H:%M").time()

# Endpoint
@router.post("/clases/importar")
def importar_clases(data: ImportarClasesRequest):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)  # Usamos DictCursor

    # 1️⃣ Insertar grupos
    for g in data.grupos:
        try:
            cursor.execute("""
                INSERT INTO grupo (nombre, turno, nivel)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    turno = VALUES(turno),
                    nivel = VALUES(nivel)
            """, (g.nombre, g.turno, g.nivel))
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Error insertando grupo {g.nombre}: {e}")

    # 2️⃣ Insertar clases y horarios
    clases_map = {}  # Para evitar duplicados en la misma carga
    for c in data.clases:
        # Obtener IDs necesarios
        cursor.execute("SELECT id_profesor FROM profesor WHERE nombre=%s", (c.profesor,))
        prof = cursor.fetchone()
        if not prof:
            continue  # O manejar error
        id_profesor = prof['id_profesor']

        cursor.execute("SELECT id_grupo FROM grupo WHERE nombre=%s", (c.grupo,))
        grp = cursor.fetchone()
        if not grp:
            continue
        id_grupo = grp['id_grupo']

        cursor.execute("SELECT id_materia FROM materia WHERE nombre=%s", (c.materia,))
        mat = cursor.fetchone()
        if not mat:
            continue
        id_materia = mat['id_materia']

        # Clave única temporal para evitar duplicados en la misma carga
        clave = f"{c.nombre_clase}|{id_profesor}|{id_grupo}|{id_materia}|{c.nrc}"
        if clave in clases_map:
            id_clase = clases_map[clave]
        else:
            # Verificar si ya existe clase con ese NRC
            cursor.execute("SELECT id_clase FROM clase WHERE nrc=%s LIMIT 1", (c.nrc,))
            existente = cursor.fetchone()
            if existente:
                id_clase = existente['id_clase']
            else:
                cursor.execute("""
                    INSERT INTO clase (nombre_clase, id_materia, id_grupo, id_profesor, nrc)
                    VALUES (%s, %s, %s, %s, %s)
                """, (c.nombre_clase, id_materia, id_grupo, id_profesor, c.nrc))
                id_clase = cursor.lastrowid
            clases_map[clave] = id_clase

        # Insertar horario_clase evitando duplicados
        hora_inicio = convertir_hora(c.hora_inicio)
        hora_fin = convertir_hora(c.hora_fin)
        try:
            cursor.execute("""
                INSERT IGNORE INTO horario_clase (id_clase, dia, hora_inicio, hora_fin)
                VALUES (%s, %s, %s, %s)
            """, (id_clase, c.dia_semana, hora_inicio, hora_fin))
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Error insertando horario: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    return {"mensaje": "Clases y grupos importados correctamente"}
