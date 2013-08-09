from django.shortcuts import render_to_response, RequestContext
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.context_processors import csrf
from game.models import Profile, Game
from game.views import percentage_generator

def home(request):
    user = auth.get_user(request)
    if user.is_authenticated():  #user is Logged
        if user.profile.in_game:  #user in game -> redirect to active game
            return HttpResponseRedirect('/game/active/')
        elif user.profile.is_host:  #user is host -> redirect to wait room
            return HttpResponseRedirect('/game/wait_room')

    first_ten_profiles =  Profile.objects.order_by('-points')[:10]  #get first ten profiles, ordered by points
    games_on_wait = Game.objects.filter(wait=True)  #get all games waiting for opponent player
    args = {'first_ten': first_ten_profiles, 'games': games_on_wait}  #make args dict

    user = auth.get_user(request)
    if user.is_authenticated():
        args['rank'] = percentage_generator(user.profile)  #add user % based rank to args dict
    return render_to_response('home.html', args, context_instance=RequestContext(request))

def login(request):
    user = auth.get_user(request)
    if user.is_authenticated():  #user already logged in
        if user.profile.in_game:   #user in game -> redirect to active game
            return HttpResponseRedirect('/game/active/')
        elif user.profile.is_host:   #user is host -> redirect to wait room
            return HttpResponseRedirect('/game/wait_room/')
        else:
            return HttpResponseRedirect('/home/')
    else:
        if request.method == 'POST':  #HTTP method is POST (form posted)
            form = AuthenticationForm(None, request.POST)  #standard user authentication form
            if form.is_valid():  #user login is valid
                auth.login(request, form.get_user())  #login user and redirect
                return HttpResponseRedirect('/home/')

        form = AuthenticationForm()  #form is not valid or HTTP method is not POST
        args = {}
        args.update(csrf(request))  #add Cross Site Request Forgery protection for better security

        args['form'] = form  #add form to args and render form
        return render_to_response('login.html', args)

def logout(request): #user log out
    user = auth.get_user(request)
    if user.is_authenticated():  #user is logged in
        auth.logout(request)  #logging out user
    return HttpResponseRedirect('/home/')
    
def register_user(request):  #register new user
    user = auth.get_user(request)
    if user.is_authenticated():  #user already logged in
        if user.profile.in_game:   #user in game -> redirect to active game
            return HttpResponseRedirect('/game/active/')
        elif user.profile.is_host:   #user is host -> redirect to wait room
            return HttpResponseRedirect('/game/wait_room/')
        else:
            return HttpResponseRedirect('/home/')
    else:
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.save()
                user.profile = Profile(user=user)
                user.save()
                user.profile.save()
                return HttpResponseRedirect('/accounts/register_success/')

        form = UserCreationForm()
        args = {}
        args.update(csrf(request))

        args['form'] = form

        return render_to_response('register.html', args)

def register_success(request): #new user registered successfully
    user = auth.get_user(request)
    if user.is_authenticated():  #user already logged in
        if user.profile.in_game:   #user in game -> redirect to active game
            return HttpResponseRedirect('/game/active/')
        elif user.profile.is_host:   #user is host -> redirect to wait room
            return HttpResponseRedirect('/game/wait_room/')
        else:
            return HttpResponseRedirect('/home/')
    else:
        return render_to_response('register_success.html', context_instance=RequestContext(request))