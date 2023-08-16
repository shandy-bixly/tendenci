# Generated by Django 3.2.18 on 2023-08-15 18:38

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0031_alter_eventstaff_include_on_certificate'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrantcredits',
            name='credit_dt',
            field=models.DateTimeField(db_index=True, default=datetime.datetime(2023, 8, 15, 18, 38, 17, 465365)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='registrantcredits',
            name='event',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='events.event'),
            preserve_default=False,
        ),
    ]
