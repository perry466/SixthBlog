# Generated migration: fix Tag.slug to accept Unicode characters

from django.db import migrations, models


def fix_empty_slugs(apps, schema_editor):
    """修复旧数据中 slug 为空的标签，用标签名作为 slug"""
    Tag = apps.get_model('blog', 'Tag')
    for tag in Tag.objects.filter(slug=''):
        # 用 slugify(name, allow_unicode=True) 生成新 slug
        # 如果打不到 slugify，直接用 name 作为 slug
        tag.slug = tag.name
        tag.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_media'),
    ]

    operations = [
        # SlugField -> CharField：移除 ASCII-only 验证器，允许中文 slug
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.CharField(max_length=50, unique=True, verbose_name='标签标识'),
        ),
        # 修复已有空 slug 数据
        migrations.RunPython(fix_empty_slugs, migrations.RunPython.noop),
    ]
