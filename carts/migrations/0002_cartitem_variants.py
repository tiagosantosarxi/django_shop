# Generated by Django 4.0.3 on 2022-04-17 22:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_variant'),
        ('carts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='variants',
            field=models.ManyToManyField(blank=True, to='store.variant'),
        ),
    ]
