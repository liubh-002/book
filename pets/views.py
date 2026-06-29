from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Pet

@login_required
def pet_list(request):
    pets = Pet.objects.filter(user=request.user, is_active=True)
    return render(request, 'pets/list.html', {'pets': pets})

@login_required
def pet_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if not name:
            messages.error(request, '请填写宠物昵称')
            return render(request, 'pets/add_edit.html')
        
        pet = Pet.objects.create(
            user=request.user,
            name=name,
            breed=request.POST.get('breed', ''),
            gender=request.POST.get('gender', ''),
            age=request.POST.get('age') or None,
            weight=request.POST.get('weight') or None,
            color=request.POST.get('color', ''),
            size=request.POST.get('size', 'small'),
            vaccination=request.POST.get('vaccination', ''),
            deworming=request.POST.get('deworming', ''),
            allergies=request.POST.get('allergies', ''),
            medical_history=request.POST.get('medical_history', ''),
            taboos=request.POST.get('taboos', ''),
            personality=request.POST.get('personality', ''),
            notes=request.POST.get('notes', ''),
        )
        if 'avatar' in request.FILES:
            pet.avatar = request.FILES['avatar']
        pet.save()
        
        messages.success(request, f'🎉 {pet.name}的档案创建成功！')
        return redirect('pets:list')
    
    return render(request, 'pets/add_edit.html', {'is_add': True})

@login_required
def pet_edit(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, user=request.user)
    if request.method == 'POST':
        pet.name = request.POST.get('name', pet.name)
        pet.breed = request.POST.get('breed', '')
        pet.gender = request.POST.get('gender', '')
        pet.age = request.POST.get('age') or None
        pet.weight = request.POST.get('weight') or None
        pet.color = request.POST.get('color', '')
        pet.size = request.POST.get('size', 'small')
        pet.vaccination = request.POST.get('vaccination', '')
        pet.deworming = request.POST.get('deworming', '')
        pet.allergies = request.POST.get('allergies', '')
        pet.medical_history = request.POST.get('medical_history', '')
        pet.taboos = request.POST.get('taboos', '')
        pet.personality = request.POST.get('personality', '')
        pet.notes = request.POST.get('notes', '')
        if 'avatar' in request.FILES:
            pet.avatar = request.FILES['avatar']
        pet.save()
        messages.success(request, f'✨ {pet.name}的档案已更新！')
        return redirect('pets:list')
    
    return render(request, 'pets/add_edit.html', {'pet': pet, 'is_add': False})

@login_required
def pet_delete(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, user=request.user)
    pet.is_active = False
    pet.save()
    messages.success(request, f'{pet.name}的档案已删除')
    return redirect('pets:list')

@login_required
def pet_set_default(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, user=request.user)
    Pet.objects.filter(user=request.user).update(is_default=False)
    pet.is_default = True
    pet.save()
    messages.success(request, f'{pet.name}已设为默认宠物')
    return redirect('pets:list')
