import os
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.const import TodoItemStatusCode

from .models.item_model import ItemModel
from .models.list_model import ListModel    # SQLAlchemyのモデル定義

from fastapi import Depends
from .dependencies import get_db    # 依存関係を注入。DBセッション管理
from sqlalchemy import select, and_
from sqlalchemy.orm import Session


DEBUG = os.environ.get("DEBUG", "") == "true"

app = FastAPI(
    title="Python Backend Stations",
    debug=DEBUG,
)

if DEBUG:
    from debug_toolbar.middleware import DebugToolbarMiddleware

    # panelsに追加で表示するパネルを指定できる
    app.add_middleware(
        DebugToolbarMiddleware,
        panels=["app.database.SQLAlchemyPanel"],
    )


class NewTodoItem(BaseModel):
    """TODO項目新規作成時のスキーマ."""

    title: str = Field(title="Todo Item Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo Item Description", min_length=1, max_length=200)
    due_at: datetime | None = Field(default=None, title="Todo Item Due")


class UpdateTodoItem(BaseModel):
    """TODO項目更新時のスキーマ."""

    title: str | None = Field(default=None, title="Todo Item Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo Item Description", min_length=1, max_length=200)
    due_at: datetime | None = Field(default=None, title="Todo Item Due")
    complete: bool | None = Field(default=None, title="Set Todo Item status as completed")


class ResponseTodoItem(BaseModel):
    """TODOリストのレスポンススキーマ."""

    id: int
    todo_list_id: int
    title: str = Field(title="Todo Item Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo Item Description", min_length=1, max_length=200)
    status_code: TodoItemStatusCode = Field(title="Todo Status Code")
    due_at: datetime | None = Field(default=None, title="Todo Item Due")
    created_at: datetime = Field(title="datetime that the item was created")
    updated_at: datetime = Field(title="datetime that the item was updated")


class NewTodoList(BaseModel):
    """TODOリスト新規作成時のスキーマ."""

    title: str = Field(title="Todo List Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo List Description", min_length=1, max_length=200)


class UpdateTodoList(BaseModel):
    """TODOリスト更新時のスキーマ."""

    title: str | None = Field(default=None, title="Todo List Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo List Description", min_length=1, max_length=200)


class ResponseTodoList(BaseModel):
    """TODOリストのレスポンススキーマ."""

    id: int
    title: str = Field(title="Todo List Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo List Description", min_length=1, max_length=200)
    created_at: datetime = Field(title="datetime that the item was created")
    updated_at: datetime = Field(title="datetime that the item was updated")


@app.get("/echo", tags=["Echo"])
def get_echo(message: str, name: str):
    return {"Message": message + " " + name + "!"}

@app.get("/health", tags=["System"])
def get_health():
    return {"status": "ok"}

@app.get("/lists/{todo_list_id}", tags=["Todoリスト"])
def get_todo_list(todo_list_id: int, db: Session = Depends(get_db)):
    # db_item = Session.query(ListModel).filter(ListModel.id == todo_list_id).first()
    stmt = select(ListModel).where(ListModel.id == todo_list_id)
    result = db.execute(stmt)
    db_item = result.scalar_one_or_none()

    if db_item is None:
        return {"error": "Todo list not found"}
    
    return db_item

# クライアントからのリクエストボディをNewTodoList型で受け取る
# get_db()を使ってデータベースセッションを取得
# Depends(get_db)により、関数の引数としてdbを渡せば自動でDBに接続できる
@app.post("/lists", response_model=ResponseTodoList, tags=["Todoリスト"])
def post_todo_list(todo_list: NewTodoList, db: Session = Depends(get_db)):  
    """新しいTODOリストを作成するAPI"""

    # 新しいリストを作成。ListModelインスタンスを生成
    new_list = ListModel(
        title=todo_list.title,
        description=todo_list.description
    )

    db.add(new_list)    # 追加
    db.commit()     # 保存
    db.refresh(new_list)    # 保存後に最新のデータを取得

    # 作成したnew_listをレスポンスとして返す
    # response_model=NewTodoListのため、FastAPIは自動でJSONに変換する
    return new_list

@app.put("/lists/{todo_list_id}", response_model=ResponseTodoList, tags=["Todoリスト"])
def put_todo_list(todo_list_id: int, update_data: UpdateTodoList, db: Session = Depends(get_db)):
    """Todoリストを更新するAPI"""

    # 指定されたtodo_list_idのリストを取得
    todo_list = db.get(ListModel, todo_list_id)

    # update_dataに新しい値があれば更新
    if update_data.title is not None:
        todo_list.title = update_data.title
    if update_data.description is not None:
        todo_list.description = update_data.description

    db.commit()
    db.refresh(todo_list)

    return todo_list

@app.delete("/lists/{todo_list_id}", response_model=dict, tags=["Todoリスト"])
def delete_todo_list(todo_list_id: int, db: Session = Depends(get_db)):
    """Todoリストを削除するAPI"""

    # 指定されたtodo_list_idのリストを取得
    todo_list = db.get(ListModel, todo_list_id)

    db.delete(todo_list)
    db.commit()

    return {}

@app.get("/lists/{todo_list_id}/items/{todo_item_id}", response_model=ResponseTodoItem, tags=["Todo項目"])
def get_todo_item(todo_list_id: int, todo_item_id: int, db: Session = Depends(get_db)):
    """Todo項目を取得するAPI"""

    # SQL文の作成
    stmt = select(ItemModel).where(
        and_(ItemModel.id == todo_item_id, ItemModel.todo_list_id == todo_list_id)
    )
    result = db.execute(stmt)   # DBに問い合わせ
    db_item = result.scalar_one_or_none()   # 単一の結果を取得

    if db_item is None:
        return {"error": "Todo list not found"}
    
    return db_item

@app.post("/lists/{todo_list_id}/items", response_model=ResponseTodoItem, tags=["Todo項目"])
def post_todo_item(todo_list_id: int, todo_item_list: NewTodoItem, db: Session = Depends(get_db)):
    """Todo項目を作成するAPI"""

    new_list = ItemModel(
        todo_list_id = todo_list_id,
        title = todo_item_list.title,
        description = todo_item_list.description,
        due_at = todo_item_list.due_at,
        status_code = TodoItemStatusCode.NOT_COMPLETED.value
    )

    db.add(new_list)
    db.commit()
    db.refresh(new_list)

    return new_list

@app.put("/lists/{todo_list_id}/items/{todo_item_id}", response_model=ResponseTodoItem, tags=["Todo項目"])
def put_todo_item(todo_list_id: int, todo_item_id: int, update_data: UpdateTodoItem, db: Session = Depends(get_db)):
    """Todo項目を更新するAPI"""

    stmt = select(ItemModel).where(
        and_(ItemModel.id == todo_item_id, ItemModel.todo_list_id == todo_list_id)
    )
    result = db.execute(stmt)
    db_item = result.scalar_one_or_none()

    if db_item is None:
        return {"error": "Todo list not found"}
    
    if update_data.title is not None:
        db_item.title = update_data.title
    if update_data.description is not None:
        db_item.description = update_data.description
    if update_data.due_at is not None:
        db_item.due_at = update_data.due_at
    if update_data.complete is not None:
        if update_data.complete:
            db_item.status_code = TodoItemStatusCode.COMPLETED.value
        else:
            db_item.status_code = TodoItemStatusCode.NOT_COMPLETED.value

    db.commit()
    db.refresh(db_item)

    return db_item

@app.delete("/lists/{todo_list_id}/items/{todo_item_id}", response_model=dict, tags=["Todo項目"])
def delete_todo_item(todo_list_id: int, todo_item_id: int, db: Session = Depends(get_db)):
    """Todo項目を削除するAPI"""

    stmt = select(ItemModel).where(
        and_(ItemModel.id == todo_item_id, ItemModel.todo_list_id == todo_list_id)
    )
    result = db.execute(stmt)
    db_item = result.scalar_one_or_none()

    if db_item is None:
        return {"error": "Todo list not found"}
    
    db.delete(db_item)
    db.commit()

    return {}