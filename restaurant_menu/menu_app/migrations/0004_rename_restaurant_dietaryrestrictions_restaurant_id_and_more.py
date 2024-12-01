# Generated by Django 5.1.3 on 2024-12-01 23:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu_app', '0003_rename_restaurant_id_dietaryrestrictions_restaurant_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dietaryrestrictions',
            old_name='restaurant',
            new_name='restaurant_id',
        ),
        migrations.RenameField(
            model_name='menuitemdietaryrestrictions',
            old_name='item',
            new_name='item_id',
        ),
        migrations.RenameField(
            model_name='menuitemdietaryrestrictions',
            old_name='restriction',
            new_name='restriction_id',
        ),
        migrations.RenameField(
            model_name='menuitems',
            old_name='section',
            new_name='section_id',
        ),
        migrations.RenameField(
            model_name='menus',
            old_name='restaurant',
            new_name='restaurant_id',
        ),
        migrations.RenameField(
            model_name='menusections',
            old_name='menu',
            new_name='menu_id',
        ),
        migrations.RemoveField(
            model_name='menuprocessinglogs',
            name='menu',
        ),
        migrations.AlterField(
            model_name='restaurants',
            name='address',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='restaurants',
            name='email',
            field=models.EmailField(max_length=254, null=True, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='menuitemdietaryrestrictions',
            unique_together={('item_id', 'restriction_id')},
        ),
        migrations.CreateModel(
            name='Menu_Versions',
            fields=[
                ('version_id', models.AutoField(primary_key=True, serialize=False)),
                ('version_number', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('menu_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='menu_app.menus')),
            ],
        ),
        migrations.AddField(
            model_name='menuprocessinglogs',
            name='version_id',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='processing_logs', to='menu_app.menu_versions'),
        ),
    ]
