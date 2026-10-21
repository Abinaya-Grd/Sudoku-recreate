from django.db import models
import random
import string

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)

    def __str__(self):
        return self.name
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey('SubCategory', on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    price = models.IntegerField()
    image = models.ImageField(upload_to='products/')

    sku_code = models.CharField(max_length=100, unique=True, blank=True, null=True)
    sku_classification = models.CharField(max_length=100, blank=True, null=True)
    sku_classification1 = models.CharField(max_length=100, blank=True, null=True)

    discount_price = models.IntegerField(blank=True, null=True)
    offer = models.CharField(max_length=100, blank=True, null=True)

    about = models.TextField(blank=True, null=True)
    health_benefits = models.TextField(blank=True, null=True)
    nutrition = models.TextField(blank=True, null=True)
    origin = models.TextField(blank=True, null=True)

    def generate_sku(self):
        name_code = self.name[:3].upper()
        random_number = ''.join(random.choices(string.digits, k=5))
        return f"PRO-{name_code}-{random_number}"

    def save(self, *args, **kwargs):
        if not self.sku_code:
            sku = self.generate_sku()

            while Product.objects.filter(sku_code=sku).exists():
                sku = self.generate_sku()

            self.sku_code = sku

        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')

    sku_code = models.CharField(max_length=100, unique=True, blank=True, null=True)

    label = models.CharField(max_length=100)
    price = models.IntegerField()
    discount_price = models.IntegerField(blank=True, null=True)
    offer = models.CharField(max_length=100, blank=True, null=True)

    is_combo_pack = models.BooleanField(default=False)
    is_multi_pack = models.BooleanField(default=False)

    combo_sku_code = models.CharField(max_length=100, blank=True, null=True)
    combo_name = models.CharField(max_length=100, blank=True, null=True)
    combo_image = models.ImageField(upload_to='combo/', blank=True, null=True)

    stock_quantity = models.IntegerField(default=0)
    image = models.ImageField(upload_to='variant/', blank=True, null=True)
    cart_quantity = models.IntegerField(default=0)

    def generate_sku(self):
        product_code = self.product.name[:3].upper()
        label_code = self.label.replace(" ", "").replace("-", "").upper()[:6]
        random_number = ''.join(random.choices(string.digits, k=4))
        return f"{product_code}-{label_code}-{random_number}"

    def save(self, *args, **kwargs):
        if not self.sku_code:
            sku = self.generate_sku()

            while ProductVariant.objects.filter(sku_code=sku).exists():
                sku = self.generate_sku()

            self.sku_code = sku

        super().save(*args, **kwargs)

    def __str__(self):
        return self.label  
class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='subcategory/')
    
    def __str__(self):
            return self.name      
class GrabEssentials(models.Model):
    image = models.ImageField(upload_to='GrabEssentials')
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.name  
class Cart(models.Model):
    session_key = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True
    )

    user = models.ForeignKey(
        "UserOTP",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="carts"
    )

    delivery_instructions = models.TextField(blank=True, null=True)
    add_notes = models.TextField(blank=True, null=True)
    delivery_tip = models.IntegerField(default=0)

    def __str__(self):
        return str(self.user) if self.user else str(self.session_key)
    def item_total(self):
        total = 0
        for item in self.items.all():
            price = item.discount_price if item.discount_price else item.price
            total += price * item.quantity
        return total
    def subtotal_with_gst(self):
        return self.item_total() + self.gst()
    
    def gst(self):
        return round(self.item_total() * 0.05, 2)

    def handling_charges(self):
        return 10

    def delivery_fee(self):
        return 50

    def total_bill(self):
        return self.item_total() + self.gst() + self.delivery_fee() + self.delivery_tip + self.handling_charges()

    def savings(self):
        total = 0
        for item in self.items.all():
            if item.discount_price:
                total += (item.price - item.discount_price) * item.quantity
        return total

    def __str__(self):
        return self.session_key
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)

    quantity = models.IntegerField(default=1)
    variant_label = models.CharField(max_length=100)
    image = models.ImageField(upload_to="cart/", blank=True, null=True)

    price = models.IntegerField()
    discount_price = models.IntegerField(blank=True, null=True)

    def total_price(self):
        final_price = self.discount_price if self.discount_price else self.price
        return final_price * self.quantity

    def __str__(self):
        return self.product.name      
class BannerList(models.Model):
    
    BANNER_TYPES = [
        ('offer', 'Offer'),
        ('festival', 'Festival'),
        ('dailyusage', 'Daily Usage'),
    ]

    banner_type = models.CharField(
        max_length=50,
        choices=BANNER_TYPES
    )

    image = models.ImageField(upload_to='banner_list/')

    products = models.ManyToManyField(Product)  
class Banner(models.Model):
    image = models.ImageField(upload_to='banners/')
    products = models.ManyToManyField(Product,blank=True)

    def __str__(self):
        return self.image.name
class ExploreCategories(models.Model):
    image = models.ImageField(upload_to='GrabEssentials')
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return self.name
class HomeProductSection(models.Model):
    display_name = models.CharField(max_length=100)
    products = models.ManyToManyField(Product)
        
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

 
    def __str__(self):
        return self.display_name

class SimilarProduct(models.Model):
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="similar_for"
    )

    similar_product = models.ManyToManyField(
        Product,
        related_name="similar_to",
        blank=True
    )

    def __str__(self):
        return self.product.name
class UserOTP(models.Model):
    mobile_number=models.CharField(max_length=10,unique=True)
    name=models.CharField(max_length=100,blank=True)
    email=models.EmailField(max_length=254,blank=True,null=True)
    otp=models.CharField(max_length=6,blank=True,null=True)
    otp_expiry=models.DateTimeField(blank=True,null=True)
    is_verified=models.BooleanField(blank=True,null=True)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.mobile_number
class Address(models.Model):

    user = models.ForeignKey(
        UserOTP,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=10)

    house = models.CharField(max_length=200)
    area = models.CharField(max_length=200)

    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Order(models.Model):
    user = models.ForeignKey(UserOTP, on_delete=models.CASCADE)
    total_amount = models.IntegerField()
    status = models.CharField(max_length=50, default="Placed")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.mobile_number)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_name = models.CharField(max_length=100)
    variant_label = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price = models.IntegerField()

    def __str__(self):
        return self.product_name