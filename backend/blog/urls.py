from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'articles', views.ArticleViewSet, basename='article')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'tags', views.TagViewSet, basename='tag')
router.register(r'menu-items', views.MenuItemViewSet, basename='menuitem')
router.register(r'guestbook', views.GuestbookViewSet, basename='guestbook')
router.register(r'diaries', views.DiaryViewSet, basename='diary')

urlpatterns = [
    path('', include(router.urls)),
    path('site-config/', views.SiteConfigView.as_view(), name='site-config'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('upload-image/', views.upload_image, name='upload-image'),
    path('articles/<int:article_pk>/comments/', views.CommentViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='article-comments'),
    # 管理员分类管理
    path('admin/categories/', views.CategoryManageViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='admin-categories-list'),
    path('admin/categories/<int:pk>/', views.CategoryManageViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='admin-categories-detail'),
    # 管理员菜单管理
    path('admin/menu-items/', views.MenuItemManageViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='admin-menuitems-list'),
    path('admin/menu-items/<int:pk>/', views.MenuItemManageViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='admin-menuitems-detail'),
    # 管理员留言管理
    path('admin/guestbook/', views.GuestbookManageViewSet.as_view({
        'get': 'list',
    }), name='admin-guestbook-list'),
    path('admin/guestbook/<int:pk>/', views.GuestbookManageViewSet.as_view({
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='admin-guestbook-detail'),
    # 管理员站点配置
    path('admin/site-config/', views.SiteConfigManageView.as_view(), name='admin-site-config'),
    # 管理员评论管理
    path('admin/comments/', views.CommentManageViewSet.as_view({
        'get': 'list',
    }), name='admin-comments-list'),
    path('admin/comments/<int:pk>/', views.CommentManageViewSet.as_view({
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='admin-comments-detail'),
]
