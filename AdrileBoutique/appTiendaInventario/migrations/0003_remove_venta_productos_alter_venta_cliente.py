# Generated by Django 4.2.5 on 2023-10-14 23:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appTiendaInventario', '0002_remove_compra_productos'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='venta',
            name='productos',
        ),
        migrations.AlterField(
            model_name='venta',
            name='cliente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appTiendaInventario.cliente'),
        ),
    ]