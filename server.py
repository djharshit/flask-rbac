from flask import Flask, request
from flask_restx import Api, Resource
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
from os import environ

from models import db, User, Role, Permission, pre_populate_roles
from logs import mylogger, get_logs

if "MYSQL_URI" not in environ:
    raise ValueError("MYSQL_URI not found in environment variables")


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = environ["MYSQL_URI"]
app.config["JWT_SECRET_KEY"] = environ["JWT_SECRET"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)


api = Api(app)
db.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()
    pre_populate_roles()


# Health Check API
@api.route("/health")
class HealthAPI(Resource):
    def get(self):
        return {"success": "true", "message": "Healthy"}, 200


# Login Management API
@api.route("/login")
class LoginAPI(Resource):
    def post(self):
        data: dict[str, str] = request.get_json()
        user: User = User.query.filter_by(username=data["username"]).first()  # type: ignore

        if not user or user.password != data["password"]:
            mylogger.info(f"[Denied] User {data['username']} login failed")
            return {"success": "false", "message": "Invalid credentials"}, 401

        access_token = create_access_token(identity=str(user.id))

        mylogger.info(f"[Granted] User {data['username']} logged in successfully")
        return {"success": "true", "access_token": access_token}, 200


# User API
@api.route("/users")
class UserAPI(Resource):
    def get(self):  # type: ignore
        users: list[User] = User.query.all()
        return {"success": "true", "data": [{"id": u.id, "username": u.username} for u in users]}

    def post(self):
        try:
            data: dict[str, str] = request.get_json()
            print(data)
            user = User(username=data["username"], password=data["password"])

            db.session.add(user)
            db.session.commit()

            mylogger.info(f"[Granted] User {data['username']} created successfully")
            return {"success": "true", "message": "User created"}, 201

        except KeyError:
            return {"success": "false", "message": "Username not provided"}, 400

        except IntegrityError:
            return {"success": "false", "message": "User already exists"}, 409


# Role Management API
@api.route("/roles")
class RoleAPI(Resource):
    def get(self):  # type: ignore
        roles = Role.query.all()
        return {"success": "true", "data": [{"id": r.id, "name": r.name} for r in roles]}

    @jwt_required()
    def post(self):
        try:
            data: dict[str, str] = request.get_json()
            role: Role = Role(name=data["role"])

            # print(role)

            db.session.add(role)
            db.session.commit()

            mylogger.info(f"[Granted] Role {data['role']} created successfully [Access] user {get_jwt_identity()}")
            return {"success": "true", "message": "Role created"}, 201

        except KeyError:
            mylogger.info(f"[Denied] Role creation failed. Role name not provided [Access] user {get_jwt_identity()}")
            return {"success": "false", "message": "Role name not provided"}, 400

        except IntegrityError:
            mylogger.info(f"[Denied] Role creation failed. Role already exists [Access] user {get_jwt_identity()}")
            return {"success": "false", "message": "Role already exists"}, 409


@api.route("/role/<int:roleid>")
class RolePermissionAPI(Resource):
    @jwt_required()
    def get(self, roleid: int): # type: ignore
        curr_user = get_jwt_identity()
        curr_user: User = User.query.filter_by(id=curr_user).first()  # type: ignore
        curr_role: Role = Role.query.filter_by(id=curr_user.role_id).first()  # type: ignore

        if curr_role.id == 1:
            mylogger.info(f"[Denied] Access denied to view permissions [Access] user {get_jwt_identity()}")
            return {"success": "false", "message": "Access denied"}, 403

        role: Role = Role.query.filter_by(id=roleid).first()  # type: ignore
        if not role:
            mylogger.info(f"[Denied] Role not found [Access] user {get_jwt_identity()}")
            return {"success": "false", "message": "Role not found"}, 404

        perms: list[Permission] = Permission.query.filter(Permission.id.in_(role.perm_id)).all()

        mylogger.info(f"[Granted] Permissions viewed for role {role.id} [Access] user {get_jwt_identity()}")
        return {"success": "true", "data": [{"id": p.id, "action": p.action, "resource": p.resource} for p in perms]}


# Permission Management API
@api.route("/permissions")
class PermissionAPI(Resource):
    @jwt_required()
    def get(self):  # type: ignore

        curr_user = get_jwt_identity()
        curr_user: User = User.query.filter_by(id=curr_user).first()  # type: ignore
        curr_role: Role = Role.query.filter_by(id=curr_user.role_id).first()  # type: ignore

        if curr_role.id == 1:
            mylogger.info(f"[Denied] Access denied to view permissions [Access] user {get_jwt_identity()}")
            return {"success": "false", "message": "Access denied"}, 403

        perms = Permission.query.all()

        mylogger.info(f"[Granted] Permissions viewed [Access] user {get_jwt_identity()}")
        return {"success": "true", "data": [{"id": p.id, "action": p.action, "resource": p.resource} for p in perms]}

    @jwt_required()
    def post(self):
        data: dict[str, str] = request.get_json()
        print(data)

        perm = Permission(action=data["action"], resource=data["resource"])
        db.session.add(perm)
        db.session.commit()

        mylogger.info(f"[Granted] Permission {perm.id} created [Access] user {get_jwt_identity()}")
        return {"success": "true", "message": "Permission created"}, 201


@api.route("/assignrole")
class AssignRoleAPI(Resource):
    @jwt_required()
    def post(self):
        data: dict[str, str] = request.get_json()
        # print(data)
        userid: User = User.query.filter_by(id=data["userid"]).first()  # type: ignore
        roleid: Role = Role.query.filter_by(id=data["roleid"]).first()  # type: ignore

        current_user = get_jwt_identity()

        # Get the current user and his roleid
        curr_user: User = User.query.filter_by(id=current_user).first()  # type: ignore
        curr_role: Role = Role.query.filter_by(id=curr_user.role_id).first()  # type: ignore

        # print(curr_user, curr_role)

        if curr_role.id == 1:
            mylogger.info(f"[Denied] Access denied to assign role {roleid.id} for user {userid.id}[Access] user {get_jwt_identity()}")
            return {"success": "false", "message": "Access denied"}, 403

        if not userid or not roleid:

            mylogger.info(f"[Denied] User or Role not found [Access] user {get_jwt_identity()}")
            return {"success": "false", "message": "User or Role not found"}, 404

        userid.role_id = roleid.id
        db.session.commit()

        mylogger.info(f"[Granted] Role {roleid.id} assigned for user {userid.id} [Access] user {get_jwt_identity()}")
        return {"success": "true", "message": "Role assigned"}, 200


@api.route("/assignperm")
class AssignPermAPI(Resource):
    @jwt_required()
    def post(self):
        try:
            data: dict[str, str] = request.get_json()
            # print(data)

            roleid: Role = Role.query.filter_by(id=data["roleid"]).first()  # type: ignore
            permid: Permission = Permission.query.filter_by(id=data["permid"]).first()  # type: ignore

            current_user = get_jwt_identity()

            # Get the current user and his roleid
            curr_user: User = User.query.filter_by(id=current_user).first()  # type: ignore
            curr_role: Role = Role.query.filter_by(id=curr_user.role_id).first()  # type: ignore

            # print(curr_user, curr_role)

            if curr_role.id != 3:

                mylogger.info(f"[Denied] Access denied to assign permission {permid.id} for role {roleid.id} [Access] user {get_jwt_identity()}")
                return {"success": "false", "message": "Access denied"}, 403

            if not roleid or not permid:

                mylogger.info(f"[Denied] Role or Permission not found [Access] user {get_jwt_identity()}")
                return {"success": "false", "message": "Role or Permission not found"}, 404

            if permid.id in roleid.perm_id:
                mylogger.info(f"[Denied] Permission {permid.id} already assigned for role {roleid.id} [Access] user {get_jwt_identity()}")
                return {"success": "false", "message": "Permission already assigned"}, 409

            roleid.perm_id = roleid.perm_id + [permid.id]

            db.session.commit()

            mylogger.info(f"[Granted] Permission {permid.id} assigned for role {roleid.id} [Access] user {get_jwt_identity()}")
            return {"success": "true", "message": "Permission assigned"}, 200

        except KeyError:
            mylogger.info(f"[Denied] Role or Permission not found [Access] user {get_jwt_identity()}")
            return {"success": "false", "message": "Role or Permission not found"}, 404


@api.route("/validate")
class ValidateAccessAPI(Resource):
    @jwt_required()
    def post(self): # type: ignore
        data: dict[str, str] = request.get_json()
        user: User = User.query.filter_by(id=data["user_id"]).first()  # type: ignore
        if not user:
            mylogger.info(f"[Denied] User not found [Access] user {get_jwt_identity()}")
            return {"success": "false", "message": "User not found"}, 404

        for perm in user.role_id.perm_id:
            if perm.action == data["action"] and perm.resource == data["resource"]:

                mylogger.info(f"[Granted] Access granted [Access] user {get_jwt_identity()}")
                return {"success": "true", "message": "Access granted"}, 200

        mylogger.info(f"[Denied] Access denied [Access] user {get_jwt_identity()}")
        return {"success": "false", "message": "Access denied"}, 403


# Logs API - Retrievve logs for past N hours by admin
@api.route("/logs/<int:hours>")
class LogsAPI(Resource):
    @jwt_required()
    def get(self, hours: int):  # type: ignore
        current_user = get_jwt_identity()
        curr_user: User = User.query.filter_by(id=current_user).first()  # type: ignore
        curr_role: Role = Role.query.filter_by(id=curr_user.role_id).first()  # type: ignore

        if curr_role.id != 3:
            mylogger.info(f"[Denied] Access denied to view logs [Access] user {get_jwt_identity()}")
            return {"success": "false", "message": "Access denied"}, 403

        logs = get_logs(hours)
        return {"success": "true", "data": logs}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
