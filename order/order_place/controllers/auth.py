from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout

def auth(request):
    if request.method =='POST':
        username = request.POST.get('login')
        password = request.POST.get('password')
        print(login, password)
        user = authenticate(request,  username=username, password=password )
        if user is not None:
            login(request, user)
            request.session['user'] = user.id
            return redirect('order')
    return render(request, 'auth.html')

def user_logout(request):
    if request.method =='POST':
        logout(request)
    return redirect('auth')



    
