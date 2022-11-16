from typing import List

from ninja import ModelSchema, Schema
from ninja.orm import create_schema
from pydantic import UUID4

from commerce.models import Product, Merchant
from .models import Category

import datetime



class UUIDSchema(Schema):
    id: UUID4


# ProductSchemaOut = create_schema(Product, depth=2)
#ProductSchemaOutCat = create_schema(Category, depth=1) self refernce with many to many 


class VendorOut(UUIDSchema):
    name: str
    image: str


class LabelOut(UUIDSchema):
    name: str


class MerchantOut(ModelSchema):
    class Config:
        model = Merchant
        model_fields = ['id', 'name']


class ProductTypeOut(Schema):
    id : UUID4
    name : str

class CategoryOut(Schema):
    id : UUID4
    types: List[ProductTypeOut] = None
    name: str= None
    description: str= None
    image: str = None
    is_active : bool = None
    


CategoryOut.update_forward_refs()

class Size_Out(Schema) :
    id : UUID4 = None
    size : str = None

class ProductImageOut(Schema) :
    image : str = None
class ProductOut(ModelSchema):
    label: LabelOut
    category: CategoryOut
    product_type : ProductTypeOut = None
    product_size : list[Size_Out] 
    img : list[ProductImageOut] 


    class Config:
        model = Product
        model_fields = ['id',
                        'name',
                        'description',
                        'img',
                        'qty',
                        'price',
                        'discounted_price',
                        'category',
                        'product_type',
                        'label',


                        ]


# class ProductManualSchemaOut(Schema):
#     pass


class CitySchema(Schema):
    name: str


class CitiesOut(CitySchema, UUIDSchema):
    pass


class ItemSchema(Schema):
    # user:
    id : UUID4
    product: ProductOut
    item_qty: int
    ordered: bool
    item_total : str = None
    item_size : Size_Out = None


class ItemCreate(Schema):
    product_id: UUID4
    item_qty: int
    item_size_id : UUID4 = None


class ItemOut(UUIDSchema, ItemSchema):
    total_price : str = None


class OrderOut(UUIDSchema) :
    total  : int = None
    note : str = None
    ordered : bool
    items : List[ItemSchema]
    ref_code : str = None

class OrderSchemaOut(UUIDSchema) :
    id: UUID4
    note : str = None
    ordered : bool = None
    total_items : str = None
    total_price : str = None
    created : datetime.datetime = None


class AddressOut(UUIDSchema):
    id : UUID4
    work_address : bool = None
    address1 : str 
    address2 : str = None
    phone : str 


class AddressIn(Schema):
    work_address : bool = None
    address1 : str
    address2 : str 
    city : str  = None
    phone : str
    note : str = None

class TotalPriceOut(Schema):
    total_price : str  
    total_items : str = None 

class CartSchemaOut(Schema):
    items :List[ItemSchema] = None
    total_price : TotalPriceOut = None


