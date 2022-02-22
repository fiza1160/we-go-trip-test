from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])
    text = models.TextField(blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.author} ({self.created}): {self.text}'

    def __repr__(self):
        return f'(author: {self.author} rating: {self.rating} created: {self.created} ' \
               f'text: {self.text} is_published: {self.is_published})'
