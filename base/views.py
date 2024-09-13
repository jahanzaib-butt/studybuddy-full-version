from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Room,Topic,Message
from .forms import RoomForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages
from django.contrib.auth.models import User 
from django.contrib.auth.forms import  UserCreationForm

# Create your views here.

# rooms= [
#     {'id':1,'name':'lets learn python'},
#     {'id':2,'name':'designing with python'},

#     {'id':3,'name':'coding python'},
# ]



#home page 
def home(request):
    q =  request.GET.get('q') if request.GET.get('q') != None else ''

    rooms =  Room.objects.filter(
        Q(topic__name__icontains=q)|
        Q(name__icontains=q)|
        Q(host__username__icontains=q)|
        Q(description__icontains=q)
        )
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages =  Message.objects.filter(room__topic__name__icontains=q)[0:5]



    context  = {'rooms': rooms,'topics':topics,'room_count':room_count,'room_messages':room_messages}

    return render(request, 'base/home.html',context)



#room page
def room(request,pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    if  request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
    

    context  = {'room': room,'room_messages':room_messages,
                'participants':participants}
    return render(request, 'base/room.html',context)



#login page
def login_view(request):
    page = 'login'

    if  request.user.is_authenticated:
        return redirect('home')


    if request.method == 'POST':
        username = request.POST['username'].lower()
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')  # redirect to the home page
        else:
            messages.error(request, "wrong username or password .")
    content  = {'page': page}
    return render(request, 'base/login.html',content)


#logout page
def logout_view(request):
    logout(request)
    return redirect('home')

#register form
def registerUser(request):
    # page = 'register'
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request,'An error has occurred during registration')

    return render(request,'base/login.html',{'form':form})




def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user,'rooms':rooms,'room_messages':room_messages,'topics':topics}
    return render(request,'base/profile.html',context)

#createRoom
@login_required(login_url='login')
def  createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form =  RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context={'form':form}
    return  render(request, 'base/room_form.html',context)


#updateRoom
@login_required(login_url='login')
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    if request.user != room.host:
        return HttpResponse('You do not own this room!')

    if  request.method == 'POST':
        form = RoomForm(request.POST,instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')


    context = {'form':form}
    return render (request, 'base/room_form.html',context)



#deleteRoom
@login_required(login_url='login')
def  deleteRoom(request,pk):
    room =  Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You do not own this room!')

    if request.method == 'POST':
        room.delete()
        return  redirect('home')

    return render (request, 'base/delete.html',{'obj':room})


@login_required(login_url='login')
def  deleteMessage(request,pk):
    message =  Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('You do not own this room!')

    if request.method == 'POST':
        message.delete()
        return  redirect('home')

    return render (request, 'base/delete.html',{'obj':message})


