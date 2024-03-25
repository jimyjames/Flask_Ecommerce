from pydantic import BaseModel
from typing import List
from .models import ProductDescription



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










    
