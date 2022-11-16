# Generated by Django 3.2.8 on 2022-08-09 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0008_auto_20220809_2037'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='child',
        ),
        migrations.AddField(
            model_name='category',
            name='types',
            field=models.ManyToManyField(blank=True, null=True, related_name='categories', to='commerce.ProductType', verbose_name='Types'),
        ),
    ]