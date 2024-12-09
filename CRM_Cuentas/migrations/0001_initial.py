# Generated by Django 4.2.17 on 2024-12-07 16:28

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id_cliente', models.AutoField(primary_key=True, serialize=False)),
                ('nombres', models.CharField(max_length=300)),
                ('telefono', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Cuenta',
            fields=[
                ('id_cuenta', models.AutoField(primary_key=True, serialize=False)),
                ('correo_cuenta', models.CharField(max_length=300)),
                ('contrasena', models.CharField(max_length=300)),
                ('fech_inicio', models.DateField(default=datetime.date.today)),
                ('mes', models.PositiveIntegerField()),
                ('fech_fin', models.DateField(blank=True, null=True)),
                ('estado', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Grupo',
            fields=[
                ('id_grupo', models.AutoField(primary_key=True, serialize=False)),
                ('descripcion', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='Servicio',
            fields=[
                ('id_servicio', models.AutoField(primary_key=True, serialize=False)),
                ('descripcion', models.CharField(max_length=300)),
                ('precio_mayorista', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cantidad_perfiles', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='TipoDispositivo',
            fields=[
                ('id_tipo_dispositivo', models.AutoField(primary_key=True, serialize=False)),
                ('descripcion', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id_plan', models.AutoField(primary_key=True, serialize=False)),
                ('descripcion', models.CharField(max_length=300)),
                ('numero_dispositivos', models.PositiveIntegerField()),
                ('numero_meses', models.PositiveIntegerField()),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('id_servicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CRM_Cuentas.servicio')),
            ],
        ),
        migrations.CreateModel(
            name='PerfilCuenta',
            fields=[
                ('id_perfil_cuenta', models.AutoField(primary_key=True, serialize=False)),
                ('usuario', models.CharField(max_length=300)),
                ('pin', models.PositiveIntegerField()),
                ('asignado', models.BooleanField()),
                ('id_cuenta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CRM_Cuentas.cuenta')),
            ],
        ),
        migrations.CreateModel(
            name='Perfil',
            fields=[
                ('id_perfil', models.AutoField(primary_key=True, serialize=False)),
                ('fech_inicio', models.DateField(default=datetime.date.today)),
                ('mes', models.PositiveIntegerField()),
                ('fech_fin', models.DateField(blank=True, null=True)),
                ('notas', models.CharField(blank=True, max_length=300)),
                ('estado', models.BooleanField(default=True)),
                ('id_cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CRM_Cuentas.cliente')),
                ('id_perfil_cuenta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CRM_Cuentas.perfilcuenta')),
                ('id_plan', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='CRM_Cuentas.plan')),
                ('id_tipo_dispositivo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CRM_Cuentas.tipodispositivo')),
            ],
        ),
        migrations.CreateModel(
            name='HistorialRenovacion',
            fields=[
                ('id_historial', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_renovacion', models.DateField(default=datetime.date.today)),
                ('meses_agregados', models.PositiveIntegerField()),
                ('correo_cuenta', models.CharField(max_length=300)),
                ('contrasena_cuenta', models.CharField(max_length=300)),
                ('usuario_perfil', models.CharField(max_length=300)),
                ('pin_perfil', models.PositiveIntegerField()),
                ('id_perfil', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CRM_Cuentas.perfil')),
                ('id_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CRM_Cuentas.plan')),
            ],
        ),
        migrations.AddField(
            model_name='cuenta',
            name='id_grupo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='CRM_Cuentas.grupo'),
        ),
        migrations.AddField(
            model_name='cuenta',
            name='id_servicio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CRM_Cuentas.servicio'),
        ),
        migrations.AddField(
            model_name='cuenta',
            name='id_tipo_dispositivo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CRM_Cuentas.tipodispositivo'),
        ),
    ]
