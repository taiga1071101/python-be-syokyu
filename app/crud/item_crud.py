from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.models.item_model import ItemModel
from app.models.list_model import ListModel
from app.const import TodoItemStatusCode
from app.schemas.item_schema import NewTodoItem, UpdateTodoItem

def get_todo_item(db: Session, todo_list_id: int, todo_item_id: int):
    """Todo項目を取得するAPI"""

    # SQL文の作成
    stmt = select(ItemModel).where(
        and_(ItemModel.id == todo_item_id, ItemModel.todo_list_id == todo_list_id)
    )
    result = db.execute(stmt)   # DBに問い合わせ
    return result.scalar_one_or_none()   # 単一の結果を取得

def post_todo_item(db: Session, todo_list_id: int, todo_item_list: NewTodoItem):
    """Todo項目を作成するAPI"""

    stmt = select(ListModel).where(ListModel.id == todo_list_id)
    result = db.execute(stmt).scalar_one_or_none()
    if result is None:
        return None

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

def put_todo_item(db: Session, todo_list_id: int, todo_item_id: int, update_data: UpdateTodoItem):
    """Todo項目を更新するAPI"""

    stmt = select(ItemModel).where(
        and_(ItemModel.id == todo_item_id, ItemModel.todo_list_id == todo_list_id)
    )
    result = db.execute(stmt)
    db_item = result.scalar_one_or_none()

    if db_item is None:
        return
    
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

def delete_todo_item(db: Session, todo_list_id: int, todo_item_id: int):
    """Todo項目を削除するAPI"""

    stmt = select(ItemModel).where(
        and_(ItemModel.id == todo_item_id, ItemModel.todo_list_id == todo_list_id)
    )
    result = db.execute(stmt)
    db_item = result.scalar_one_or_none()

    if db_item is None:
        return
    
    db.delete(db_item)
    db.commit()

    return {}

def get_todo_items(db: Session, todo_list_id: int):
    """Todo項目一覧を取得するAPI"""

    stmt = select(ItemModel).where(
        and_(ItemModel.todo_list_id == todo_list_id)
    )
    result = db.execute(stmt)
    return result.scalars().all()