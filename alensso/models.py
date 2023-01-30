from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100,unique=True,blank=False,null=False)
    img = models.ImageField(upload_to='category/',null=True,blank=True)

    def __str__(self):
        return self.name
    

    @staticmethod
    def get_all_category():
        return Category.objects.all()


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.IntegerField()
    bio = models.TextField(null=True,blank=True)
    pics = models.ImageField(upload_to='products/', null=True,blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True,blank=True)
    view = models.BooleanField(default = False)
    date_added = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name

    @staticmethod
    def get_product_byId(id):
        return Product.objects.get(pk = id) 

    @staticmethod
    def get_all_products():
        return Product.objects.all()
  
    @staticmethod
    def get_all_products_by_categoryid(category_id):
        if category_id:
            return Product.objects.filter(category=category_id)
        else:
            return Product.get_all_products()

    @staticmethod
    def get_specific_products():
        return Product.objects.filter(view = True)

Status = (
    ('O','Ordered'),
    ('C', 'Checked Out'),
    ('P', 'Pending To Arrive'),
    ('D','Delivered')
)

class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    order_date = models.DateTimeField(default=timezone.now)
    status= models.CharField(max_length=20,choices=Status,null=True,blank=True,default='O')

    def __str__(self):
        return str(self.product)
    
    @staticmethod
    def add_product_quantity(product,user):
        order,created = Order.objects.get_or_create(product=product,user= user)
        if order.quantity <= 0:
            order.quantity = 1
        else:
            order.quantity += 1
        order.save()
        
    @staticmethod
    def remove_product_quantity(product,user):
        if Order.objects.get(product=product,user=user):
            order = Order.objects.get(product=product,user=user)
            order.quantity -= 1
            order.save()
        while order.quantity <= 0:
            order.delete()

    @staticmethod
    def delete_product(product,user):
        if Order.objects.get(product=product,user=user):
            order = Order.objects.get(product=product,user=user)
            order.delete()

    @staticmethod
    def get_full_amount(user):
        order = Order.objects.filter(user=user)
        amount = 0
        for each in order:
            amount += each.quantity*each.product.price
        return amount

    
    @staticmethod
    def get_total_amount(user):
        amount = Order.get_full_amount(user)
        if amount != 0:
            amount += 70
        return amount


    @staticmethod
    def get_cart_total(user):
        order = Order.objects.filter(user= user)
        cart = 0
        for each in order:
            cart += each.quantity
        return cart