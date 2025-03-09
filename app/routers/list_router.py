from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..crud import list_crud
from ..schemas.list_schema import NewTodoList, UpdateTodoList, ResponseTodoList
from app.dependencies import get_db

router = APIRouter(prefix="/lists", tags=["TODOリスト"],)

@router.get("/{todo_list_id}", response_model=ResponseTodoList)
def get_todo_list(todo_list_id: int, db: Session = Depends(get_db)):
  return list_crud.get_todo_list(db, todo_list_id)

# クライアントからのリクエストボディをNewTodoList型で受け取る
# get_db()を使ってデータベースセッションを取得
# Depends(get_db)により、関数の引数としてdbを渡せば自動でDBに接続できる
@router.post("/", response_model=ResponseTodoList)
def post_todo_list(todo_list: NewTodoList, db: Session = Depends(get_db)):
  return list_crud.post_todo_list(db, todo_list)

@router.put("/{todo_list_id}", response_model=ResponseTodoList)
def put_todo_list(todo_list_id: int, update_data: UpdateTodoList, db: Session = Depends(get_db)):
  return list_crud.put_todo_list(db, todo_list_id, update_data)

@router.delete("/{todo_list_id}", response_model=dict)
def delete_todo_list(todo_list_id: int, db: Session = Depends(get_db)):
  return list_crud.delete_todo_list(db, todo_list_id)

@router.get("/", response_model=List[ResponseTodoList])
def get_todo_lists(db: Session = Depends(get_db)):
  return list_crud.get_todo_lists(db)