# Generated by Django 5.1.3 on 2024-12-02 12:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Menu_Versions',
            fields=[
                ('version_id', models.AutoField(primary_key=True, serialize=False)),
                ('version_number', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Menus',
            fields=[
                ('menu_id', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Restaurants',
            fields=[
                ('restaurant_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('address', models.TextField(null=True)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(max_length=254, null=True, unique=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='MenuProcessingLogs',
            fields=[
                ('log_id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(max_length=50)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('processed_at', models.DateTimeField(auto_now_add=True)),
                ('version', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='processing_logs', to='menu_app.menu_versions')),
            ],
        ),
        migrations.AddField(
            model_name='menu_versions',
            name='menu',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='menu_app.menus'),
        ),
        migrations.CreateModel(
            name='MenuSections',
            fields=[
                ('section_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('menu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='menu_app.menus')),
            ],
        ),
        migrations.CreateModel(
            name='MenuItems',
            fields=[
                ('item_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='menu_app.menusections')),
            ],
        ),
        migrations.AddField(
            model_name='menus',
            name='restaurant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='menus', to='menu_app.restaurants'),
        ),
        migrations.CreateModel(
            name='DietaryRestrictions',
            fields=[
                ('restriction_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dietary_restrictions', to='menu_app.restaurants')),
            ],
        ),
        migrations.CreateModel(
            name='MenuItemDietaryRestrictions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('restriction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='menu_app.dietaryrestrictions')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='menu_app.menuitems')),
            ],
            options={
                'unique_together': {('item', 'restriction')},
            },
        ),
    ]
