# Generated by Django 5.1.1 on 2024-10-05 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processing', '0003_remove_product_farmer'),
        ('user_app', '0002_processor_products'),
    ]

    operations = [
        migrations.AddField(
            model_name='farmer',
            name='products',
            field=models.ManyToManyField(related_name='farmers', to='processing.product'),
        ),
    ]
