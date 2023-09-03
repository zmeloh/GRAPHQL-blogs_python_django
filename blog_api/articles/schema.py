import graphene
from graphene_django.types import DjangoObjectType
from graphene import InputObjectType
from ..models import Article
from django.core.exceptions import ObjectDoesNotExist
from graphql import GraphQLError
from django.contrib.auth.models import User
from graphql_jwt.decorators import login_required

class ArticleType(DjangoObjectType):
    class Meta:
        model = Article

# Input type for creating or updating an article
class ArticleInput(InputObjectType):
    title = graphene.String()
    content = graphene.String()

class CreateArticle(graphene.Mutation):
    class Arguments:
        input = ArticleInput(required=True)

    article = graphene.Field(ArticleType)

    @login_required
    def mutate(self, info, input):
        user = info.context.user
        article = Article(
            title=input.title,
            content=input.content,
            author=user
        )
        article.save()
        return CreateArticle(article=article)

class UpdateArticle(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ArticleInput(required=True)

    article = graphene.Field(ArticleType)

    @login_required
    def mutate(self, info, id, input):
        user = info.context.user
        try:
            article = Article.objects.get(pk=id, author=user)
        except ObjectDoesNotExist:
            raise GraphQLError("Article not found or you don't have permission to update it.")
        article.title = input.title
        article.content = input.content
        article.save()
        return UpdateArticle(article=article)

class DeleteArticle(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info, id):
        user = info.context.user
        try:
            article = Article.objects.get(pk=id, author=user)
        except ObjectDoesNotExist:
            raise GraphQLError("Article not found or you don't have permission to delete it.")
        article.delete()
        return DeleteArticle(success=True)

class Query(graphene.ObjectType):
    all_articles = graphene.List(ArticleType)
    article_by_id = graphene.Field(ArticleType, id=graphene.Int())

    def resolve_all_articles(self, info):
        return Article.objects.all()

    def resolve_article_by_id(self, info, id):
        try:
            return Article.objects.get(pk=id)
        except ObjectDoesNotExist:
            return None

class Mutation(graphene.ObjectType):
    create_article = CreateArticle.Field()
    update_article = UpdateArticle.Field()
    delete_article = DeleteArticle.Field()
