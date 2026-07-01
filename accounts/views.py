from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone
from .models import User, LoginLog

def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('dashboard:index')
        return redirect('/')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if user is locked
        try:
            user = User.objects.get(username=username)
            if user.locked_until and user.locked_until > timezone.now():
                remaining = (user.locked_until - timezone.now()).seconds // 60
                messages.error(request, f'账号已锁定，请{remaining}分钟后再试')
                return render(request, 'accounts/login.html')
        except User.DoesNotExist:
            pass
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active:
                messages.error(request, '账号已被禁用')
                return render(request, 'accounts/login.html')
            
            login(request, user)
            user.login_attempts = 0
            user.locked_until = None
            user.save()
            
            LoginLog.objects.create(user=user, is_success=True)
            
            if user.role == 'admin':
                return redirect('dashboard:index')
            elif user.role == 'technician':
                return redirect('orders:technician_orders')
            else:
                next_url = request.GET.get('next', '/')
                return redirect(next_url)
        else:
            LoginLog.objects.create(is_success=False)
            # Record login attempt
            try:
                user_obj = User.objects.get(username=username)
                user_obj.login_attempts += 1
                if user_obj.login_attempts >= 5:
                    user_obj.locked_until = timezone.now() + timezone.timedelta(minutes=10)
                    messages.warning(request, '密码错误次数过多，账号已锁定10分钟')
                else:
                    messages.error(request, f'用户名或密码错误，还可尝试{5 - user_obj.login_attempts}次')
                user_obj.save()
            except User.DoesNotExist:
                messages.error(request, '用户名或密码错误')
    
    return render(request, 'accounts/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone')
        nickname = request.POST.get('nickname')
        
        if password != password2:
            messages.error(request, '两次密码输入不一致')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
            return render(request, 'accounts/register.html')
        
        if phone and User.objects.filter(phone=phone).exists():
            messages.error(request, '手机号已被注册')
            return render(request, 'accounts/register.html')
        
        user = User.objects.create_user(
            username=username,
            password=password,
            phone=phone,
            nickname=nickname or username,
            role='customer'
        )
        messages.success(request, '🎉 注册成功！欢迎加入萌宠洗护大家庭！')
        login(request, user)
        return redirect('/')
    
    return render(request, 'accounts/register.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, '已安全退出')
    return redirect('accounts:login')

@login_required
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        user.nickname = request.POST.get('nickname', user.nickname)
        user.phone = request.POST.get('phone', user.phone)
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        user.save()
        messages.success(request, '个人信息已更新 ✨')
        return redirect('accounts:profile')
    return render(request, 'accounts/profile.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password2 = request.POST.get('new_password2')
        
        if not request.user.check_password(old_password):
            messages.error(request, '原密码不正确')
        elif new_password != new_password2:
            messages.error(request, '新密码两次输入不一致')
        elif len(new_password) < 6:
            messages.error(request, '新密码长度不能少于6位')
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, '密码修改成功 🔐')
            return redirect('accounts:profile')
    
    return render(request, 'accounts/change_password.html')


@login_required
def technician_list(request):
    if request.user.role != 'admin':
        messages.error(request, '无权限访问')
        return redirect('/')
    technicians = User.objects.filter(role='technician').order_by('-date_joined')
    return render(request, 'accounts/technician_list.html', {'technicians': technicians})

@login_required
def add_technician(request):
    if request.user.role != 'admin':
        messages.error(request, '无权限访问')
        return redirect('/')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        nickname = request.POST.get('nickname')
        phone = request.POST.get('phone')
        
        if not username or not password:
            messages.error(request, '用户名和密码为必填项')
            return render(request, 'accounts/add_technician.html')
        
        if password != password2:
            messages.error(request, '两次密码输入不一致')
            return render(request, 'accounts/add_technician.html')
        
        if len(password) < 6:
            messages.error(request, '密码长度不能少于6位')
            return render(request, 'accounts/add_technician.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
            return render(request, 'accounts/add_technician.html')
        
        if phone and User.objects.filter(phone=phone).exists():
            messages.error(request, '手机号已被其他用户使用')
            return render(request, 'accounts/add_technician.html')
        
        user = User.objects.create_user(
            username=username,
            password=password,
            nickname=nickname or username,
            phone=phone or None,
            role='technician',
            is_active=True,
        )
        messages.success(request, f'技师 {user.nickname or user.username} 添加成功 ✨')
        return redirect('accounts:technician_list')
    
    return render(request, 'accounts/add_technician.html')
