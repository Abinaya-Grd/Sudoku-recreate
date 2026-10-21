from django.shortcuts import render,redirect,get_object_or_404
from .models import Category, SubCategory, Product, ProductVariant, Cart, CartItem, Banner, GrabEssentials, ExploreCategories, BannerList, HomeProductSection ,SimilarProduct
from django.http import HttpResponse
import random
from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import UserOTP
import razorpay
from django.conf import settings
from .models import Order, OrderItem , Address

def category_page(request):
    categories = Category.objects.all()
    banners = Banner.objects.all()
    banner_lists = BannerList.objects.all()
    explore_categories = ExploreCategories.objects.all()
    grab_items = GrabEssentials.objects.all()
    home_sections = HomeProductSection.objects.all()

    return render(request, 'category.html', {
        'categories': categories,
        'banners': banners,
        'banner_lists':banner_lists,
        'explore_categories': explore_categories,
        'grab_items':grab_items,
        'home_sections':home_sections,
    })

def explore_all_page(request):
    explore_categories = ExploreCategories.objects.all()
    return render(request, 'explore_all.html',{
       'explore_categories': explore_categories
    })
     
def banner_products_page(request,id):
    banner = BannerList.objects.get(id=id)
    products = banner.products.all()

    return render(request, 'product.html', {
        'products': products,
        'subcategories': [],
    })
    
def slider_products_page(request,id):
    banner = Banner.objects.get(id=id)
    products = banner.products.all()

    return render(request, 'product.html', {
        'products': products,
        'subcategories': [],
    })
       
def subcategory_page(request, id):

    subcategories = SubCategory.objects.filter(category=id)

    products = Product.objects.filter(category=id)

    sub_id = request.GET.get('sub')

    if sub_id:
        products = Product.objects.filter(subcategory=sub_id)

    return render(request, 'subcategory.html', {
        'subcategories': subcategories,
        'products': products
    })

def product_page(request, id):

    products = Product.objects.filter(subcategory=id)

    print(products)

    return render(request, 'product.html', {
        'products': products
    })


def product_details(request, id):
    
    product = Product.objects.get(id=id)

    variants = product.variants.all()

    similar_entry = SimilarProduct.objects.filter(
        product=product
    ).first()

    similar_products = []

    if similar_entry:
        similar_products = similar_entry.similar_product.all()

    return render(request, 'product_details.html', {
        'product': product,
        'variants': variants,
        'similar_products': similar_products
    })


def decrease_cart_variant(request, product_id, variant_id):
    cart = get_cart(request)

    item = CartItem.objects.filter(
        cart=cart,
        product_id=product_id,
        variant_id=variant_id
    ).first()

    if item:
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()

    return redirect('/cart/')


def get_cart(request):
   
    print("SESSION USER =", request.session.get("user_mobile"))

    user_mobile = request.session.get("user_mobile")

    if not user_mobile:
        return None

    user = UserOTP.objects.get(
        mobile_number=user_mobile
    )

    cart, created = Cart.objects.get_or_create(
        user=user
    )

    return cart
def add_cart(request, product_id, variant_id):
    
    cart = get_cart(request)

    if not cart:
        return redirect('/login/')

    product = get_object_or_404(Product, id=product_id)

    variant = get_object_or_404(
        ProductVariant,
        id=variant_id,
        product=product
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=variant,
        defaults={
            "variant_label": variant.label,
            "price": variant.price,
            "discount_price": variant.discount_price,
            "quantity": 1,
        }
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('/cart/')
def decrease_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('/cart/')

def clear_cart(request):
    
    cart = get_cart(request)

    if not cart:
        return redirect('/cart/')

    cart.items.all().delete()

    return redirect('/cart/')

def cart_page(request):
    cart = get_cart(request)
    cart_items = cart.items.all()

    return render(request, "cart.html", {
        "cart": cart,
        "cart_items": cart_items
    })

def cart_page(request):
    
    cart = get_cart(request)

    if not cart:

        return render(request, "cart.html",  { "cart": None, "cart_items": []})


    cart_items = cart.items.all()

    return render(request, "cart.html", {
        "cart": cart,
        "cart_items": cart_items
    })




def generate_otp():
    return str(random.randint(1000, 9999))


@csrf_exempt
def send_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)

        mobile_number = data.get("mobileNumber", "").strip()

        if len(mobile_number) != 10 or not mobile_number.isdigit():
            return JsonResponse({
                "error": "Invalid mobile number format"
            }, status=400)

        user, created = UserOTP.objects.get_or_create(
            mobile_number=mobile_number
        )

        otp = generate_otp()

        user.otp = otp
        user.otp_expiry = timezone.now() + timedelta(minutes=5)
        user.is_verified = False
        user.save()

        print("OTP:", otp)

        return JsonResponse({
            "message": "OTP sent successfully",
            "otp_for_testing": otp
        })

    return JsonResponse({"error": "Only POST method allowed"}, status=405)


@csrf_exempt
def verify_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)

        mobile_number = data.get("mobileNumber")
        entered_otp = data.get("enteredOTP")

        user, created = UserOTP.objects.get_or_create(
            mobile_number=mobile_number
        )

        if entered_otp == "firebase_verified":
            user.is_verified = True
            user.otp = None
            user.save()

            request.session["user_mobile"] = mobile_number
            request.session.modified = True
            request.session.save()

            return JsonResponse({
                "message": "Login success",
                "userId": user.id
            })

        return JsonResponse({
            "message": "Incorrect OTP"
        }, status=400)

    return JsonResponse({
        "error": "Only POST method allowed"
    }, status=405)




@csrf_exempt
def resend_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)

        mobile_number = data.get("mobileNumber")

        try:
            user = UserOTP.objects.get(mobile_number=mobile_number)
        except UserOTP.DoesNotExist:
            return JsonResponse({
                "message": "User not found"
            }, status=400)

        otp = generate_otp()

        user.otp = otp
        user.otp_expiry = timezone.now() + timedelta(minutes=5)
        user.is_verified = False
        user.save()

        print("Resend OTP:", otp)

        return JsonResponse({
            "message": "OTP resent successfully",
            "otp_for_testing": otp
        })

    return JsonResponse({"error": "Only POST method allowed"}, status=405)

def login_page(request):
    
    return render(request , "login.html")
@csrf_exempt
def save_tip(request):
    data = json.loads(request.body)
    tip = int(data.get("tip", 0))

    cart = get_cart(request)

    if cart:
        cart.delivery_tip = tip
        cart.save()

    return JsonResponse({"message": "Tip saved"})
def payment_page(request):

    cart = get_cart(request)

    if not cart:
        return redirect('/cart/')

    total_amount = cart.total_bill()

    razorpay_amount = int(total_amount * 100)

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    payment = client.order.create({
        "amount": razorpay_amount,
        "currency": "INR",
        "payment_capture": 1
    })

    return render(request, "payment.html", {
        "payment": payment,
        "key_id": settings.RAZORPAY_KEY_ID,
        "amount": razorpay_amount,
        "display_amount": total_amount
    })

def order_success(request):
    cart = get_cart(request)

    if cart and cart.items.exists():
        order = Order.objects.create(
            user=cart.user,
            total_amount=cart.total_bill(),
            status="Placed"
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product_name=item.product.name,
                variant_label=item.variant_label,
                quantity=item.quantity,
                price=item.discount_price
            )

        cart.items.all().delete()

    return render(request, "order_success.html")

def my_orders(request):
    cart = get_cart(request)

    if not cart:
        return redirect('/login/')

    orders = Order.objects.filter(user=cart.user).order_by("-created_at")

    return render(request, "my_orders.html", {
        "orders": orders
    })

from .models import Address

def address_page(request):

    cart = get_cart(request)

    if not cart or not cart.user:
        return redirect('/login/')

    if request.method == "POST":

        Address.objects.create(
            user=cart.user,
            name=request.POST.get("name"),
            mobile=request.POST.get("mobile"),
            house=request.POST.get("house"),
            area=request.POST.get("area"),
            city=request.POST.get("city"),
            pincode=request.POST.get("pincode")
        )

        return redirect('/cart/')

    return render(request, "address.html")