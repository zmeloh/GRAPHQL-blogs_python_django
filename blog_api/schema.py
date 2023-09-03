import graphene
import blog_api.articles.schema as articles_schema
import blog_api.comments.schema as comments_schema
import blog_api.users.schema as users_schema

class Query(
    articles_schema.Query,
    comments_schema.Query,
    users_schema.Query,
    graphene.ObjectType
):
    pass

schema = graphene.Schema(query=Query)
