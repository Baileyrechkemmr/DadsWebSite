# Generated by Django 4.2 on 2025-07-22 00:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0029_alter_blogimages_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Title for the gallery image', max_length=200)),
                ('image', models.ImageField(upload_to='images/gallery/')),
                ('description', models.TextField(blank=True, help_text='Optional description for the image')),
                ('is_active', models.BooleanField(default=True, help_text='Uncheck to hide from gallery')),
                ('sort_order', models.IntegerField(default=0, help_text='Lower numbers appear first')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Gallery Image',
                'verbose_name_plural': 'Gallery Images',
                'ordering': ['sort_order', '-date_added'],
            },
        ),
    ]
