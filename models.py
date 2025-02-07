from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import JSON
from typing import Optional

db = SQLAlchemy()

# Association table (Many-to-Many)
# user_roles = db.Table(
#     "user_roles", db.Column("user_id", db.Integer, db.ForeignKey("users.id")), db.Column("role_id", db.Integer, db.ForeignKey("roles.id"))
# )

# role_permissions = db.Table(
#     "role_permissions",
#     db.Column("role_id", db.Integer, db.ForeignKey("roles.id")),
#     db.Column("permission_id", db.Integer, db.ForeignKey("permissions.id")),
# )


class User(db.Model):
    __tablename__: str = "users"
    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username: str = db.Column(db.String(50), unique=True, nullable=False)
    password: str = db.Column(db.String(50), nullable=False)
    role_id: int = db.Column(db.Integer, db.ForeignKey("roles.id"))

    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password

        staff_role: Optional[Role] = Role.query.filter_by(name="staff").first()

        # print(staff_role)

        if not staff_role:
            raise ValueError("Default role 'staff' not found. Make sure roles are pre-seeded.")

        self.role_id = staff_role.id


class Role(db.Model):
    __tablename__ = "roles"
    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name: str = db.Column(db.String(50), unique=True, nullable=False)
    perm_id: list[int] = db.Column(JSON, nullable=False, default=list)

    def __init__(self, name: str) -> None:
        self.name = name


class Permission(db.Model):
    __tablename__ = "permissions"
    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    action: str = db.Column(db.String(50), nullable=False)
    resource: str = db.Column(db.String(50), nullable=False)

    def __init__(self, action: str, resource: str) -> None:
        self.action = action
        self.resource = resource


def pre_populate_roles():
    roles = ["staff", "supervisor", "admin"]

    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name)
            db.session.add(role)

    db.session.commit()
