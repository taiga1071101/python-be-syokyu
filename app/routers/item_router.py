from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..crud import item_crud
from ..schemas.item_schema import ResponseTodoItem, NewTodoItem, UpdateTodoItem
from app.dependencies import get_db

router = APIRouter(
      prefix="/lists",
      tags=["TODO項目"],
  )

@router.get("/{todo_list_id}/items/{todo_item_id}", response_model=ResponseTodoItem)
def get_todo_item(todo_list_id: int, todo_item_id: int, db: Session = Depends(get_db)):
    result = item_crud.get_todo_item(db, todo_list_id, todo_item_id)
    if result is None:
        raise HTTPException(status_code=404, detail="result not found")
    return result

@router.post("/{todo_list_id}/items", response_model=ResponseTodoItem)
def post_todo_item(todo_list_id: int, todo_item_list: NewTodoItem, db: Session = Depends(get_db)):
    result = item_crud.post_todo_item(db, todo_list_id, todo_item_list)
    if result is None:
        raise HTTPException(status_code=404, detail="result not found")
    return result

@router.put("/{todo_list_id}/items/{todo_item_id}", response_model=ResponseTodoItem)
def put_todo_item(todo_list_id: int, todo_item_id: int, update_data: UpdateTodoItem, db: Session = Depends(get_db)):
    result = item_crud.put_todo_item(db, todo_list_id, todo_item_id, update_data)
    if result is None:
        raise HTTPException(status_code=404, detail="result not found")
    return result

@router.delete("/{todo_list_id}/items/{todo_item_id}", response_model=dict)
def delete_todo_item(todo_list_id: int, todo_item_id: int, db: Session = Depends(get_db)):
    result = item_crud.delete_todo_item(db, todo_list_id, todo_item_id)
    if result is None:
        raise HTTPException(status_code=404, detail="result not found")
    return result

@router.get("/{todo_list_id}/items", response_model=List[ResponseTodoItem])
def get_todo_items(todo_list_id: int, page: int, per_page: int, db: Session = Depends(get_db)):
    return item_crud.get_todo_items(db, todo_list_id, page, per_page)