from app.extensions import db

class BaseRepository:
    def __init__(self,model):
        self.model = model

    def get_by_id(self,id):
        return db.session.get(self.model, id)

    def get_all(self):
        return db.session.execute(db.select(self.model)).scalars().all()

    def create(self, entidade):
        db.session.add(entidade)
        db.session.commit()
        return entidade

    def update(self, entidade):
        db.session.commit()
        return entidade

    def delete(self, entidade):
        db.session.delete(entidade)
        db.session.commit()
