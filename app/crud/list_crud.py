from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.list_model import ListModel
from app.schemas.list_schema import NewTodoList, UpdateTodoList

def get_todo_list( db: Session, todo_list_id: int):
    """Todoリストを取得するAPI"""

    stmt = select(ListModel).where(ListModel.id == todo_list_id)
    result = db.execute(stmt)
    return result.scalar_one_or_none()

def post_todo_list(db: Session, todo_list: NewTodoList):  
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

def put_todo_list(db: Session, todo_list_id: int, update_data: UpdateTodoList):
    """Todoリストを更新するAPI"""

    # 指定されたtodo_list_idのリストを取得
    todo_list = db.get(ListModel, todo_list_id)
    if todo_list is None:
        return

    # update_dataに新しい値があれば更新
    if update_data.title is not None:
        todo_list.title = update_data.title
    if update_data.description is not None:
        todo_list.description = update_data.description

    db.commit()
    db.refresh(todo_list)

    return todo_list

def delete_todo_list(db: Session, todo_list_id: int):
    """Todoリストを削除するAPI"""

    # 指定されたtodo_list_idのリストを取得
    todo_list = db.get(ListModel, todo_list_id)
    if todo_list is None:
        return

    db.delete(todo_list)
    db.commit()

    return {}

def get_todo_lists(db: Session, page: int, per_page: int):
    """Todoリスト一覧を取得するAPI"""

    page = max(page, 1) # 1未満の場合は1に
    offset = (page - 1) * per_page

    stmt = select(ListModel).offset(offset).limit(per_page)
    result = db.execute(stmt)
    return result.scalars().all()