# Generated by Django 3.2.18 on 2023-08-10 13:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0027_auto_20230810_1308'),
    ]

    operations = [
        migrations.CreateModel(
            name='SignatureImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(help_text="Image of person's signature", upload_to='photos/signatures', verbose_name='Image')),
                ('name', models.CharField(help_text='Name of person to whom signature belongs.', max_length=255, verbose_name='Name')),
            ],
        ),
        migrations.AddField(
            model_name='eventstaff',
            name='use_signature_on_certificate',
            field=models.BooleanField(default=False, help_text='Enabling will display signature image on certificate. If not enabled, the printed name will be used. (If using certificates)', verbose_name='Use Signature Image on Certificate'),
        ),
        migrations.AddField(
            model_name='eventstaff',
            name='signature_image',
            field=models.ForeignKey(blank=True, help_text="Optional image of staff member's signature", null=True, on_delete=django.db.models.deletion.SET_NULL, to='events.signatureimage'),
        ),
    ]
