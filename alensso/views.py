from django.shortcuts import render,redirect
from django.http import HttpResponseBadRequest,HttpResponse,HttpResponseRedirect
from .models import Product,Category
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout,authenticate
from .forms import *
from django.views import View
from django.contrib import messages
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
cart = Order.get_cart_total(user=None)
razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID,settings.RAZOR_KEY_SECRET))

def home(req):
    user = None
    if req.user:
        user = req.user
    
    view_categories = Category.get_all_category()
    view_special_products = Product.get_specific_products()

    context = {
        'view_categories': view_categories,
        'user': user,
        'cart':cart
    }
    return render(req,'app/home.html',context)


class AddtoCartView(View):
    def get(self,req,id):
        try:
            product = Product.objects.get(pk = id)
            user = req.user
            Order.add_product_quantity(product,user)
            global cart 
            cart = Order.get_cart_total(user)
            return HttpResponseRedirect(req.META.get('HTTP_REFERER'))
        except Exception as e:
            print(e)
            messages.error(req,str(e))
            return redirect('/')


class CartView(View):
    def get(self,req):
        try:
            user = req.user
            try:
                products = Order.objects.filter(user = user)
                amount = Order.get_full_amount(user)
                total_amount = Order.get_total_amount(user)
                return render(req,'app/addtocart.html',{'products':products,'amount':amount,'total_amount':total_amount,'cart':cart})
            except Exception as e:
                print(e)
                products = {}
                total_amount = 0
                amount = 0
                return render(req,'app/addtocart.html',{'products':products,'amount':amount,'total_amount':total_amount,'cart':cart})
        except Exception as e:
            print(e)
            products = {}
            total_amount = 0
            amount = 0
            return render(req,'app/addtocart.html',{'products':products,'amount':amount,'total_amount':total_amount,'cart':cart})


class EpaymentView(View):
    def get(self,req):
        try:
            user = req.user
            products = Order.objects.filter(user = user)
            full_amount = Order.get_full_amount(user)
            total_amount = Order.get_total_amount(user)
            razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID,settings.RAZOR_KEY_SECRET))
            amount = total_amount*100
            currency = 'INR'
            razorpay_order = razorpay_client.order.create(dict(amount = amount,currency= currency,payment_capture='0'))

            # order id of newly created order.
            razorpay_order_id = razorpay_order['id']
            callback_url = 'paymenthandler/'

            context = {'razorpay_order_id':razorpay_order_id,'razorpay_merchant_key' : settings.RAZOR_KEY_ID,'razorpay_amount':amount,'currency': currency,'callback_url': callback_url,'products':products,'total_amount':total_amount,'full_amount':full_amount}
            # context['razorpay_order_id'] = razorpay_order_id
            # context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
            # context['razorpay_amount'] = amount
            # context['currency'] = currency
            # context['callback_url'] = callback_url
            print(context)
            return render(req, 'app/checkout.html', context)
        except Exception as e:
            print(e)
            products = {}
            total_amount = 0
            amount = 0
            return render(req,'app/checkout.html',{'products':products,'amount':amount,'total_amount':total_amount,'cart':cart})
            
# we need to csrf_exempt this url as
# POST request will be made by Razorpay
# and it won't have the csrf token.
@csrf_exempt
def paymenthandler(request):
 
    # only accept POST request.
    if request.method == "POST":
        try:
           
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
 
            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            if result is not None:
                amount = 1000  # Rs. 10
                try:
 
                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)
 
                    # render success page on successful caputre of payment
                    return render(request, 'paymentsuccess.html')
                except:
 
                    # if there is an error while capturing payment.
                    return render(request, 'paymentfail.html')
            else:
 
                # if signature verification fails.
                return render(request, 'paymentfail.html')
        except:
 
            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:
       # if other than POST request is made.
        return HttpResponseBadRequest()

class LoginUser(View):
    def get(self,req):
        form = LoginUserForm()
        return render(req,'app/login.html',{'form':form,'cart':cart})

    def post(self,req):
        form = LoginUserForm(req.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            if User.objects.filter(username = username):
                user = User.objects.get(username = username)
                if user.check_password(password):
                    user = authenticate(req, username = username, password = password)
                    if user is not None:
                        login(req, user)
                        return redirect('/')
                else:
                    messages.error(req,'Invalid Credentials')
                    return redirect('/login')
            else:
                messages.error(req,'User is not found. Please continue with a new account')
                return redirect('/login')



class LogoutUser(View):
    def get(self,req):
        logout(req)
        return redirect('/login')


class Signupuser(View):
    def get(self,req):
        form = CustomerForm()
        return render(req,'app/signup.html',{'form':form,'cart':cart})

    def post(self,req):
        form = CustomerForm(req.POST)
        if form.is_valid():
            form.save()
            return redirect('/login')
        else:
            print(form.errors)
            return render(req,'app/signup.html',{'form':form,'cart':cart})


# @login_required(login_url='/login')
class Admin(View):
    def get(self,req):
        products = Product.objects.all()
        print(products)
        context = {'products':products,'cart':cart}
        return render(req,'app/admin.html',context)


# @login_required(login_url='/login')
class AddProduct(View):
    def get(self,req):
        form = ProductForm()
        context = {'form':form,'cart':cart}
        return render(req,'app/addproduct.html',context)
    
    def post(self,req):
        form = ProductForm(req.POST,req.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            category = form.cleaned_data['category']
            price = form.cleaned_data['price']
            bio = form.cleaned_data['bio']
            img = form.cleaned_data['pics']
            view = form.cleaned_data['view']
            print(form.cleaned_data)
            product = Product.objects.create(name = name, category = category, price = price, bio = bio,pics = img, view = view)
            message = 'New product '+product.name+' is added to '+str(product.category)
            messages.success(req,message)
            return redirect('/staff/add_product')
        else:
            print(form.errors)
            messages.error(req,'Invalid Data. Please Check again')
        context = {'form':form,'cart':cart}
        return render(req,'app/addproduct.html',context)
        
class ProductView(View):
    def get(self,req,id):
        try:
            product = Product.objects.get(pk = id)
            return render(req,'app/productdetail.html',{'product':product,'cart':cart})
        except:
            product = {}
            messages.error(req,'Product not found.Please add the Product')
            return render(req,'app/productdetail.html',{'product':product,'cart':cart})


class AddCategory(View):
    def get(self,req):
        form = CategoryForm()
        categories = Category.objects.all()
        print(categories)
        return render(req,'app/addcategory.html',{'form':form,'categories':categories})
    
    def post(self,req):
        form = CategoryForm(req.POST,req.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            img = form.cleaned_data['img']
            Category.objects.create(name= name, img = img)
            messages.success(req,'New Category '+name+' added Successfully!')
            return HttpResponseRedirect(req.META.get('HTTP_REFERER'))
        else:
            messages.error(req,'Something went wrong. Please try again')
            return HttpResponseRedirect(req.META.get('HTTP_REFERER'))
