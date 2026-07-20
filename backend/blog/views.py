from django.db.models import F
from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from users.models import UserProfile
from .models import Category, Tag, Article, Comment, SiteConfig, MenuItem, Guestbook
from .serializers import (
    CategorySerializer, TagSerializer,
    ArticleListSerializer, ArticleDetailSerializer, ArticleCreateUpdateSerializer,
    CommentSerializer, CommentCreateSerializer,
    SiteConfigSerializer, MenuItemSerializer, MenuItemManageSerializer, GuestbookSerializer,
)


class IsAdminOrEditorOrAuthor(permissions.BasePermission):
    """自定义权限：管理员、编辑、作者可访问"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser or request.user.is_staff:
            return True
        try:
            role = request.user.profile.role
            return role in ['admin', 'editor', 'author']
        except UserProfile.DoesNotExist:
            return False


class IsAdminOrEditor(permissions.BasePermission):
    """自定义权限：仅管理员和编辑可访问（用于用户管理等敏感操作）"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser or request.user.is_staff:
            return True
        try:
            return request.user.profile.role in ['admin', 'editor']
        except UserProfile.DoesNotExist:
            return False


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class ArticleViewSet(viewsets.ModelViewSet):
    pagination_class = StandardPagination
    filterset_fields = ['category', 'category__slug', 'tags__slug', 'status', 'article_type']
    search_fields = ['title', 'content', 'tags__name']
    ordering_fields = ['created_at', 'updated_at', 'view_count', 'published_at']

    def get_permissions(self):
        # 公开读取，管理员/编辑/作者可写
        if self.action in ['list', 'retrieve', 'archives', 'stats']:
            return [permissions.AllowAny()]
        return [IsAdminOrEditorOrAuthor()]

    def get_queryset(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return Article.objects.all()
        # retrieve 允许所有公开类型
        if self.action == 'retrieve':
            return Article.objects.filter(status='published')
        # 管理员可通过 ?scope=all 查看全部文章（否则公开列表仅已发布）
        qs = Article.objects.filter(status='published', article_type='article')
        user = self.request.user
        if user and user.is_authenticated and (user.is_superuser or user.is_staff):
            if self.request.query_params.get('scope') == 'all':
                qs = Article.objects.all()
        # 支持 status / article_type 筛选（管理员用）
        status_filter = self.request.query_params.get('status', None)
        type_filter = self.request.query_params.get('article_type', None)
        # 支持多分类筛选：?category_slug=tech,life（逗号分隔）
        category_slug = self.request.query_params.get('category_slug', None)
        if category_slug:
            slugs = [s.strip() for s in category_slug.split(',') if s.strip()]
            if slugs:
                # 按分类筛选时不过滤 article_type，展示该分类下所有类型的文章
                qs = Article.objects.filter(status='published', category__slug__in=slugs)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if type_filter:
            qs = qs.filter(article_type=type_filter)
        # 支持 month 参数筛选
        month = self.request.query_params.get('month', None)
        if month:
            qs = qs.filter(published_at__startswith=month)
        return qs

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ArticleCreateUpdateSerializer
        if self.action == 'retrieve':
            return ArticleDetailSerializer
        return ArticleListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 自动设置作者为当前登录用户
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # 异步增加阅读量，避免缓存问题
        Article.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
        instance.view_count += 1
        serializer = self.get_serializer(instance)

        # 添加上一篇/下一篇信息
        data = serializer.data
        qs = Article.objects.filter(status='published', article_type=instance.article_type)
        # 使用 created_at 作为排序基准（published_at 可能为 None）
        order_field = 'published_at' if instance.published_at else 'created_at'
        order_value = getattr(instance, order_field)

        previous = qs.filter(**{f'{order_field}__lt': order_value}).exclude(pk=instance.pk).order_by(f'-{order_field}').first()
        next_article = qs.filter(**{f'{order_field}__gt': order_value}).exclude(pk=instance.pk).order_by(order_field).first()
        data['previous_article'] = {'id': previous.id, 'title': previous.title} if previous else None
        data['next_article'] = {'id': next_article.id, 'title': next_article.title} if next_article else None

        return Response(data)

    @action(detail=False, methods=['get'])
    def archives(self, request):
        articles = Article.objects.filter(status='published', article_type='article').values('id', 'title', 'published_at')
        from collections import defaultdict
        month_articles = defaultdict(list)
        for a in articles:
            if a['published_at']:
                month_key = a['published_at'].strftime('%Y-%m')
                month_articles[month_key].append({'id': a['id'], 'title': a['title']})
        archives = [{'month': k, 'count': len(v), 'articles': v} for k, v in sorted(month_articles.items(), reverse=True)]
        return Response(archives)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        stats = {
            'total_articles': Article.objects.filter(status='published').count(),
            'total_comments': Comment.objects.filter(is_approved=True).count(),
            'total_categories': Category.objects.count(),
            'total_tags': Tag.objects.count(),
        }
        return Response(stats)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(parent__isnull=True)
    serializer_class = CategorySerializer
    pagination_class = None
    permission_classes = [permissions.AllowAny]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [permissions.AllowAny]


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentCreateSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardPagination

    def get_queryset(self):
        article_id = self.kwargs.get('article_pk')
        return Comment.objects.filter(article_id=article_id, is_approved=True, parent__isnull=True)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SiteConfigView(generics.RetrieveAPIView):
    queryset = SiteConfig.objects.all()
    serializer_class = SiteConfigSerializer
    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, *args, **kwargs):
        config = SiteConfig.objects.first()
        if not config:
            config = SiteConfig.objects.create()
        serializer = self.get_serializer(config)
        return Response(serializer.data)


class SiteConfigManageView(generics.RetrieveUpdateAPIView):
    """管理员站点配置管理（读写）"""
    serializer_class = SiteConfigSerializer
    permission_classes = [IsAdminOrEditorOrAuthor]

    def get_object(self):
        config = SiteConfig.objects.first()
        if not config:
            config = SiteConfig.objects.create()
        return config

    def perform_update(self, serializer):
        instance = serializer.save()
        # 同步 about_content → 关于页面 Article
        about_content = self.request.data.get('about_content', None)
        if about_content is not None:
            article, created = Article.objects.get_or_create(
                article_type='about',
                defaults={
                    'title': '关于',
                    'slug': 'about',
                    'content': about_content,
                    'author': self.request.user,
                    'status': 'published',
                    'summary': about_content[:200] if about_content else '',
                }
            )
            if not created:
                article.content = about_content
                if not article.summary:
                    article.summary = about_content[:200] if about_content else ''
                article.save()


class MenuItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MenuItem.objects.filter(is_active=True, parent__isnull=True)
    serializer_class = MenuItemSerializer
    pagination_class = None
    permission_classes = [permissions.AllowAny]


class GuestbookViewSet(viewsets.ModelViewSet):
    serializer_class = GuestbookSerializer
    http_method_names = ['get', 'post']
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Guestbook.objects.filter(is_approved=True)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CategoryManageViewSet(viewsets.ModelViewSet):
    """管理员分类管理"""
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrEditorOrAuthor]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    pagination_class = None

    def get_queryset(self):
        return Category.objects.filter(parent__isnull=True)

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        parent_id = request.data.get('parent')
        if parent_id is not None and int(parent_id) == instance.pk:
            return Response(
                {'error': '父分类不能指向自身'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.articles.exists():
            return Response(
                {'error': f'分类 "{instance.name}" 下有关联文章，无法删除'},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.delete()
        return Response({'message': '分类已删除'}, status=status.HTTP_204_NO_CONTENT)


class MenuItemManageViewSet(viewsets.ModelViewSet):
    """管理员菜单管理"""
    serializer_class = MenuItemManageSerializer
    permission_classes = [IsAdminOrEditorOrAuthor]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'create':
            return MenuItemSerializer
        if self.action in ['update', 'partial_update']:
            return MenuItemSerializer
        return MenuItemManageSerializer

    def get_queryset(self):
        return MenuItem.objects.all().select_related('parent')

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        parent_id = request.data.get('parent')
        if parent_id is not None and int(parent_id) == instance.pk:
            return Response(
                {'error': '父菜单不能指向自身'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'message': '菜单项已删除'}, status=status.HTTP_204_NO_CONTENT)


class GuestbookManageViewSet(viewsets.ModelViewSet):
    """管理员留言审核"""
    serializer_class = GuestbookSerializer
    permission_classes = [IsAdminOrEditorOrAuthor]
    http_method_names = ['get', 'put', 'patch', 'delete']
    pagination_class = None  # 管理界面不分页

    def get_queryset(self):
        qs = Guestbook.objects.all()
        approved = self.request.query_params.get('approved', None)
        if approved is not None:
            qs = qs.filter(is_approved=approved.lower() == 'true')
        return qs

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'message': '留言已删除'}, status=status.HTTP_204_NO_CONTENT)


class CommentManageViewSet(viewsets.ModelViewSet):
    """管理员评论管理"""
    serializer_class = CommentSerializer
    permission_classes = [IsAdminOrEditorOrAuthor]
    http_method_names = ['get', 'put', 'patch', 'delete']
    pagination_class = None  # 管理界面不分页

    def get_queryset(self):
        qs = Comment.objects.all()
        approved = self.request.query_params.get('approved', None)
        article_id = self.request.query_params.get('article', None)
        if approved is not None:
            qs = qs.filter(is_approved=approved.lower() == 'true')
        if article_id:
            qs = qs.filter(article_id=article_id)
        return qs.select_related('article')

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'message': '评论已删除'}, status=status.HTTP_204_NO_CONTENT)


class DiaryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ArticleListSerializer
    pagination_class = StandardPagination
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Article.objects.filter(status='published', article_type='diary')


class AboutView(generics.RetrieveAPIView):
    serializer_class = ArticleDetailSerializer
    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, *args, **kwargs):
        article = Article.objects.filter(status='published', article_type='about').first()
        if not article:
            return Response({'detail': '关于页面尚未创建'}, status=404)
        serializer = self.get_serializer(article)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminOrEditorOrAuthor])
def upload_image(request):
    """图片上传接口"""
    image = request.FILES.get('image')
    if not image:
        return Response({'error': '请上传图片'}, status=400)
    # 验证文件类型
    if not image.content_type.startswith('image/'):
        return Response({'error': '只允许上传图片文件'}, status=400)
    # 限制文件大小（5MB）
    if image.size > 5 * 1024 * 1024:
        return Response({'error': '图片大小不能超过5MB'}, status=400)
    # 保存到 articles/images/ 目录
    from django.core.files.storage import default_storage
    from django.conf import settings
    import os
    filename = default_storage.save(f'articles/images/{image.name}', image)
    url = f'{settings.MEDIA_URL}{filename}'
    return Response({'url': url, 'filename': image.name})
