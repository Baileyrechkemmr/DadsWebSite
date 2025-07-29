# Generated manually for PageContent model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0031_ordersettings'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page_section', models.CharField(choices=[('sales_paypal_info', 'Sales Page - PayPal Information'), ('sales_form_title', 'Sales Page - Form Title'), ('footer_copyright', 'Footer - Copyright Text'), ('coming_soon_title', 'Coming Soon - Title'), ('coming_soon_message', 'Coming Soon - Message')], help_text='Select which section of the website this content belongs to', max_length=50, unique=True)),
                ('title', models.CharField(blank=True, help_text='Optional title for this content section', max_length=200)),
                ('content', models.TextField(help_text='The actual content that will be displayed on the website')),
                ('is_active', models.BooleanField(default=True, help_text='Uncheck to hide this content from the website')),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Page Content',
                'verbose_name_plural': 'Page Content',
                'ordering': ['page_section'],
            },
        ),
    ] 