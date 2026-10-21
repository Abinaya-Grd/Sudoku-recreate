from django.urls import path
from . import views

urlpatterns = [
    path('', views.category_page),
    path('subcategory/<int:id>/', views.subcategory_page),
    path('products/<int:id>/', views.product_page),
    path('add-cart/<int:product_id>/<int:variant_id>/', views.add_cart),
    path('decrease-cart/<int:item_id>/', views.decrease_cart),
    path('decrease-cart-variant/<int:product_id>/<int:variant_id>/',views.decrease_cart_variant),
    path('clear-cart/', views.clear_cart),
    path('product-details/<int:id>/', views.product_details),
    path('banner-products/<int:id>/', views.banner_products_page),
    path('slider-products/<int:id>/', views.slider_products_page),
    path('explore-all/', views.explore_all_page),
    path('cart/', views.cart_page),
    path('login/',views.login_page),
    path("send-otp/", views.send_otp, name="send_otp"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("resend-otp/", views.resend_otp, name="resend_otp"),
    path("payment/", views.payment_page),
    path("order-success/", views.order_success),
    path("order-success/", views.order_success),
    path("my-orders/", views.my_orders),
    path("address/", views.address_page),
    path("save-tip/", views.save_tip),
]
