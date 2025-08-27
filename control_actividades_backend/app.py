from fastapi import FastAPI
from routes import usuarios, actividades

app = FastAPI(title="Control de actividades")

app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(actividades.router, prefix="/actividades", tags=["Actividades"])


@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a Control de Actividades"}