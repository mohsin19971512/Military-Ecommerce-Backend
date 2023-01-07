from django.contrib import admin

from commerce.models import Product, Order, Item, Address, OrderStatus, ProductImage, Category, ProductSize, Vendor, Merchant,Size, \
    Label,ProductType
from django.utils.html import format_html
admin.site.register(Item)
admin.site.register(Address)
admin.site.register(OrderStatus)
admin.site.register(ProductImage)
admin.site.register(Category)
admin.site.register(Vendor)
admin.site.register(Merchant)
admin.site.register(Label)
admin.site.register(ProductSize)
admin.site.register(Size)

admin.site.register(ProductType)

from django.urls import reverse

@admin.register(Order)
class Orderadmin(admin.ModelAdmin):
    list_display = ("user","link_to_address","total_items","total_price","note","ordered","status")
    def link_to_address(self, obj):
        link = reverse("admin:commerce_address_change", args=[obj.address_id])
        return format_html('<a href="{}">{}</a>', link, obj.address)
    link_to_address.short_description = 'Address'
    list_filter = ("status__title","ordered")
    search_fields =["ordered","status__title"]

@admin.register(Product)
class Orderadmin(admin.ModelAdmin):
    def picture(self, obj):
        return format_html('<img style="width:50px; height:50px; border-radius: 50%;" src="{}" />'.format(obj.img.all()[0].image.url))



    def cqty(self, obj):
        color = 'white'
        if obj.qty <= 5:
            color = 'red'
        return format_html('<b style="color:{};">{}</b>',color,obj.qty)


    picture.short_description = 'picture'
    cqty.short_description = 'الكمية'

    list_display = ("name","cqty","cost","price","discounted_price","category","product_type","is_active","label","picture")

    list_filter = ("qty","name")
    search_fields =["name","price","is_active"]
