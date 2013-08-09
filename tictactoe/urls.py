from django.conf.urls import patterns, include, url

#setting up the global project url patterns
urlpatterns = patterns('',
    url(r'^$', 'tictactoe.views.home'),
    url(r'^home/$', 'tictactoe.views.home'),  #home page url

    url(r'^game/', include('game.urls')),  #game page (app) url

    #user login/register/logout urls:
    url(r'^accounts/login/$', 'tictactoe.views.login'),
    url(r'^accounts/logout/$', 'tictactoe.views.logout'),
    url(r'^accounts/register/$', 'tictactoe.views.register_user'),
    url(r'^accounts/register_success/$', 'tictactoe.views.register_success'),
)
