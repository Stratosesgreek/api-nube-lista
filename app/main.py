from typing import Union, List, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
import models, database

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine) #crea las tablas con el orm

class User(BaseModel):
    name: str
    emails: List[EmailStr]

class UserUpdate(BaseModel):
    name: Optional[str] = None
    emails: Optional[List[EmailStr]] = None

@app.get("/status/")
def get_status():
    return {"message": "pong"}

@app.get("/directories/")
def get_users(page: int = 1, per_page: int = 10, db: database.Session = Depends(database.get_db)):
    # Calcula el total de objetos para determinar si hay una siguiente página
    total_users = db.query(models.Users).count()
    total_pages = (total_users - 1) // per_page + 1

    # Obtiene los usuarios de la página actual
    users = db.query(models.Users).offset((page - 1) * per_page).limit(per_page).all()

    # Construye el enlace a la siguiente página si esta existe
    next_page_url =  f"http://127.0.0.1:8000/directories/?page={page + 1}" + (f"&per_page={per_page}" if per_page != 10 else "") if page < total_pages else None

    # Construye la respuesta
    response = {
        "count": total_users,
        "next": next_page_url,
        "previous": None if page == 1 else f"http://127.0.0.1:8000/directories/?page={page - 1}" + (f"&per_page={per_page}" if per_page != 10 else ""),
        "results": users
    }
    return response

@app.post("/directories/", status_code=status.HTTP_201_CREATED)
def create_user(user: User, db: database.Session = Depends(database.get_db)):
    # Crear una nueva instancia de usuario
    new_user = models.Users(name=user.name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # Iterar sobre la lista de correos electrónicos y crear instancias de Emails
    for email in user.emails:
        new_email = models.Emails(email=email, user_id=new_user.id)
        db.add(new_email)
    db.commit()
    return {
        "id": new_user.id,
        "name": new_user.name,
        "emails": user.emails
    }


@app.get("/directories/{id}", response_model=User)
def get_directory(id: int, db: database.Session = Depends(database.get_db)):
    # Busca el usuario en la base de datos por su ID
    db_user = db.query(models.Users).filter(models.Users.id == id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    # Busca todos los correos electrónicos relacionados con el usuario
    db_emails = db.query(models.Emails).filter(models.Emails.user_id == db_user.id).all()
    email_list = [email.email for email in db_emails]
    return User(
        id=db_user.id,
        name=db_user.name,
        emails=email_list
    )

@app.delete("/directories/{id}",status_code=status.HTTP_200_OK )
def delete_user(id: int, db: database.Session = Depends(database.get_db)):
    # Busca el usuario en la base de datos por su ID
    db_user = db.query(models.Users).filter(models.Users.id == id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    # Elimina todos los correos electrónicos relacionados con el usuario
    db.query(models.Emails).filter(models.Emails.user_id == db_user.id).delete()
    # Elimina el usuario
    db.delete(db_user)
    # Confirma los cambios en la base de datos
    db.commit()
    return {"detail": "usuario eliminado exitosamente"}

@app.put("/directories/{id}", response_model=User)
def update_user(id: int, user: User, db: database.Session = Depends(database.get_db)):
    # Busca el usuario en la base de datos por su ID
    db_user = db.query(models.Users).filter(models.Users.id == id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    # Actualiza los campos del usuario si se proporcionan
    db_user.name = user.name
    # Primero elimina los correos electrónicos existentes
    db.query(models.Emails).filter(models.Emails.user_id == db_user.id).delete()
    # Luego agrega los nuevos correos electrónicos
    for email in user.emails:
        new_email = models.Emails(email=email, user_id=db_user.id)
        db.add(new_email)
    # Confirma los cambios en la base de datos
    db.commit()
    db.refresh(db_user)
    # Se consulta el usuario actualizado
    db_user = db.query(models.Users).filter(models.Users.id == id).first()
    db_emails = db.query(models.Emails).filter(models.Emails.user_id == db_user.id).all()
    lista_de_emails = [email_obj.email for email_obj in db_emails]
    # Devuelve el usuario actualizado
    return User(
        id=db_user.id,
        name=db_user.name,
        emails=lista_de_emails
    )

@app.patch("/directories/{id}", response_model=User)
def update_user(id: int, user_update: UserUpdate, db: database.Session = Depends(database.get_db)):
    # Busca el usuario en la base de datos por su ID
    db_user = db.query(models.Users).filter(models.Users.id == id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    # Actualiza los campos del usuario si se proporcionan
    if user_update.name is not None:
        db_user.name = user_update.name
    # Si se proporciona una lista de correos electrónicos, primero elimina los existentes
    if user_update.emails is not None:
        db.query(models.Emails).filter(models.Emails.user_id == db_user.id).delete()
        # Luego agrega los nuevos correos electrónicos
        for email in user_update.emails:
            new_email = models.Emails(email=email, user_id=db_user.id)
            db.add(new_email)
    # Confirma los cambios en la base de datos
    db.commit()
    db.refresh(db_user)
    # Se consulta el usuario actualizado
    db_user = db.query(models.Users).filter(models.Users.id == id).first()
    db_emails = db.query(models.Emails).filter(models.Emails.user_id == db_user.id).all()
    lista_de_emails = [email_obj.email for email_obj in db_emails]
    # Devuelve el usuario actualizado
    return User(
        id=db_user.id,
        name=db_user.name,
        emails=lista_de_emails
    )
