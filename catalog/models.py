from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class Book(models.Model):
    category = models.ForeignKey(
        Category,
        related_name='books',
        on_delete=models.CASCADE
    )
    number = models.PositiveSmallIntegerField(default=0)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.number} - {self.title} | #{self.category.name}'


class Chapter(models.Model):
    book = models.ForeignKey(
        Book,
        related_name='chapters',
        on_delete=models.CASCADE
    )
    number = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    content = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.number} - {self.title} | #{self.book.title}'