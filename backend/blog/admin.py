from django.contrib import admin
from .models import Category, Tag, Article, Comment, SiteConfig, MenuItem, Guestbook


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'order', 'article_count']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class TagInline(admin.TabularInline):
    model = Article.tags.through
    extra = 1


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'article_type', 'view_count', 'word_count', 'is_featured', 'created_at']
    list_filter = ['status', 'article_type', 'category', 'is_featured', 'tags']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [TagInline]
    readonly_fields = ['view_count', 'word_count', 'created_at', 'updated_at']
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'slug', 'content', 'summary', 'cover_image', 'author', 'category', 'tags')
        }),
        ('状态设置', {
            'fields': ('status', 'article_type', 'is_featured')
        }),
        ('SEO设置', {
            'fields': ('seo_title', 'seo_description'),
            'classes': ('collapse',)
        }),
        ('统计信息', {
            'fields': ('view_count', 'word_count', 'created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['nickname', 'article', 'is_approved', 'created_at']
    list_filter = ['is_approved']
    search_fields = ['nickname', 'content']


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ['site_title', 'articles_per_page', 'show_article_stats']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'order', 'is_active', 'parent']
    list_editable = ['order', 'is_active']


@admin.register(Guestbook)
class GuestbookAdmin(admin.ModelAdmin):
    list_display = ['nickname', 'email', 'is_approved', 'created_at']
    list_filter = ['is_approved']
