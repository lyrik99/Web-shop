from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import ProductUploadForm
from django.contrib import messages
from .models import Product

def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/product_list.html', {'products': products})

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'shop/product_detail.html', {'product': product})

@login_required
def upload_product(request):
    if request.method == 'POST':
        form = ProductUploadForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user  # Привязываем товар к пользователю
            product.save()
            messages.success(request, 'Товар успешно загружен!')
            return redirect('product_list')
    else:
        form = ProductUploadForm()
    return render(request, 'shop/upload_product.html', {'form': form})