import graphene
from graphene_django.types import DjangoObjectType
from graphql import GraphQLError
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from graphql_jwt.decorators import login_required
from django.db import IntegrityError

class UserType(DjangoObjectType):
    class Meta:
        model = User

class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserType)

    def mutate(self, info, username, password):
        try:
            user = User(username=username)
            user.set_password(password)
            user.save()
            return CreateUser(user=user)
        except IntegrityError:
            raise GraphQLError("Username already exists.")

class UpdateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        new_password = graphene.String(required=True)

    user = graphene.Field(UserType)

    @login_required
    def mutate(self, info, username, password, new_password):
        user = info.context.user
        if user.username == username and user.check_password(password):
            user.set_password(new_password)
            user.save()
            return UpdateUser(user=user)
        else:
            raise GraphQLError("Invalid username or password.")

class DeleteUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info, username, password):
        user = info.context.user
        if user.username == username and user.check_password(password):
            user.delete()
            return DeleteUser(success=True)
        else:
            raise GraphQLError("Invalid username or password.")

class Query(graphene.ObjectType):
    all_users = graphene.List(UserType)
    user_by_id = graphene.Field(UserType, id=graphene.Int())
    @login_required
    def resolve_all_users(self, info):
        return User.objects.all()
    
    @login_required
    def resolve_user_by_id(self, info, id):
        try:
            return User.objects.get(pk=id)
        except ObjectDoesNotExist:
            return None
class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()
