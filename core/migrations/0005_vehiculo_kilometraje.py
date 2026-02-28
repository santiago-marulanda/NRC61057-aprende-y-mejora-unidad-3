from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_alter_vehiculo_placa_vehiculo_uniq_vehiculo_placa_ci"),
    ]

    operations = [
        migrations.AddField(
            model_name="vehiculo",
            name="kilometraje",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
