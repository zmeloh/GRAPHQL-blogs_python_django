from django.db import models
from django.contrib.auth.models import User  # Importez le modèle User

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    pub_date = models.DateTimeField('date published')
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # Lien vers l'utilisateur

    def __str__(self):
        return self.title

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # Lien vers l'utilisateur
    text = models.TextField()
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.text