# Generated by Django 3.2 on 2024-07-27 15:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20240727_1838'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredientrecipie',
            old_name='recipie',
            new_name='recipe',
        ),
    ]
