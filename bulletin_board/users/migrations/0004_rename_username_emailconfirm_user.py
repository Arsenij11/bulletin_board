# Generated by Django 5.1 on 2024-10-03 04:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_rename_passwordconfirm_emailconfirm'),
    ]

    operations = [
        migrations.RenameField(
            model_name='emailconfirm',
            old_name='username',
            new_name='user',
        ),
    ]
