from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Review, Complaint
from orders.models import Order

@login_required
def create_review(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status='completed')
    
    if Review.objects.filter(order=order).exists():
        messages.warning(request, '该订单已评价')
        return redirect('orders:my_orders')
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        content = request.POST.get('content', '')
        
        review = Review.objects.create(
            order=order,
            user=request.user,
            rating=rating,
            content=content,
        )
        if 'image' in request.FILES:
            review.image = request.FILES['image']
        review.save()
        
        messages.success(request, '🎉 评价成功！感谢您的反馈~')
        return redirect('orders:my_orders')
    
    return render(request, 'reviews/create.html', {'order': order})

@login_required
def reviews_list(request):
    if request.user.role == 'admin':
        reviews = Review.objects.all()
    else:
        reviews = Review.objects.filter(user=request.user)
    
    return render(request, 'reviews/list.html', {'reviews': reviews})

@login_required
def admin_reply_review(request, review_id):
    if request.user.role != 'admin':
        return redirect('/')
    
    review = get_object_or_404(Review, id=review_id)
    if request.method == 'POST':
        review.reply_content = request.POST.get('reply_content', '')
        review.reply_time = timezone.now()
        review.save()
        messages.success(request, '回复成功')
    
    return redirect('reviews:list')

@login_required
def create_complaint(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        title = request.POST.get('title', '')
        content = request.POST.get('content', '')
        
        complaint = Complaint.objects.create(
            user=request.user,
            order_id=order_id or None,
            title=title,
            content=content,
        )
        messages.success(request, '投诉已提交，我们将尽快处理 🙏')
        return redirect('orders:my_orders')
    
    orders = Order.objects.filter(user=request.user)
    return render(request, 'reviews/complaint.html', {'orders': orders})
