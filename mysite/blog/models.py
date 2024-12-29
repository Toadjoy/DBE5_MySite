from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)

# Create your models here.
class Post(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title=models.CharField(max_length=250)
    slug=models.SlugField(
        max_length=250,
        unique_for_date='publish'
        )
    author=models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts' #Identifys the reverse relationship. Allows you to easily reference the Posts of a User via "user.blog_posts"
    )
    body=models.TextField()
    publish=models.DateTimeField(default=timezone.now)
    created=models.DateTimeField(auto_now_add=True) #Sets the time automatically when the object is created
    updated=models.DateTimeField(auto_now=True) #Sets the time everytime the object is saved
    status=models.CharField(
        max_length=2,
        choices=Status,
        default=Status.DRAFT
    )
    """
    managers are used for retrieving objects in the database .1st manager declared 
    becomes default manager (so if published was 1st it would be default). Using 
    "default_manage_name" in Meta can override this and specify a default.
    """
    objects = models.Manager() #default manager
    published = PublishedManager() #Custome published manager


    class Meta:
        ordering =['-publish'] #hyphen indicates sort in descending order
        indexes = [
            models.Index(fields=['-publish'])
        ]

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("blog:post_detail",
                        args=[self.publish.year,
                              self.publish.month,
                              self.publish.day,
                              self.slug])
    

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=100)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created']),
        ]
        
    def __str__(self):
        return f'Comment by {self.name} on {self.post}'
