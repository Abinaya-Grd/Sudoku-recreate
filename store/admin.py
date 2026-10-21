from django.contrib import admin
from .models import Category,SubCategory , Product , Cart, Banner,BannerList ,GrabEssentials, ExploreCategories, ProductVariant ,CartItem,HomeProductSection ,SimilarProduct

admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Product)
admin.site.register(GrabEssentials)
admin.site.register(Cart)
admin.site.register(BannerList)
admin.site.register(Banner)
admin.site.register(ExploreCategories)
admin.site.register(ProductVariant)
admin.site.register(CartItem)
admin.site.register(HomeProductSection)
admin.site.register(SimilarProduct)

