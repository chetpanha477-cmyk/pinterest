from django.contrib import admin
from .models import Board, Pin, Comment


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    search_fields = ('name',)


@admin.register(Pin)
class PinAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'owner', 'board', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('category', 'board', 'owner')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pin', 'author', 'created_at')
