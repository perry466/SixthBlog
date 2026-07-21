from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='分类名称')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='分类标识')
    description = models.TextField(blank=True, default='', verbose_name='分类描述')
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='children', verbose_name='父分类'
    )
    order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def article_count(self):
        return self.articles.filter(status='published').count()


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='标签名')
    slug = models.CharField(max_length=50, unique=True, verbose_name='标签标识')

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'

    def __str__(self):
        return self.name


class Article(models.Model):
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
        ('archived', '已归档'),
    ]
    ARTICLE_TYPE_CHOICES = [
        ('article', '文章'),
        ('diary', '日记'),
        ('about', '关于'),
    ]

    title = models.CharField(max_length=200, verbose_name='标题')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='文章标识')
    content = models.TextField(verbose_name='正文内容(Markdown)')
    summary = models.TextField(blank=True, default='', verbose_name='文章摘要')
    cover_image = models.ImageField(
        upload_to='articles/covers/', blank=True, null=True, verbose_name='封面图片'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='articles', verbose_name='作者'
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True,
        related_name='articles', verbose_name='分类'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles', verbose_name='标签')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='published', verbose_name='状态'
    )
    article_type = models.CharField(
        max_length=20, choices=ARTICLE_TYPE_CHOICES, default='article', verbose_name='文章类型'
    )
    view_count = models.IntegerField(default=0, verbose_name='阅读量')
    word_count = models.IntegerField(default=0, verbose_name='字数')
    seo_title = models.CharField(max_length=200, blank=True, default='', verbose_name='SEO标题')
    seo_description = models.TextField(blank=True, default='', verbose_name='SEO描述')
    is_featured = models.BooleanField(default=False, verbose_name='是否置顶')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='发布时间')

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ['-is_featured', '-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.content:
            import re
            plain_text = re.sub(r'[#*`\[\]()!>_\-]', '', self.content)
            self.word_count = len(plain_text)
            if not self.summary:
                self.summary = plain_text[:200]
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class Comment(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='comments', verbose_name='文章'
    )
    nickname = models.CharField(max_length=50, verbose_name='昵称')
    email = models.EmailField(verbose_name='邮箱')
    content = models.TextField(verbose_name='评论内容')
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE,
        related_name='replies', verbose_name='父评论'
    )
    is_approved = models.BooleanField(default=True, verbose_name='是否通过')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.nickname}: {self.content[:30]}'


class SiteConfig(models.Model):
    site_title = models.CharField(max_length=200, default='My Blog', verbose_name='网站标题')
    site_description = models.TextField(blank=True, default='', verbose_name='网站描述')
    site_logo = models.ImageField(
        upload_to='site/', blank=True, null=True, verbose_name='网站Logo'
    )
    site_favicon = models.ImageField(
        upload_to='site/', blank=True, null=True, verbose_name='网站图标'
    )
    blog_background = models.ImageField(
        upload_to='site/', blank=True, null=True, verbose_name='博客背景图'
    )
    about_content = models.TextField(blank=True, default='', verbose_name='关于页面内容')
    social_links = models.JSONField(default=dict, blank=True, verbose_name='社交账号链接')
    welcome_messages = models.JSONField(
        default=list, blank=True, verbose_name='随机问候语列表'
    )
    splash_animation_text = models.CharField(
        max_length=200, blank=True, default='', verbose_name='开屏动画文字'
    )
    splash_animation_bg = models.CharField(
        max_length=50, blank=True, default='#1a1a2e', verbose_name='开屏动画背景色'
    )
    splash_animation_theme = models.CharField(
        max_length=50, blank=True, default='default', verbose_name='开屏动画主题'
    )
    articles_per_page = models.IntegerField(default=10, verbose_name='每页文章数')
    show_article_stats = models.BooleanField(default=True, verbose_name='展示文章统计信息')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '站点配置'
        verbose_name_plural = '站点配置'

    def __str__(self):
        return self.site_title


class MenuItem(models.Model):
    name = models.CharField(max_length=100, verbose_name='菜单名称')
    url = models.CharField(max_length=200, blank=True, default='', verbose_name='菜单链接/路由')
    icon = models.CharField(max_length=50, blank=True, default='', verbose_name='菜单图标')
    order = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE,
        related_name='children', verbose_name='父菜单'
    )

    class Meta:
        verbose_name = '菜单项'
        verbose_name_plural = '菜单项'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Media(models.Model):
    """媒体库：记录所有上传的图片文件"""
    file = models.ImageField(upload_to='media/%Y/%m/', verbose_name='文件')
    filename = models.CharField(max_length=255, verbose_name='原始文件名')
    file_size = models.IntegerField(default=0, verbose_name='文件大小(字节)')
    mime_type = models.CharField(max_length=50, default='', verbose_name='MIME类型')
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='uploads',
        verbose_name='上传者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '媒体文件'
        verbose_name_plural = '媒体文件'
        ordering = ['-created_at']

    def __str__(self):
        return self.filename

    @property
    def file_url(self):
        """返回文件完整访问 URL"""
        try:
            return self.file.url
        except Exception:
            return ''


class Guestbook(models.Model):
    nickname = models.CharField(max_length=50, verbose_name='昵称')
    email = models.EmailField(verbose_name='邮箱')
    content = models.TextField(verbose_name='留言内容')
    is_approved = models.BooleanField(default=False, verbose_name='是否通过')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '留言板'
        verbose_name_plural = '留言板'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.nickname}: {self.content[:30]}'
