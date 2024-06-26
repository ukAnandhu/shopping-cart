# Generated by Django 4.2.9 on 2024-05-03 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=150, unique=True)),
                ('slug', models.CharField(max_length=150, unique=True)),
                ('description', models.TextField(max_length=200)),
                ('category_img', models.ImageField(blank=True, upload_to='photos/Categories')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
    ]
