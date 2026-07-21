from rest_framework import serializers
from django.utils.text import slugify
from .models import Category, Tag, Article, Comment, SiteConfig, MenuItem, Guestbook, Media


class CategorySerializer(serializers.ModelSerializer):
    article_count = serializers.IntegerField(read_only=True, default=0)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'order', 'article_count', 'children']

    def get_children(self, obj):
        children = obj.children.all()
        return CategorySerializer(children, many=True).data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    article_title = serializers.CharField(source='article.title', read_only=True, default='')

    class Meta:
        model = Comment
        fields = ['id', 'article', 'article_title', 'nickname', 'email', 'content', 'parent', 'is_approved', 'replies', 'created_at']

    def get_replies(self, obj):
        replies = obj.replies.filter(is_approved=True)
        return CommentSerializer(replies, many=True).data


class ArticleListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, default='')
    tags = TagSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'summary', 'cover_image',
            'category', 'category_name', 'tags',
            'view_count', 'word_count', 'status', 'article_type',
            'is_featured', 'created_at', 'updated_at', 'published_at',
            'comment_count',
        ]

    def get_comment_count(self, obj):
        return obj.comments.filter(is_approved=True).count()


class ArticleDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, default='')
    tags = TagSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    author_name = serializers.CharField(source='author.username', read_only=True)
    table_of_contents = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'content', 'summary', 'cover_image',
            'category', 'category_name', 'tags',
            'view_count', 'word_count', 'status', 'article_type',
            'is_featured', 'created_at', 'updated_at', 'published_at',
            'seo_title', 'seo_description',
            'author_name', 'comments', 'table_of_contents',
        ]

    def get_comments(self, obj):
        comments = obj.comments.filter(is_approved=True, parent__isnull=True)
        return CommentSerializer(comments, many=True).data

    def get_table_of_contents(self, obj):
        import re
        headings = re.findall(r'^(#{1,6})\s+(.+)$', obj.content, re.MULTILINE)
        toc = []
        for level, text in headings:
            toc.append({
                'level': len(level),
                'text': text.strip(),
                'id': text.strip().lower().replace(' ', '-').replace('#', ''),
            })
        return toc


class TagListField(serializers.Field):
    """标签字段：写入时自动创建不存在的标签，读取时返回标签名列表"""

    def to_representation(self, value):
        # value 是 article.tags (ManyRelatedManager)，Django 5.0+ 必须显式 .all()
        return [tag.name for tag in value.all()]

    def to_internal_value(self, data):
        tags = []
        for name in data:
            name = name.strip()
            if not name:
                continue
            slug = slugify(name, allow_unicode=True)
            if not slug:
                slug = name
            # 用 name 查找（name 也是 unique），避免旧数据空 slug 导致的冲突
            tag, created = Tag.objects.get_or_create(
                name=name,
                defaults={'slug': slug}
            )
            # 修复旧数据中 slug 为空的情况
            if not created and not tag.slug:
                tag.slug = slug
                tag.save(update_fields=['slug'])
            tags.append(tag)
        return tags


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    tags = TagListField(required=False, default=list)
    slug = serializers.SlugField(required=False, allow_blank=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'content', 'summary', 'cover_image',
            'category', 'tags', 'status', 'article_type',
            'seo_title', 'seo_description', 'is_featured',
        ]
        extra_kwargs = {
            'status': {'default': 'published'},
        }

    def _generate_unique_slug(self, title, instance=None):
        """根据标题生成唯一 slug"""
        base_slug = slugify(title) or 'article'
        slug = base_slug
        counter = 1
        qs = Article.objects.all()
        if instance:
            qs = qs.exclude(pk=instance.pk)
        while qs.filter(slug=slug).exists():
            slug = f'{base_slug}-{counter}'
            counter += 1
        return slug

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        if not validated_data.get('slug'):
            validated_data['slug'] = self._generate_unique_slug(validated_data.get('title', ''))
        article = Article.objects.create(**validated_data)
        article.tags.set(tags)
        return article

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if not validated_data.get('slug') and 'title' in validated_data:
            validated_data['slug'] = self._generate_unique_slug(validated_data['title'], instance=instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['article', 'nickname', 'email', 'content', 'parent']


class ImagePathField(serializers.ImageField):
    """接受文件上传或文本路径（用于站点设置中手动填写图片路径）"""
    def to_internal_value(self, data):
        if isinstance(data, str):
            return data
        return super().to_internal_value(data)


class SiteConfigSerializer(serializers.ModelSerializer):
    site_logo = ImagePathField(required=False, allow_null=True)
    site_favicon = ImagePathField(required=False, allow_null=True)
    blog_background = ImagePathField(required=False, allow_null=True)

    class Meta:
        model = SiteConfig
        fields = '__all__'


class MenuItemSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'url', 'icon', 'order', 'is_active', 'parent', 'children']

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return MenuItemSerializer(children, many=True).data


class MenuItemManageSerializer(serializers.ModelSerializer):
    """管理员用——扁平列表，包含父菜单名称"""
    parent_name = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'url', 'icon', 'order', 'is_active', 'parent', 'parent_name']

    def get_parent_name(self, obj):
        if obj.parent:
            return obj.parent.name
        return None


class GuestbookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guestbook
        fields = ['id', 'nickname', 'email', 'content', 'is_approved', 'created_at']


class MediaSerializer(serializers.ModelSerializer):
    """媒体列表/详情序列化（file 返回完整 URL）"""
    file_url = serializers.SerializerMethodField()
    file = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Media
        fields = ['id', 'file', 'file_url', 'filename', 'file_size',
                  'mime_type', 'uploaded_by', 'created_at']
        read_only_fields = ['filename', 'file_size', 'mime_type',
                            'uploaded_by', 'created_at']

    def get_file_url(self, obj):
        return obj.file_url
