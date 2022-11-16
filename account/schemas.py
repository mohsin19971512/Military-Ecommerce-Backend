from typing import Optional

from ninja import Schema
from pydantic import EmailStr, Field
from django.core.validators import RegexValidator
phone_validator = RegexValidator(r"^(((?:\+|00)964)|(0)*)7\d{9}$", "The phone number provided is invalid")

class AccountCreate(Schema):
    first_name: str
    last_name: str
    phone_number: str
    password1: str = Field(min_length=8)
    password2: str
    address1: str = None



class AccountOut(Schema):
    first_name: str
    last_name: str
    phone_number: Optional[str]
    address1: str = None
 

class TokenOut(Schema):
    access: str

class AuthOut(Schema):
    token: TokenOut
    account: AccountOut

class SigninSchema(Schema):
    phone_number: str
    password: str


class AccountUpdate(Schema):
    first_name: str
    last_name: str
    phone_number: Optional[str]
    address1: str



class ChangePasswordSchema(Schema):
    old_password: str
    new_password1: str
    new_password2: str
