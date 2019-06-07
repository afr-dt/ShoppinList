import graphene
from models import Purchase, User
from graphql import GraphQLError
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from db import db


def require_auth(method):
    def wrapper(self, *args, **kwargs):
        auth_resp = User.decode_auth_token(args[0].context)
        if not isinstance(auth_resp, str):
            kwargs['user'] = User.query.filter_by(id=auth_resp).first()
            return method(self, *args, **kwargs)
        raise GraphQLError(auth_resp)
    return wrapper


class PurchaseObject(SQLAlchemyObjectType):
    class Meta:
        model = Purchase
        interfaces = (graphene.relay.Node, )


class UserObject(SQLAlchemyObjectType):
    class Meta:
        model = User
        interfaces = (graphene.relay.Node, )
        exclude_fields = ('password_hash')


class Viewer(graphene.ObjectType):
    class Meta:
        interfaces = (graphene.relay.Node, )

    all_purchases = SQLAlchemyConnectionField(PurchaseObject)
    all_users = SQLAlchemyConnectionField(UserObject)


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    viewer = graphene.Field(Viewer)

    @staticmethod
    def resolve_viewer(root, info):
        auth_resp = User.decode_auth_token(info.context)
        if not isinstance(auth_resp, str):
            return Viewer()
        raise GraphQLError(auth_resp)


class SignUp(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
    user = graphene.Field(lambda: UserObject)
    auth_token = graphene.String()

    def mutate(self, info, **kwargs):
        user = User(email=kwargs.get('email'))
        user.set_password(kwargs.get('password'))
        db.session.add(user)
        db.session.commit()
        return SignUp(user=user, auth_token=user.encode_auth_token(user.id).decode())


class Login(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
    user = graphene.Field(lambda: UserObject)
    auth_token = graphene.String()

    def mutate(self, info, **kwargs):
        user = User.query.filter_by(email=kwargs.get('email')).first()
        if user is None or not user.check_password(kwargs.get('password')):
            raise GraphQLError("Invalid Credentials")
        return Login(user=user, auth_token=user.encode_auth_token(user.id).decode())


class CreatePurchase(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        tags = graphene.String()
        is_done = graphene.Boolean()
        user_id = graphene.Int()
    purchase = graphene.Field(lambda: PurchaseObject)

    @require_auth
    def mutate(self, info, **kwargs):
        user = User.query.filter_by(id=kwargs.get('user_id')).first()
        purchase = Purchase(name=kwargs.get('name'), tags=kwargs.get(
            'tags'), is_done=kwargs('is_done'))
        if user is not None:
            purchase.user = user
        db.session.add(purchase)
        db.session.commit()
        return CreatePurchase(purchase=purchase)


class UpdatePurchase(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        tags = graphene.String()
        is_done = graphene.Boolean()
        user_id = graphene.Int()
    purchase = graphene.Field(lambda: PurchaseObject)

    @require_auth
    def mutate(self, info, **kwargs):
        purchase = Purchase.query.filter_by(id=kwargs.get('id')).first()
        user = User.query.filter_by(id=purchase.user.id).first()
        if kwargs.get('user') != user:
            raise GraphQLError("No tienes permisos para modificar!!!")
        else:
            purchase.name = kwargs.get('name')
            purchase.tags = kwargs.get('tags')
            purchase.is_done = kwargs.get('is_done')
            return UpdatePurchase(purchase=purchase)


class DeletePurchase(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
    status = graphene.Boolean()

    @require_auth
    def mutate(self, info, **kwargs):
        purchase = Purchase.query.filter_by(id=kwargs.get(id)).first()
        user = User.query.filter_by(id=user.user.id).first()
        if kwargs.get('user') != user:
            raise GraphQLError("No tienes permisos para eliminar!!!")
        else:
            db.session.delete(purchase)
            db.session.commit()
            return DeletePurchase(status=status)


class Mutation(graphene.ObjectType):
    signup = SignUp.Field()
    login = Login.Field()
    create_purchase = CreatePurchase.Field()
    update_purchase = UpdatePurchase.Field()
    delete_purchase = DeletePurchase.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
