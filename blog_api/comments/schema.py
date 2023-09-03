import graphene
from graphene_django.types import DjangoObjectType
from graphene import InputObjectType
from ..models import Comment
from django.core.exceptions import ObjectDoesNotExist
from graphql import GraphQLError
from django.contrib.auth.models import User
from graphql_jwt.decorators import login_required

class CommentType(DjangoObjectType):
    class Meta:
        model = Comment

# Input type for creating or updating a comment
class CommentInput(InputObjectType):
    text = graphene.String()

class CreateComment(graphene.Mutation):
    class Arguments:
        input = CommentInput(required=True)
        article_id = graphene.Int(required=True)

    comment = graphene.Field(CommentType)

    @login_required
    def mutate(self, info, input, article_id):
        user = info.context.user
        try:
            article = user.article_set.get(pk=article_id)
        except ObjectDoesNotExist:
            raise GraphQLError("Article not found or you don't have permission to add comments to it.")
        comment = Comment(
            text=input.text,
            article=article,
            author=user
        )
        comment.save()
        return CreateComment(comment=comment)

class UpdateComment(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = CommentInput(required=True)

    comment = graphene.Field(CommentType)

    @login_required
    def mutate(self, info, id, input):
        user = info.context.user
        try:
            comment = Comment.objects.get(pk=id, author=user)
        except ObjectDoesNotExist:
            raise GraphQLError("Comment not found or you don't have permission to update it.")
        comment.text = input.text
        comment.save()
        return UpdateComment(comment=comment)

class DeleteComment(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info, id):
        user = info.context.user
        try:
            comment = Comment.objects.get(pk=id, author=user)
        except ObjectDoesNotExist:
            raise GraphQLError("Comment not found or you don't have permission to delete it.")
        comment.delete()
        return DeleteComment(success=True)

class Query(graphene.ObjectType):
    all_comments = graphene.List(CommentType)
    comment_by_id = graphene.Field(CommentType, id=graphene.Int())

    def resolve_all_comments(self, info):
        return Comment.objects.all()
    
    def resolve_comemnt_by_id(self, info, id):
        try:
            return Comment.objects.get(pk=id)
        except ObjectDoesNotExist:
            return None

class Mutation(graphene.ObjectType):
    create_comment = CreateComment.Field()
    update_comment = UpdateComment.Field()
    delete_comment = DeleteComment.Field()
