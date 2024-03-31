from pydantic import BaseModel
from typing import List, Optional
from .models import ProductDescription
from datetime import datetime

class Userdetails(BaseModel): 
    id : int
    phone : int
    county :str
    town :str
    dob :datetime
    gender :str
    companyname :str
    address :str

class Userbase(BaseModel):
    name : str
    username : str
    email : str
class Userin(Userbase):
  
    password : str

class Userout(Userbase):
    id : int
    profile : str
    created_at :datetime
    phone : Optional[int]
    county :Optional[str]
    town :Optional[str]
    dob :Optional[datetime]
    gender :Optional[str]
    companyname :Optional[str]
    address :Optional[str]


    class Config:
        from_attributes=True

class ProductDescriptionin(BaseModel):

    title : str 
    description : str


class Productdescriptionout(BaseModel):
    title: str
    description: str
    class Config:
        from_attributes=True
    

    


class Productin(BaseModel):
    name : str
    description  : str
    category : str
    price : float
    detail: List[ProductDescriptionin]

    
class Productout(Productin):
    id:int
    detail:List[Productdescriptionout]=[]
    class Config:
        from_attributes=True


class Orderin(BaseModel):
    customer : int
    product_id : int 
    quantity : int
   
class Orderout(Orderin):
    id : int
    total_price : float
   
    class Config :
        from_attributes=True

class Testlogin(BaseModel):
    email : str
    password : str











    
