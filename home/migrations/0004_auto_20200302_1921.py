# Generated by Django 3.0 on 2020-03-02 19:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_auto_20200302_1827'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transhomepage',
            old_name='body_de',
            new_name='body_ar',
        ),
        migrations.RenameField(
            model_name='transhomepage',
            old_name='body_it',
            new_name='body_po',
        ),
    ]