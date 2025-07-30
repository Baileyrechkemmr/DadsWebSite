

from django.shortcuts import render, get_object_or_404, redirect

from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.utils.safestring import mark_safe

from .models import Year, Classes, Sword_img, Hotel, Blog, Sword_sales, BlogImages, OrderSettings, PageContent
# Create your views here.


def home(request):
    swords = Sword_img.objects

    

    context = {
        'swords': swords,

    }
    return render(request, 'projects/home.html', context)


def about(request):
    # Get page content for about page
    about_biography = PageContent.get_content('about_biography', 
        'Howard Clark is Omimi. Big Ear. The most sought after maker of Japanese style sword blades. The creator of the L6 Banite Katana which is hands down the highest performance sword blade in the world. Omimi-san has been a bladesmith for over 30 years. Early on he mastered forging, damascus, and distal symmetry. As Morgan Valley Forge Howard produced knives with organic flow and keen balance. Everything he made was meant to be used and felt right in the hand. The natural style of his work in straight fixed blades and folders is distinctive.\n\nHoward delved deep into the science of metallurgy. Teaching himself how to read isothermal transformation diagrams he began the journey to create what he desired as the best blade. One that was tough; would not chip, crack or break. One that was hard enough to hold it\'s edge for prolonged use and still be able to be resharpened. Through his research it is said Howard broke more blades deliberately than most knife-makers made. With known steel alloys, controlled temperatures, the test of the metal was in the heat treatment.\n\nIt is interesting to see so much of what is now readily accepted as standard practice and regurgitated on internet forums and bulletin boards came originally from Howard Clark. It was a long time coming. At the git go the good-old-boys-club of knife making didn\'t want to accept what this upstart was teaching. They didn\'t want to hear: that blind procedure without analysis could not produce consistent quality blades; that color of a hot blade prior to quenching was subjective; that besides carbon content other alloys in a steel also played roles and changed the dynamics of the heat treatment dance for a given steel to get the desired end product.\n\nThere are multiple reasons and much history in why Omimi is the sole source of the L6 Banite Katana. Why the Omimi 1086 Katana will out match the majority of Japanese style blades and the Omimi L6 is the quantum leap beyond. It is his genius level intellect. It is his hard working hands that create. It is his eye that can look down all surfaces of a 30 inch katana and see where the plane is a few thousandths of an inch off. It is Omimi.\n\nWelcome to the Morgan Valley Forge site. Thank you for visiting.')
    

    
    context = {
        'about_biography': about_biography,

    }
    return render(request, 'projects/about.html', context)


def classes(request):
    if request.method == 'POST':
        class_name = request.POST.get('class_name', '')
        email = request.POST.get('email', '')
        name = request.POST.get('name', '')
        address_1 = request.POST.get('address_1', '')
        address_2 = request.POST.get('address_2', '')
        city = request.POST.get('city', '')
        state_or_province = request.POST.get('state_or_province', '')
        zip_code = request.POST.get('zip_code', '')
        country = request.POST.get('country', '')
        phone_number = request.POST.get('phone_number', '')

        messages = f"""
        Class Name: {class_name}
        Email: {email}
        Name: {name}
        Address 1: {address_1}
        Address 2: {address_2}
        City: {city}
        State or Province: {state_or_province}
        Zip Code: {zip_code}
        Country: {country}
        Phone Number: {phone_number}
        """
        send_mail(
            'class singe up form',  # email titel
            messages,  # messages
            settings.EMAIL_HOST_USER,  # email for site
            ['howard@mvforge.com', 'Christine@mvforge.com'],  # email of recever
            fail_silently=False)
    year = Year.objects
    classes = Classes.objects
    hotel = Hotel.objects
    
    # Get page content for classes page
    classes_general_info = PageContent.get_content('classes_general_info', 
        'Each of these classes will include one day of forging blade(s), grinding, heat treating, and assembling a basic forged carbon steel knife. All classes are limited to four participants\n\n$775 for the week. $700 tuition, plus $75 materials fee')
    
    classes_payment_instructions = PageContent.get_content('classes_payment_instructions', 
        'To secure your spot in any of these classes, Email to howard@mvforge.com, and send a $200 deposit to howard@mvforge.com via PayPal, making sure to mention which class.\n\nBalance due two weeks prior to class start date')
    
    classes_address_info = PageContent.get_content('classes_address_info', 
        'Or mail a check to Howard Clark\n115 35th Place\nRunnells, IA 50237')
    
    classes_materials_info = PageContent.get_content('classes_materials_info', 
        'All required materials will be provided. Blade steel, basic shop supplies, and basic handle materials. Premium materials may be available for additional cost.')
    
    classes_equipment_requirements = PageContent.get_content('classes_equipment_requirements', 
        'You will need long pants, leather shoes, safety glasses, and a dust particle mask of your liking, at least a p95 rating. Bringing snacks or lunch is required, as the shop is in a rural location and lunch is not readily available without driving a few miles')
    
    classes_safety_equipment = PageContent.get_content('classes_safety_equipment', 
        'For forging classes, you may also want an apron as well as gloves to protect your from heat and sparks. Hot mill gloves made from cotton, or cotton chore gloves are advised. Leather can and will shrink fit onto your hand at times, and can exacerbate the burn potential in this way.')
    
    classes_practice_recommendations = PageContent.get_content('classes_practice_recommendations', 
        'If you have no prior forging experience, then some hammer practice time may be in order. One of my dear late friends, Larry Harley, always suggested that folks get a carpenters hammer and a pile of nails, and some scrap lumber, and simply drive nails. It builds accuracy, which is essential to forging success.')
    
    classes_one_on_one_info = PageContent.get_content('classes_one_on_one_info', 
        'It is also possible that we may be able to accommodate one on one lessons at the rate of $500/day, scheduling to be decided. Please inquire via e-mail, howard@mvforge.com')
    
    footer_copyright = PageContent.get_content('footer_copyright', 
        'Morgan Valley forge since 1988.')
    
    coming_soon_title = PageContent.get_content('coming_soon_title', 'Coming Soon')
    coming_soon_message = PageContent.get_content('coming_soon_message', 
        'Our website is currently under construction. Please check back later!')
    
    context = {
        'classes': classes, 
        'hotel': hotel, 
        'year': year,
        'classes_general_info': classes_general_info,
        'classes_payment_instructions': classes_payment_instructions,
        'classes_address_info': classes_address_info,
        'classes_materials_info': classes_materials_info,
        'classes_equipment_requirements': classes_equipment_requirements,
        'classes_safety_equipment': classes_safety_equipment,
        'classes_practice_recommendations': classes_practice_recommendations,
        'classes_one_on_one_info': classes_one_on_one_info,
        'footer_copyright': footer_copyright,
        'coming_soon_title': coming_soon_title,
        'coming_soon_message': coming_soon_message,
    }
    return render(request, 'projects/classes.html', context)


def movie(request):
    return render(request, 'projects/movie.html')


def blog(request):
    blogs = Blog.objects.all()
    
    # Get blog page content
    blog_page_greeting = PageContent.get_content('blog_page_greeting', 
        'A Look into the Life of Howard Clark and his Animal companions')
    
    context = {
        'blogs': blogs,
        'blog_page_greeting': blog_page_greeting,
    }

    return render(request, 'projects/blog.html', context)



def gallery(request):
    # Get only active gallery images, ordered by sort_order and date
    from .models import Gallery
    gallery_images = Gallery.objects.filter(is_active=True)
    
    context = {
        'gallery_images': gallery_images,
    }
    return render(request, 'projects/gallery.html', context)


def details_s(request, sword_img_id):
    sword_detail = get_object_or_404(Sword_img, pk=sword_img_id)
    return render(request, 'projects/details_s.html', {'sword': sword_detail})


def order_form(request):
    # Check if orders are enabled (with error handling for initial deployment)
    try:
        order_settings = OrderSettings.get_settings()
        if not order_settings.orders_enabled:
            # Get page content for orders disabled page
            orders_disabled_title = PageContent.get_content('orders_disabled_title', 
                'Custom Sword Orders Currently Unavailable')
            orders_disabled_message = PageContent.get_content('orders_disabled_message', 
                'We apologize for any inconvenience. Please check back later or browse our available swords in the Sales section.')
            footer_copyright = PageContent.get_content('footer_copyright', 
                'Morgan Valley forge since 1988.')
            
            return render(request, 'projects/orders_disabled.html', {
                'disabled_message': order_settings.disabled_message,
                'disabled_image': order_settings.disabled_image,
                'orders_disabled_title': orders_disabled_title,
                'orders_disabled_message': orders_disabled_message,
                'footer_copyright': footer_copyright,
            })
    except Exception:
        # If OrderSettings table doesn't exist yet (before migration), 
        # default to orders enabled to maintain existing functionality
        pass
    
    if request.method == 'POST':
        email = request.POST.get('email', '')
        name = request.POST.get('name', '')
        address_1 = request.POST.get('address_1', '')
        address_2 = request.POST.get('address_2', '')
        city = request.POST.get('city', '')
        state_or_province = request.POST.get('state_or_province', '')
        zip_code = request.POST.get('zip_code', '')
        country = request.POST.get('country', '')
        phone_number = request.POST.get('phone_number', '')
        depth_of_sori = request.POST.get('depth_of_sori', '')
        length_of_blade = request.POST.get('length_of_blade', '')
        type_of_steel = request.POST.get('type_of_steel', '')
        other_specifications = request.POST.get('other_specifications', '')

        messages = f"""
        Email: {email}
        Name: {name}
        Address 1: {address_1}
        Address 2: {address_2}
        City: {city}
        State or Province: {state_or_province}
        Zip Code: {zip_code}
        Country: {country}
        Phone Number: {phone_number}
        Depth of Sori: {depth_of_sori}
        Length of Blade: {length_of_blade}
        Type of Steel: {type_of_steel}
        Other Specifications: {other_specifications}
        """
        send_mail(
            'Sword order form', #email titel
            messages, # messages
            settings.EMAIL_HOST_USER, #email for site
            ['howard@mvforge.com', 'Christine@mvforge.com'],  # email of recever
        fail_silently=False)
    
    # Get page content for order form page
    sword_order_payment_instructions = PageContent.get_content('')
    
    sword_order_info_section = PageContent.get_content('sword_order_info_section', 
        '')
    

    
    context = {
        'sword_order_payment_instructions': sword_order_payment_instructions,
        'sword_order_info_section': sword_order_info_section,
    }
    return render(request, 'projects/order_form.html', context)


def details_h(request, hotel_id):
    hotel_details = get_object_or_404(Hotel, pk=hotel_id)
    return render(request, 'projects/details_h.html', {'hotel': hotel_details})


def sales(request):
    if request.method == 'POST':
        item_number = request.POST.get('item_number', '')
        email = request.POST.get('email', '')
        name = request.POST.get('name', '')
        address_1 = request.POST.get('address_1', '')
        address_2 = request.POST.get('address_2', '')
        city = request.POST.get('city', '')
        state_or_province = request.POST.get('state_or_province', '')
        zip_code = request.POST.get('zip_code', '')
        country = request.POST.get('country', '')
        phone_number = request.POST.get('phone_number', '')

        messages = f"""
        Item Number: {item_number}
        Email: {email}
        Name: {name}
        Address 1: {address_1}
        Address 2: {address_2}
        City: {city}
        State or Province: {state_or_province}
        Zip Code: {zip_code}
        Country: {country}
        Phone Number: {phone_number}
        """
        send_mail(
            'Sales order form',  # email titel
            messages,  # messages
            settings.EMAIL_HOST_USER,  # email for site
            ['howard@mvforge.com', 'Christine@mvforge.com'],  # email of recever
            fail_silently=False)

    # Get page content for sales page
    payment_info = PageContent.get_content('sales_page_payment_info', 
        'To secure your order, send a PayPal payment to howard@mvforge.com and please include complete contact information, such as a mailing address, shipping address (if different), email contact, and a telephone number. Or we can make arrangements to accept a credit card in other ways. Contact us at howard@mvforge.com for more options.')

    sword_sales = Sword_sales.objects
    context = {
        'sword_sales': sword_sales,
        'payment_info': payment_info,
    }
    return render(request, 'projects/sales.html', context)


def details_sales(request, sword_sales_id):
    sword_sales_detail = get_object_or_404(Sword_sales, pk=sword_sales_id)
    return render(request, 'projects/details_sales.html', {'sword_sales_detail': sword_sales_detail})


def gallery_detail(request, gallery_id):
    """Display detailed view of a gallery item using existing details_s template"""
    from .models import Gallery
    gallery_item = get_object_or_404(Gallery, pk=gallery_id)
    # Use existing details_s.html template by mapping gallery fields to sword fields
    return render(request, 'projects/details_s.html', {'sword': gallery_item})
