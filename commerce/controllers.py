import random
import string
from typing import List
from django.contrib import auth

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router
from pydantic import UUID4

from account.authorization import GlobalAuth
from commerce.models import Address, Product, Category, ProductSize, Vendor, Item, Order, OrderStatus, ProductType
from commerce.schemas import AddressIn, OrderSchemaOut, CartSchemaOut, ProductTypeOut, ProductOut, VendorOut, ItemOut, ItemCreate, CategoryOut
from config.utils.schemas import MessageOut
import string
import random

products_controller = Router(tags=['products'])
vendor_controller = Router(tags=['vendors'])
order_controller = Router(tags=['orders'])
checkout_controller = Router(tags=['checkout'])
category_controllers = Router(tags=['Category'])


User = get_user_model()


@vendor_controller.get('', response=List[VendorOut])
def list_vendors(request):
    return Vendor.objects.all()


@products_controller.get('', response={
    200: List[ProductOut],
    404: MessageOut
})
def list_products(
        request, *,
        q: str = None,
        price_from: int = None,
        price_to: int = None,
):
    products_qs = Product.objects.filter(
        is_active=True).select_related('category', 'label')

    if not products_qs:
        return 404, {'detail': 'No products found'}

    if q:
        products_qs = products_qs.filter(
            Q(name__icontains=q) | Q(description__icontains=q)
        )

    if price_from:
        products_qs = products_qs.filter(discounted_price__gte=price_from)

    if price_to:
        products_qs = products_qs.filter(discounted_price__lte=price_to)

    return products_qs


@products_controller.get('products/{product_id}', response={
    200: ProductOut,
    404: MessageOut
})
def productDetails(request, product_id: UUID4):
    try:
        products_qs = Product.objects.get(id=product_id)

    except products_qs.DoesNotExist:
        return 404, {'detail': 'No products found'}

    return products_qs


@order_controller.get('cart', auth=GlobalAuth(), response={
    200: List[ItemOut],
    404: MessageOut
})
def view_cart(request):
    user = get_object_or_404(User, id=request.auth['pk'])
    cart_items = Item.objects.filter(user=user, ordered=False)
    total_Price = sum(i.item_total for i in cart_items)
    ItemOut.total_price = total_Price
    if cart_items:
        return cart_items

    return 404, {'detail': 'Your cart is empty, go shop like crazy!'}


@order_controller.post('add-to-cart', auth=GlobalAuth(), response={
    200: MessageOut,
    # 400: MessageOut
})
def add_update_cart(request, item_in: ItemCreate):
    try:
        user = get_object_or_404(User, id=request.auth['pk'])
        
        if item_in.item_size_id:
            product_size = ProductSize.objects.get(id=item_in.item_size_id)
            item = Item.objects.get(
                product_id=item_in.product_id, user=user, item_size=product_size,ordered=False)
            item.item_qty += 1
        else:
            item = Item.objects.get(
                product_id=item_in.product_id, user=user,ordered=False)
            item.item_qty += 1
        #item_exist = Item.objects.get(product_id=item_in.product_id,user=user)

    except Item.DoesNotExist:
        if item_in.item_size_id:
            product_size = ProductSize.objects.get(id=item_in.item_size_id)
            Item.objects.create(**item_in.dict(), item_size=product_size, ordered=False,user=user)
        else:    
            Item.objects.create(**item_in.dict(), ordered=False,user=user)

    return 200, {'detail': 'Added to cart successfully'}


@order_controller.post('item/{id}/reduce-quantity', auth=GlobalAuth(), response={
    200: MessageOut,
})
def reduce_item_quantity(request, id: UUID4):
    user = get_object_or_404(User, id=request.auth['pk'])
    item = get_object_or_404(Item, id=id, user=user)
    if item.item_qty <= 1:
        item.delete()
        return 200, {'detail': 'Item deleted!'}
    item.item_qty -= 1
    item.save()

    return 200, {'detail': 'Item quantity reduced successfully!'}


@order_controller.delete('/item/{id}', auth=GlobalAuth(), response={
    204: MessageOut
})
def delete_item(request, id: UUID4):
    user = get_object_or_404(User, id=request.auth['pk'])

    item = get_object_or_404(Item, id=id, user=user)
    item.delete()

    return 204, {'detail': 'Item deleted!'}


def generate_ref_code():
    return ''.join(random.sample(string.ascii_letters + string.digits, 6))


@order_controller.post('/item/{id}/increase-quantity', auth=GlobalAuth(), response={200: MessageOut, })
def increase_item_quantity(request, id: UUID4):
    user = get_object_or_404(User, id=request.auth['pk'])
    item = get_object_or_404(Item, id=id, user=user, ordered=False)
    item.item_qty += 1
    item.save()
    return 200, {'detail': 'item increased successfully'}


@order_controller.post('create-order', auth=GlobalAuth(), response={200: MessageOut, 201: MessageOut})
def create_update_order(request, address_in: AddressIn):
    # set ref_code to a randomly generated 6 alphanumeric value
    ref_code = ''.join(random.sample(string.ascii_letters+string.digits, 6))
    # get status
    try:
        get_status = OrderStatus.objects.get(title="NEW")
    except OrderStatus.DoesNotExist:
        get_status = OrderStatus.objects.create(title="NEW", is_default=True)
    user = get_object_or_404(User, id=request.auth['pk'])
    address_qs = Address(work_address=address_in.work_address, address1=address_in.address1,
                         address2=address_in.address2, phone=address_in.phone, user=user)
    address_qs.save()

    # take all current items (ordered=False)

    items_qs = Item.objects.filter(user=user, ordered=False)
    total_price = sum(i.item_total for i in items_qs)
    total_items = sum(i.item_qty for i in items_qs)
    print("items_qs", items_qs)
    #order = Order.objects.get(user=user,ordered = False)
    # print("order",order)
    order_qs = Order.objects.filter(user=user, ordered=False)

    print("order_qs", order_qs)
    if order_qs:
        items_qs.update(ordered=True)
        order_qs.first().ordered = True
        order_qs.first().total_items = total_items
        order_qs.first().total_price = total_price

        return 200, {"detail": "Order Updated Successfully"}
    else:
        order = Order.objects.create(user=user, total_items=total_items, total_price=total_price,
                                     status=get_status, ref_code=ref_code, ordered=True, note=address_in.note, address=address_qs)
        order.items.add(*items_qs)
        items_qs.update(ordered=True)

        return 201, {"detail": "Order Created Successfully"}


@order_controller.get('total-price', auth=GlobalAuth(), response={200: CartSchemaOut, 404: MessageOut})
def un_complete_order(request):
    user = get_object_or_404(User, id=request.auth['pk'])
    if user:

        cart_items = Item.objects.filter(
            user=user, ordered=False).select_related("product", "item_size")

        total_price = sum(i.item_total for i in cart_items)
        total_items = sum(i.item_qty for i in cart_items)
        CartSchemaOut.total_price = {
            "total_items": total_items, "total_price": total_price}
        CartSchemaOut.items = cart_items
    else:
        return 404, {"detail": "Your cart is Empty"}

    return 200, CartSchemaOut


@order_controller.get('completed-order', auth=GlobalAuth(), response={200: list[OrderSchemaOut], 404: MessageOut})
def completed_order(request):
    user = get_object_or_404(User, id=request.auth['pk'])
    status = OrderStatus.objects.get(title="COMPLETED")
    order = Order.objects.filter(ordered=True, status=status)
    if user and order:
        return 200, order

    else:
        return 404, {"detail": "Your cart is Empty"}


@checkout_controller.post('/create/', auth=GlobalAuth(), response={200: MessageOut, 404: MessageOut})
def checkout(request, address_in: AddressIn, note: str = None):
    # crete city
    user = get_object_or_404(User, id=request.auth['pk'])
    # create address
    address_qs = Address(**address_in.dict(), user=user)
    address_qs.save()
    # get Order
    try:
        checkout = Order.objects.get(ordered=False, user=user)
    except Order.DoesNotExist:
        return 404, {'detail': 'Order Not Found'}

    # get note if exist
    if note:
        checkout.note = note

    checkout.status = OrderStatus.objects.get(title="PROCESSING")
    checkout.total = checkout.order_total
    checkout.ordered = True
    checkout.address = address_qs
    checkout.save()
    return 200, {'detail': 'Checkout Created successfully'}


@category_controllers.get('categories', response=List[CategoryOut])
def list_categories(request):
    return Category.objects.all()


@category_controllers.get('categories/{category_id}', response=List[ProductTypeOut])
def category_products(request, category_id: UUID4):
    types = Category.objects.get(id=category_id).types.all()
    return types


@category_controllers.get('category/{category_id}/{type_id}', response=List[ProductOut])
def products_category_type(request, category_id: UUID4, type_id: UUID4):
    products = Product.objects.filter(category=Category.objects.get(
        id=category_id), product_type=ProductType.objects.get(id=type_id))
    return products
