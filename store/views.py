from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import Product, Category, Order, OrderItem
from .forms import RegisterForm, LoginForm


# =========================
# HOME
# =========================

def home(request):
    query = request.GET.get("q")
    category = request.GET.get("category")

    products = Product.objects.all()
    categories = Category.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if category:
        products = products.filter(category__name__iexact=category)

    return render(request, "Store/home.html", {
        "products": products,
        "categories": categories,
    })


# =========================
# ADD TO CART
# =========================

def add_to_cart(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    request.session["cart"] = cart
    request.session.modified = True

    # Buy Now → Cart
    if request.GET.get("next") == "cart":
        return redirect("cart")

    # Add to Cart → Home
    return redirect("home")


# =========================
# CART
# =========================

def cart(request):

    cart_data = request.session.get("cart", {})

    products = []
    total = 0

    for product_id, quantity in cart_data.items():

        product = get_object_or_404(
            Product,
            id=product_id
        )

        subtotal = product.price * quantity
        total += subtotal

        products.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal
        })

    return render(request, "Store/cart.html", {
        "products": products,
        "total": total
    })


# =========================
# INCREASE QUANTITY
# =========================

def increase_quantity(request, product_id):

    cart = request.session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


# =========================
# DECREASE QUANTITY
# =========================

def decrease_quantity(request, product_id):

    cart = request.session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:

        cart[product_id] -= 1

        if cart[product_id] <= 0:
            del cart[product_id]

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


# =========================
# REMOVE FROM CART
# =========================

def remove_from_cart(request, product_id):

    cart = request.session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


# =========================
# CHECKOUT
# =========================

def checkout(request):

    cart_data = request.session.get("cart", {})

    if not cart_data:
        return redirect("home")

    products = []
    total = 0

    for product_id, quantity in cart_data.items():

        product = get_object_or_404(
            Product,
            id=product_id
        )

        subtotal = product.price * quantity
        total += subtotal

        products.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal
        })

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        city = request.POST.get("city")
        pincode = request.POST.get("pincode")
        payment_method = request.POST.get("payment_method")

        # Create order
        order = Order.objects.create(
    name=name,
    email=email,
    phone=phone,
    address=address,
    city=city,
    pincode=pincode,
    payment_method=payment_method,
    total=total
)

        # Create order items
        for item in products:

            OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["quantity"],
                price=item["product"].price
            )

        # Empty cart
        request.session["cart"] = {}
        request.session.modified = True

        return render(
            request,
            "Store/order_success.html",
            {
                "name": name,
                "email": email,
                "phone": phone,
                "address": address,
                "city": city,
                "pincode": pincode,
                "products": products,
                "total": total,
                "order_id": order.id
            }
        )

    return render(
        request,
        "Store/checkout.html",
        {
            "products": products,
            "total": total
        }
    )


# =========================
# PRODUCT DETAILS
# =========================

def product_detail(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    return render(
        request,
        "Store/product_detail.html",
        {
            "product": product
        }
    )


# =========================
# REGISTER
# =========================

def register(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            return redirect("home")

    else:

        form = RegisterForm()

    return render(
        request,
        "Store/register.html",
        {
            "form": form
        }
    )


# =========================
# LOGIN
# =========================

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("home")

        else:

            return render(
                request,
                "Store/login.html",
                {
                    "error": "Invalid username or password"
                }
            )

    return render(
        request,
        "Store/login.html"
    )


# =========================
# LOGOUT
# =========================

def logout_view(request):

    logout(request)

    return redirect("home")


# =========================
# LOGIN USING FORM
# =========================

def user_login(request):

    if request.method == "POST":

        form = LoginForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:

                login(request, user)

                next_url = request.GET.get("next")

                if next_url:
                    return redirect(next_url)

                return redirect("home")

    else:
        form = LoginForm()

    return render(request, "Store/login.html", {
        "form": form
    })

@login_required
def my_orders(request):

    orders = Order.objects.filter(
        email=request.user.email
    ).order_by("-created_at")

    return render(
        request,
        "Store/my_orders.html",
        {
            "orders": orders
        }
    )
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-id")

    return render(request, "Store/my_orders.html", {
        "orders": orders
    })
@login_required
def my_orders(request):
    orders = Order.objects.all().order_by("-created_at")

    return render(request, "Store/my_orders.html", {
        "orders": orders
    })