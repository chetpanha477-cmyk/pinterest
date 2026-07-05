from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

CATEGORY_CHOICES = [
    ("Home decor", "Home decor"),
    ("Travel", "Travel"),
    ("Recipes", "Recipes"),
    ("Fashion", "Fashion"),
    ("Art", "Art"),
    ("Fitness", "Fitness"),
    ("Beauty", "Beauty"),
    ("DIY & Crafts", "DIY & Crafts"),
    ("Photography", "Photography"),
    ("Gardening", "Gardening"),
    ("Technology", "Technology"),
    ("Wedding", "Wedding"),
    ("Animals", "Animals"),
    ("Quotes", "Quotes"),
    ("Design", "Design"),
]


class Board(models.Model):
    """A collection that a user can save pins into (like Pinterest 'boards')."""
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boards')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('name', 'owner')

    def __str__(self):
        return f"{self.name} ({self.owner.username})"

    def get_absolute_url(self):
        return reverse('board_detail', args=[self.pk])


class Pin(models.Model):
    """A single pinned image, similar to a Pinterest 'Pin'."""
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='pins/')
    link = models.URLField(blank=True, help_text="Optional source link")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="Home decor")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pins')
    board = models.ForeignKey(
        Board, on_delete=models.SET_NULL, null=True, blank=True, related_name='pins'
    )
    saved_by = models.ManyToManyField(User, related_name='saved_pins', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('pin_detail', args=[self.pk])

    @property
    def save_count(self):
        return self.saved_by.count()


class Comment(models.Model):
    pin = models.ForeignKey(Pin, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author.username}: {self.text[:30]}"
