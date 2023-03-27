from django.db import models
from datetime import datetime
from news_portal.resources import CHOICES, news, article
from django.contrib.auth.models import User
from django.db.models import Sum


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    user_rating = models.IntegerField(default=0)

    def update_rating(self):
        articles = Post.objects.filter(author=self)
        articles_rating = articles.aggregate(Sum('post_rating')).get('post_rating__sum')
        comments = Comment.objects.filter(user=self.user)
        comments_rating = comments.aggregate(Sum('comment_rating')).get('comment_rating__sum')
        comments_to_author = Comment.objects.filter(user_id=self.user)
        to_author_rating = comments_to_author.aggregate(Sum('comment_rating'))['comment_rating__sum']
        total_rating = articles_rating * 3 + comments_rating + to_author_rating
        self.user_rating = total_rating
        self.save()

    # def update_rating(self):
    #     articles = Post.objects.filter(author=self)
    #     articles_rating_sum = articles.aggregate(Sum('post_rating'))['post_rating'] * 3
    #     comments = Comment.objects.filter(user=self.user)
    #     comments_rating_sum = comments.aggregate(Sum('comment_rating'))['comment_rating']
    #     comments_author = Comment.objects.filter(post_id=self.id)
    #     to_author_rating = comments_author.aggregate(Sum('comment_rating'))['comment_rating']
    #     total_rating = articles_rating_sum + comments_rating_sum + to_author_rating
    #     self.user_rating = total_rating
    #     self.save()


class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)

class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    selection_field = models.CharField(max_length=10, choices=CHOICES, default=news)
    time_in = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through="PostCategory")
    header_field = models.CharField(max_length=255)
    text_field = models.TextField()
    post_rating = models.IntegerField(default=0)

    def like(self):
        self.post_rating += 1
        self.save()

    def dislike(self):
        self.post_rating -= 1
        self.save()

    def preview(self):
        if len(self.text_field) > 124:
            return self.text_field[:124] + "..."
        else:
            return self.text_field


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.TextField(default="comment")
    time_in = models.DateTimeField(auto_now_add=True)
    comment_rating = models.IntegerField(default=0)

    def like(self):
        self.comment_rating += 1
        self.save()

    def dislike(self):
        self.comment_rating -= 1
        self.save()