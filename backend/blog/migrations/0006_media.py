# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog', '0005_alter_menuitem_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.ImageField(upload_to='media/%Y/%m/', verbose_name='文件')),
                ('filename', models.CharField(max_length=255, verbose_name='原始文件名')),
                ('file_size', models.IntegerField(default=0, verbose_name='文件大小(字节)')),
                ('mime_type', models.CharField(default='', max_length=50, verbose_name='MIME类型')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploads', to=settings.AUTH_USER_MODEL, verbose_name='上传者')),
            ],
            options={
                'verbose_name': '媒体文件',
                'verbose_name_plural': '媒体文件',
                'ordering': ['-created_at'],
            },
        ),
    ]
