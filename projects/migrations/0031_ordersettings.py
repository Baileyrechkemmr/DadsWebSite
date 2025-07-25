# Generated manually for OrderSettings model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0030_gallery'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orders_enabled', models.BooleanField(default=True, help_text='Uncheck to disable all order functionality and show \'no longer accepting orders\' message')),
                ('disabled_message', models.TextField(default='No longer accepting orders at this time', help_text='Message to display when orders are disabled')),
                ('disabled_image', models.ImageField(blank=True, help_text='Optional image to display when orders are disabled', null=True, upload_to='images/system/')),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Order Settings',
                'verbose_name_plural': 'Order Settings',
            },
        ),
    ]