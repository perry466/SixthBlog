from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import connections
from django.db.utils import OperationalError
from blog.models import SiteConfig


class SetupStatusView(generics.GenericAPIView):
    """检查系统是否已初始化"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        has_admin = User.objects.filter(is_superuser=True).exists()
        has_config = SiteConfig.objects.exists()
        return Response({
            'initialized': has_admin and has_config,
            'has_admin': has_admin,
            'has_config': has_config,
        })


class CheckDatabaseView(generics.GenericAPIView):
    """测试数据库连接"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            db_conn = connections['default']
            db_conn.cursor()
            return Response({'ok': True, 'message': '数据库连接成功'})
        except OperationalError as e:
            return Response({'ok': False, 'error': str(e)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'ok': False, 'error': f'数据库连接失败: {str(e)}'}, status=status.HTTP_200_OK)


class InstallView(generics.GenericAPIView):
    """执行首次安装：创建超级管理员 + 初始化站点配置"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # 防止重复安装
        if User.objects.filter(is_superuser=True).exists():
            return Response({'error': '系统已经安装过了'}, status=status.HTTP_400_BAD_REQUEST)

        username = request.data.get('username', '').strip()
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '')
        site_title = request.data.get('site_title', 'SixthBlog').strip()
        site_description = request.data.get('site_description', '').strip()

        # 参数校验
        if not username or len(username) < 3:
            return Response({'error': '用户名至少需要 3 个字符'}, status=status.HTTP_400_BAD_REQUEST)
        if not password or len(password) < 6:
            return Response({'error': '密码至少需要 6 个字符'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'error': f'用户名 "{username}" 已被占用'}, status=status.HTTP_400_BAD_REQUEST)
        if not site_title:
            return Response({'error': '请输入网站标题'}, status=status.HTTP_400_BAD_REQUEST)

        # 创建超级管理员
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
        except Exception as e:
            return Response({'error': f'创建管理员失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 初始化站点配置
        config, created = SiteConfig.objects.get_or_create(
            defaults={
                'site_title': site_title,
                'site_description': site_description,
            }
        )
        if not created and site_title:
            config.site_title = site_title
            config.site_description = site_description
            config.save()

        return Response({
            'message': '安装完成！欢迎使用 SixthBlog',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            },
            'site_title': config.site_title,
        }, status=status.HTTP_200_OK)
