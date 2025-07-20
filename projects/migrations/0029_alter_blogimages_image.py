# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0028_alter_hotel_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogimages',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]