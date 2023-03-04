from django.shortcuts import render

from django.shortcuts import render, redirect, HttpResponse,HttpResponseRedirect
from .models import Customer, Product, Cart, OrderPlaced
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .serializers import ProductSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt

# Product view Code Start Here
class ProductView(View):
	def get(self, request):
		totalitem = 0
		topwears = Product.objects.filter(category='TW')
		bottomwears = Product.objects.filter(category='BW')
		mobiles = Product.objects.filter(category='M')
		if request.user.is_authenticated:
			totalitem = len(Cart.objects.filter(user=request.user))
		return render(request, 'app/home.html', {'topwears':topwears, 'bottomwears':bottomwears, 'mobiles':mobiles, 'totalitem':totalitem})
# Product view Code Ends Here

# Single Product view Code Start Here
class ProductDetailView(View):
	def get(self, request, pk):
		totalitem = 0
		product = Product.objects.get(pk=pk)
		print(product.id)
		item_already_in_cart=False
		if request.user.is_authenticated:
			totalitem = len(Cart.objects.filter(user=request.user))
			item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
		return render(request, 'app/productdetail.html', {'product':product, 'item_already_in_cart':item_already_in_cart, 'totalitem':totalitem})

# Single Product view Code Ends Here


# Add to Cart Code Starts Here

@login_required()
def add_to_cart(request):
	user = request.user
	item_already_in_cart1 = False
	product = request.GET.get('prod_id')
	item_already_in_cart1 = Cart.objects.filter(Q(product=product) & Q(user=request.user)).exists()
	if item_already_in_cart1 == False:
		product_title = Product.objects.get(id=product)
		Cart(user=user, product=product_title).save()
		messages.success(request, 'Product Added to Cart Successfully !!' )
		return redirect('/cart')
	else:
		return redirect('/cart')
  # Below Code is used to return to same page
  # return redirect(request.META['HTTP_REFERER'])

# Add to Cart Code Ends Here

# Show Cart Code Starts Here
@login_required
def show_cart(request):
	totalitem = 0
	if request.user.is_authenticated:
		totalitem = len(Cart.objects.filter(user=request.user))
		user = request.user
		cart = Cart.objects.filter(user=user)
		amount = 0.0
		shipping_amount = 70.0
		totalamount=0.0
		cart_product = [p for p in Cart.objects.all() if p.user == request.user]
		print(cart_product)
		if cart_product:
			for p in cart_product:
				tempamount = (p.quantity * p.product.discounted_price)
				amount += tempamount
				totalamount = amount+shipping_amount
			return render(request, 'app/addtocart.html', {'carts':cart, 'amount':amount, 'totalamount':totalamount, 'totalitem':totalitem})
		else:
			return render(request, 'app/emptycart.html', {'totalitem':totalitem})
	else:
		return render(request, 'app/emptycart.html', {'totalitem':totalitem})
# Show Cart Code Ends Here

#Add Quantity of Product in Cart Code Start Here
def plus_cart(request):
	if request.method == 'GET':
		prod_id = request.GET['prod_id']
		c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
		c.quantity+=1
		c.save()
		amount = 0.0
		shipping_amount= 70.0
		cart_product = [p for p in Cart.objects.all() if p.user == request.user]
		for p in cart_product:
			tempamount = (p.quantity * p.product.discounted_price)
			# print("Quantity", p.quantity)
			# print("Selling Price", p.product.discounted_price)
			# print("Before", amount)
			amount += tempamount
			# print("After", amount)
		# print("Total", amount)
		data = {
			'quantity':c.quantity,
			'amount':amount,
			'totalamount':amount+shipping_amount
		}
		return JsonResponse(data)
	else:
		return HttpResponse("")
	
#Add Quantity of Product in Cart Code Ends Here

#Subtract Quantity of Product in Cart Code Start Here


def minus_cart(request):
	if request.method == 'GET':
		prod_id = request.GET['prod_id']
		c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
		c.quantity-=1
		c.save()
		amount = 0.0
		shipping_amount= 70.0
		cart_product = [p for p in Cart.objects.all() if p.user == request.user]
		for p in cart_product:
			tempamount = (p.quantity * p.product.discounted_price)
			# print("Quantity", p.quantity)
			# print("Selling Price", p.product.discounted_price)
			# print("Before", amount)
			amount += tempamount
			# print("After", amount)
		# print("Total", amount)
		data = {
			'quantity':c.quantity,
			'amount':amount,
			'totalamount':amount+shipping_amount
		}
		return JsonResponse(data)
	else:
		return HttpResponse("")
#Subtract Quantity of Product in Cart Code Ends Here

#Cart CheckOut Code Starts Here


@login_required
def checkout(request):
	user = request.user
	add = Customer.objects.filter(user=user)
	cart_items = Cart.objects.filter(user=request.user)
	return render(request, 'app/checkout.html', {'add':add, 'cart_items':cart_items})

#Cart Checkout Code Ends Here

#Confirmation message Order Placed Code Starts here
def orderplacedpage(request):
	return render(request, 'app/orderplaced.html')

#Confirmation message Order Placed Code Ends here

#Order Placed Code Starts Here
@login_required
def payment_done(request):
	custid = request.GET.get('custid')
	print("Customer ID", custid)
	user = request.user
	cartid = Cart.objects.filter(user = user)
	customer = Customer.objects.get(id=custid)
	print(customer)
	for cid in cartid:
		OrderPlaced(user=user, customer=customer, product=cid.product, quantity=cid.quantity).save()
		print("Order Saved")
		cid.delete()
		print("Cart Item Deleted")
	return HttpResponseRedirect("/orderplaced/")
#Order Placed Code Ends Here

#Remove Product from Cart Code starts Here
def remove_cart(request):
	if request.method == 'GET':
		prod_id = request.GET['prod_id']
		c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
		c.delete()
		amount = 0.0
		shipping_amount= 70.0
		cart_product = [p for p in Cart.objects.all() if p.user == request.user]
		for p in cart_product:
			tempamount = (p.quantity * p.product.discounted_price)
			# print("Quantity", p.quantity)
			# print("Selling Price", p.product.discounted_price)
			# print("Before", amount)
			amount += tempamount
			# print("After", amount)
		# print("Total", amount)
		data = {
			'amount':amount,
			'totalamount':amount+shipping_amount
		}
		return JsonResponse(data)
	else:
		return HttpResponse("")
#Remove Product from Cart Code Ends Here

#Customer Address Code starts Here
@login_required
def address(request):
	totalitem = 0
	if request.user.is_authenticated:
		totalitem = len(Cart.objects.filter(user=request.user))
	add = Customer.objects.filter(user=request.user)
	return render(request, 'app/address.html', {'add':add, 'active':'btn-primary', 'totalitem':totalitem})
#Customer Address Code Ends Here

#Orders That placed by Customer Code starts Here
@login_required
def orders(request):
	op = OrderPlaced.objects.filter(user=request.user)
	return render(request, 'app/orders.html', {'order_placed':op})
# #Orders That placed by Customer Code Ends Here

#Filter for Products Code Starts From Here
#Mobile Filter
def mobile(request, data=None):
	totalitem = 0
	if request.user.is_authenticated:
		totalitem = len(Cart.objects.filter(user=request.user))
	if data==None :
			mobiles = Product.objects.filter(category='M')
	elif data == 'Redmi' or data == 'Samsung':
			mobiles = Product.objects.filter(category='M').filter(brand=data)
	elif data == 'below':
			mobiles = Product.objects.filter(category='M').filter(discounted_price__lt=10000)
	elif data == 'above':
			mobiles = Product.objects.filter(category='M').filter(discounted_price__gt=10000)
	return render(request, 'app/mobile.html', {'mobiles':mobiles, 'totalitem':totalitem})
#Topwear Filter
def topwear(request,data=None):
    if data == None:
        topwears=Product.objects.filter(category='TW')
    elif data == 'Adidas' or data == 'Zara':
        topwears=Product.objects.filter(category='TW').filter(brand=data)
    elif data == 'Below':
        topwears=Product.objects.filter(category='TW').filter(selling_price__lt=500)
    elif data == 'Above':
        topwears=Product.objects.filter(category='TW').filter(selling_price__gt=500)

    return render(request,'app/Topwear.html',{'topwears':topwears})
#BottomWear Filter
def bottomwear(request,data=None):
    if data == None:
        bottomwears=Product.objects.filter(category='BW')
    elif data == 'Lee' or data == 'Spykar':
        bottomwears=Product.objects.filter(category='BW').filter(brand=data)
    elif data == 'Below':
        bottomwears=Product.objects.filter(category='BW').filter(selling_price__lt=1500)
    elif data == 'Above':
        bottomwears=Product.objects.filter(category='BW').filter(selling_price__gt=1500)

    return render(request,'app/bottomwear.html',{'bottomwears':bottomwears})

#Filter for Products Code Ends  Here

#Customer Signup or Registraion Code Starts from Here
class CustomerRegistrationView(View):
 def get(self, request):
  form = CustomerRegistrationForm()
  return render(request, 'app/customerregistration.html', {'form':form})
  
 def post(self, request):
  form = CustomerRegistrationForm(request.POST)
  if form.is_valid():
   messages.success(request, 'Congratulations!! Registered Successfully.')
   form.save()
  return render(request, 'app/customerregistration.html', {'form':form})
#Customer Signup or Registraion Code Ends Here

#Customer Profile view Code Starts here
@method_decorator(login_required, name='dispatch')
class ProfileView(View):
	def get(self, request):
		totalitem = 0
		if request.user.is_authenticated:
			totalitem = len(Cart.objects.filter(user=request.user))
		form = CustomerProfileForm()
		return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary', 'totalitem':totalitem})
		
	def post(self, request):
		totalitem = 0
		if request.user.is_authenticated:
			totalitem = len(Cart.objects.filter(user=request.user))
		form = CustomerProfileForm(request.POST)
		if form.is_valid():
			usr = request.user
			name  = form.cleaned_data['name']
			locality = form.cleaned_data['locality']
			city = form.cleaned_data['city']
			state = form.cleaned_data['state']
			zipcode = form.cleaned_data['zipcode']
			reg = Customer(user=usr, name=name, locality=locality, city=city, state=state, zipcode=zipcode)
			reg.save()
			messages.success(request, 'Congratulations!! Profile Updated Successfully.')
		return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary', 'totalitem':totalitem})
#Customer Profile view Code Ends here

#Cancel Order Code start Here
def deleteproduct(request,num):
	user=request.user
	op = OrderPlaced.objects.get(id=num,user=user)
	if request.user.is_authenticated:
		op.delete()
	return redirect("/orders")	

#Products API Code Start Here
@csrf_exempt
@api_view(['GET','POST','PUT','PATCH','DELETE'])
def Product_api(request,pk=None):
	if request.method == 'GET':
		id = pk
		if id is not None:
			pro = Product.objects.get(id=id)
			serializer = ProductSerializer(pro)
			return Response(serializer.data)
		pro=Product.objects.all()
		serializer = ProductSerializer(pro,many=True)
		return Response(serializer.data)
	
	if request.method == 'POST':
		serializer = ProductSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response({'msg':'Data Created'})
		return Response(serializer.errors)
	
	if request.method == 'PUT':
		id = pk
		pro=Product.objects.get(pk=id)
		serializer=ProductSerializer(pro,data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response({'msg':' Complete Data Updated'})
		return Response(serializer.errors)
	
	if request.method=='PATCH':
		id = pk
		pro=Product.objects.get(pk=id)
		serializer=ProductSerializer(pro,data=request.data,partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response({'msg':'Partial Data Updated'})
		return Response(serializer.errors)
	
	if request.method =='DELETE':
		id = pk
		pro = Product.objects.get(pk=id)
		pro.delete()
		return Response({'msg':'Data Deleted'})

