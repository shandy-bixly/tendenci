# Generated by Django 1.11.27 on 2020-01-15 10:52


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0011_auto_20190408_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='region',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='region'),
        ),
    ]
