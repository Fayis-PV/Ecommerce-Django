from django.urls import path
from . import views

# Create alensso urls
app_name = 'alensso'
urlpatterns = [
    path("", views.home, name="home"),
    path('add_to_cart/<int:id>',views.AddtoCartView.as_view(), name= 'addtocart'),
    path("staff/view_product/<int:id>", views.ProductView.as_view(), name="staffviewproduct"),
    path("cart/", views.CartView.as_view(), name="cart"),
    path("checkout/", views.EpaymentView.as_view(), name="checkout"),
    path("e_payment/", views.EpaymentView.as_view(), name="epayment"),
    path("paymenthandler/", views.paymenthandler, name="paymenthandler"),

    path("login/", views.LoginUser.as_view(), name="login"),
    path("signup/", views.Signupuser.as_view(), name="signup"),
    path("logout", views.LogoutUser.as_view(), name="logout"),

    path("staff", views.Admin.as_view(), name="staff"),
    path("staff/add_product", views.AddProduct.as_view(), name="staffaddproduct"),
    path("staff/add_category/", views.AddCategory.as_view(), name="staffaddcategory"),
    # path("place_order/",views.place_order, name="place_order")

]
