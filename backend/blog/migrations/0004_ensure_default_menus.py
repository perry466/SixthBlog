from django.db import migrations

DEFAULT_MENU_ITEMS = [
    {'name': '首页', 'url': '/home', 'icon': '', 'order': 1, 'is_active': True},
    {'name': '文章', 'url': '/articles', 'icon': '', 'order': 2, 'is_active': True},
    {'name': '归档', 'url': '/archives', 'icon': '', 'order': 3, 'is_active': True},
    {'name': '日记', 'url': '/diaries', 'icon': '', 'order': 4, 'is_active': True},
    {'name': '留言', 'url': '/guestbook', 'icon': '', 'order': 5, 'is_active': True},
    {'name': '关于', 'url': '/about', 'icon': '', 'order': 6, 'is_active': True},
]


def ensure_default_menus(apps, schema_editor):
    MenuItem = apps.get_model('blog', 'MenuItem')
    for item_data in DEFAULT_MENU_ITEMS:
        MenuItem.objects.get_or_create(
            name=item_data['name'],
            url=item_data['url'],
            defaults=item_data,
        )


def reverse_ensure(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_seed_default_menu_items'),
    ]

    operations = [
        migrations.RunPython(ensure_default_menus, reverse_ensure),
    ]
