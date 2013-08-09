from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
#user.profile model object -> related to user model
class Profile(models.Model):
    user = models.OneToOneField(User)  #DB relationship 1 to 1 -> 1 user may have only 1 profile!!!
    points = models.IntegerField(default=0)
    in_game = models.BooleanField(default=False)
    is_host = models.BooleanField(default=False)
    on_turn = models.BooleanField(default=False)
    game_ended = models.BooleanField(default=False)
    current_game_score = models.CharField(max_length=10, null=True, blank=True, default = None)

#game model object -> related to user.profile model
class Game(models.Model):
    host_player = models.OneToOneField(Profile, related_name='hosted_game')  #DB relationship 1 to 1 -> 1 user.profile is host of only 1 game!!!
    join_player = models.OneToOneField(Profile, related_name='joined_game', null=True, blank=True, default = None)  #DB relationship 1 to 1 -> user.profile may join only one game (this filed may be Null)!!!
    wait = models.BooleanField(default=True)
    time_to_move = models.DateTimeField(default=None, null=True, blank=True)
    board = models.TextField(default="00:_,01:_,02:_,10:_,11:_,12:_,20:_,21:_,22:_")  #set up initial empty board
