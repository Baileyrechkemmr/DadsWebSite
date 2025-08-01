# Generated by Django 4.2 on 2025-07-29 00:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0032_pagecontent'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='blog',
            options={'ordering': ['-date'], 'verbose_name': 'Blog Post', 'verbose_name_plural': 'Blog Posts'},
        ),
        migrations.AlterField(
            model_name='pagecontent',
            name='page_section',
            field=models.CharField(choices=[('sales_paypal_info', 'Sales Page - PayPal Information'), ('sales_form_title', 'Sales Page - Form Title'), ('footer_copyright', 'Footer - Copyright Text'), ('coming_soon_title', 'Coming Soon - Title'), ('coming_soon_message', 'Coming Soon - Message'), ('home_classes_description', 'Home Page - Classes Description'), ('home_l6_video_description', 'Home Page - L6 Video Description'), ('home_blog_description', 'Home Page - Blog Description'), ('about_biography', 'About Page - Howard Clark Biography'), ('order_paypal_instructions', 'Order Form - PayPal Instructions'), ('order_rules_section', 'Order Form - Rules & Pricing'), ('classes_general_info', 'Classes Page - General Information'), ('classes_payment_instructions', 'Classes Page - Payment Instructions'), ('classes_address_info', 'Classes Page - Address Information'), ('classes_materials_info', 'Classes Page - Materials Information'), ('classes_equipment_requirements', 'Classes Page - Equipment Requirements'), ('classes_safety_equipment', 'Classes Page - Safety Equipment'), ('classes_practice_recommendations', 'Classes Page - Practice Recommendations'), ('classes_one_on_one_info', 'Classes Page - One-on-One Lessons'), ('orders_disabled_title', 'Orders Disabled - Title'), ('orders_disabled_message', 'Orders Disabled - Message')], help_text='Select which section of the website this content belongs to', max_length=50, unique=True),
        ),
    ]
