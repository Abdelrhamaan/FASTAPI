import time

from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel

from psycopg2 import connect
from psycopg2.extras import RealDictCursor

from . import models
from .database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

# while True:
#     try:
#         conn = connect(
#             host='localhost', database='fastapi', 
#             user='postgres', password='Aboody@190297', 
#             cursor_factory=RealDictCursor,
#         )

#         cursor = conn.cursor()
#         print('Database connected Successfully!')
#         break 
#     except Exception as error:
#         print('Error', error)   
#         time.sleep(3)

class Post(BaseModel):
    title : str
    content : str
    published: bool = True
    rating: Optional[int] = None


my_posts = [
    {"id": 1, "title": "two scoops", "content": "django book", "published": True},
    {"id": 2, "title": "Django For Example", "content": "django book", "published": True},
    {"id": 3, "title": "Django For Example", "content": "django book", "published": False},
]
@app.get('/')
async def root():
    return {"message" : "Hello World"}
    
    
@app.get('/posts')
async def get_posts():
    cursor.execute('''SELECT * FROM post''')
    posts = cursor.fetchall()
    # print(posts)
    return {'posts' : posts}


# @app.post('/createposts')
# def create_post(payload: dict = Body(...)):
#     print("paylaod", payload)
#     return {"message" : "data send successfully"}


@app.post('/createposts', status_code=status.HTTP_201_CREATED)
def create_post(new_post: Post):
    # never use f'{}' because of sql injection
    cursor.execute(''' INSERT INTO post (title, content, published) VALUES (%s, %s, %s) RETURNING *''', (
        new_post.title, new_post.content, new_post.published
    )
                   )
    new_post = cursor.fetchone()
    conn.commit()
    return new_post

def func():
    ...
    
    
@app.get('/post/{id}')
def get_post(id: int):
    print("id", id)
    cursor.execute(''' SELECT * FROM post WHERE id = %s''', (str(id),))
    post = cursor.fetchone()
    if post:
        print(post)
        return {"my_post": post}
    # return {"msg": "No Post with That Id"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No Post With That Id: {id}")


# option 1
# @app.delete('/delete/{id}', status_code=status.HTTP_204_NO_CONTENT)
# def delete_post(id: int):
#     cursor.execute(''' DELETE FROM post WHERE id = %s RETURNING * ''', (str(id),))
#     deleted_post = cursor.fetchone()
#     print("del", deleted_post)
#     if not deleted_post :
#         raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=f"No Post With That Id: {id}")
    # return {'deleted_post': deleted_post}
    
# option2
@app.delete('/delete/{id}', status_code=status.HTTP_200_OK)
def delete_post(id: int):
    cursor.execute(''' DELETE FROM post WHERE id = %s RETURNING * ''', (str(id),))
    deleted_post = cursor.fetchone()
    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No Post With That Id: {id}")
    conn.commit()

    # Return the deleted post with a 200 status
    return {'deleted_post': deleted_post}



@app.put('/update/{id}', status_code=status.HTTP_200_OK)
def update_post(id: int, post: Post):
    cursor.execute(
        ''' UPDATE post set title = %s, content = %s, published = %s WHERE id = %s RETURNING *''',
        (post.title, post.content, post.published, id)
    )
    conn.commit()
    updated_post = cursor.fetchone()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No Post With That Id: {id}")

    return {'updated_post' : updated_post}