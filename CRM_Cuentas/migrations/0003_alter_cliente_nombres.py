# Generated by Django 4.2.16 on 2024-12-09 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CRM_Cuentas', '0002_alter_perfil_id_cliente'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='nombres',
            field=models.CharField(max_length=500),
        ),
    ]
