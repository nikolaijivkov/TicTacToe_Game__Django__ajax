from django.shortcuts import render_to_response, RequestContext
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.utils import timezone
from game.models import Game, Profile
from game.game_class import TicTacToe


def percentage_generator(user_profile):
    points = user_profile.points
    profiles = Profile.objects.all()
    size = len(profiles)-1  #exclude self from count!!!
    counter=0
    for profile in profiles:
        if points > profile.points: counter+=1
    try:
        result = (counter*100)/size
    except:
        result = 0  #eather counter was 0, or size was 0...
    return result

def host_game(request):
    user = auth.get_user(request)
    if user.is_authenticated():  #user is Logged In
        if user.profile.in_game:  #active game found -> redirect to active game
            return HttpResponseRedirect('/game/active/')
        else:  #set up user's profile for new game
            user.profile.in_game = False
            user.profile.is_host = True
            user.profile.on_turn = True
            user.profile.game_ended = False
            user.profile.current_game_score = None

            user.profile.hosted_game = Game(host_player=user.profile)  #Create new game

            user.profile.save()
            user.profile.hosted_game.save()

            return HttpResponseRedirect('/game/wait_room/')
    else:
        return HttpResponseRedirect('/home/')

def join_game(request, game_id):
    user = auth.get_user(request)
    if user.is_authenticated():  #user is Logged In
        if user.profile.in_game:  #active game found -> redirect to active game
            return HttpResponseRedirect('/game/active/')
        elif user.profile.is_host: #user is host -> redirect to wait room
            return HttpResponseRedirect('/game/wait_room/')
        else:  #set up user's profile for new game
            user.profile.in_game = True
            user.profile.on_turn = False
            user.profile.game_ended = False
            user.profile.current_game_score = None

            game = Game.objects.get(pk=game_id)  #get the game with id=game_id
            game.time_to_move = timezone.now() + timezone.timedelta(seconds=60)  #opponent should move in 60 seconds from now!!!
            game.wait = False  #game no more in wait list -> game will start shortly
            game.join_player = user.profile  #set join player relationship with that game

            opponent = game.host_player  #get opponent profile from that game
            opponent.in_game=True  #opponent is host and has the first turn
            opponent.on_turn=True  #opponent is in game

            user.profile.joined_game = game

            game.save()
            user.profile.save()
            opponent.save()

            return HttpResponseRedirect('/game/active/')
    else:
        return HttpResponseRedirect('/home/')

def wait_room(request):
    user = auth.get_user(request)
    if user.is_authenticated():  #user is Logged In
        if user.profile.in_game:  #active game found -> redirect ot active game
            return HttpResponseRedirect('/game/active/')
        elif user.profile.is_host:  #user is host -> he belong here
            args={'rank': percentage_generator(user.profile)}
            return render_to_response("wait_room.html", args, context_instance=RequestContext(request))
        else:  #user is not host -> redirect ot home
            return HttpResponseRedirect('/home/')
    else:
        return HttpResponseRedirect('/home/')

def bot_play(request):
    user = auth.get_user(request)
    if user.is_authenticated():  #user is Logged In
        if user.profile.in_game:  #active game found -> redirect to active game
            return HttpResponseRedirect('/game/active/')
        elif user.profile.is_host and user.profile.hosted_game.wait:  #user is host and have game on wait -> he belong here
            #set up user profile for game with bot
            user.profile.in_game = True
            user.profile.on_turn = True
            user.profile.game_ended = False
            user.profile.current_game_score = None

            game = user.profile.hosted_game  #get game from hosted_game relationship field
            game.time_to_move = timezone.now() + timezone.timedelta(seconds=60) #move countdown set to 60 seconds from now!!!
            game.wait = False

            game.save()
            user.profile.save()

            return HttpResponseRedirect('/game/active/')
        else:  #user is not host or don't have game on wait -> redirect to home
            return HttpResponseRedirect('/home/')
    else:
        return HttpResponseRedirect('/home/')

def active_game(request):
    user = auth.get_user(request)
    if user.is_authenticated():  #user is Logged In
        if user.profile.in_game:  #active game found
            if user.profile.game_ended:  #game has ended -> redirect to end game
                return HttpResponseRedirect('/game/end_game/')
            elif user.profile.is_host:  #user is host -> set up variables for host player
                user_sign='X'
                opponent_sign='O'
                game = user.profile.hosted_game
                opponent = game.join_player  #opponent may be = None -> opponent is bot
            else:  #user is not host -> set up variables for not host player
                user_sign='O'
                opponent_sign='X'
                game = user.profile.joined_game
                opponent = game.host_player  #opponent wont be = None -> opponent is aways other playes
            if user.profile.on_turn:  #check who is on turn
                on_turn = user
            elif opponent: #opponent is not None -> not bot
                on_turn = opponent.user
            else: #bot is on move, but bots move instantly... so host player will be on move when page renders!!!
                on_turn = user

            board = game.board #get game board status

            #cast from text field to dict object for easier access later on
            game_field_status = board.split(',')
            board_dict={
                '0':{'0':None, '1':None, '2':None},
                '1':{'0':None, '1':None, '2':None},
                '2':{'0':None, '1':None, '2':None},}
            for field in game_field_status:
                pos,sign=field.split(':')
                if sign=='_': sign=None
                board_dict[pos[0]][pos[1]]=sign

            tictactoe_game_obj=TicTacToe(board_dict)  #make new game object with current board fields

            if tictactoe_game_obj.win_lost_check(home=user_sign, away=opponent_sign):  #win/lost/tie check -> if True game ends
                current_game_score = unicode(tictactoe_game_obj.win_lost)  #force cast to unicode just in case

                user.profile.game_ended = True
                user.profile.current_game_score = current_game_score
                user.profile.save()

                if opponent:  #opponent not None (not bot) -> game ends for him too, set his profile
                    opponent.game_ended = True
                    if current_game_score==u'win':
                        opponent_score = u'lost'
                    elif current_game_score==u'lost':
                        opponent_score = u'win'
                    elif current_game_score==u'tie':
                        opponent_score = u'tie'
                    else:
                        raise Exception('Current_game_score is not one of the possible scores! This should never happen!')
                    opponent.current_game_score = opponent_score
                    opponent.save()
                return HttpResponseRedirect('/game/end_game/')  #game has ended -> redirect ot end game

            else:  #if no end game has occurred -> move on as usual
                time_left = game.time_to_move - timezone.now()  #compute time to auto move
                if( time_left.days<0 or (user.profile.on_turn==False and opponent==None)):  #eather time is up, or this is game with bot and he is on turn
                    if user.profile.on_turn:  #time indeed is up -> bot will move instead of user on turn
                        tictactoe_game_obj.bot_move(sign=user_sign)  #bot move with user sign

                        user.profile.on_turn=False  #user is not on turn -> set his profile
                        user.profile.save()

                        if opponent: #opponent is not None (not bot) -> he is on turn, set his profile
                            opponent.on_turn=True
                            opponent.save()
                    else:  #user is not on turn -> time is up or bot is on turn
                        tictactoe_game_obj.bot_move(sign=opponent_sign)  #bot move with opponent sign

                        user.profile.on_turn=True  #user is on turn -> set his profile
                        user.profile.save()

                        if opponent:  #opponent not None (not bot) -> he is not in turn, set his profile
                            opponent.on_turn=False
                            opponent.save()

                    board_dict=tictactoe_game_obj.board  #get game board from tictactoe_game_obj

                    #cast from dict object to text filed
                    board = ''
                    for i in sorted(board_dict):
                        for j in sorted(board_dict[i]):
                            sign=board_dict[i][j]
                            if sign==None: sign='_'
                            board+=i+j+':'+sign
                            if(not i==j=='2'): board+=','

                    game.board = board  #set game board
                    game.time_to_move =  timezone.now() + timezone.timedelta(seconds=60)  #opponent should move in 60 seconds from now!!!
                    game.save()

                    time_left = timezone.timedelta(seconds=60)  #time to next auto move 60 sec!!!

                #make template argument dictionary
                args={'pos00': board_dict['0']['0'], 'pic00': 'assets/images/'+str(board_dict['0']['0'])+'.png',
                      'pos01': board_dict['0']['1'], 'pic01': 'assets/images/'+str(board_dict['0']['1'])+'.png',
                      'pos02': board_dict['0']['2'], 'pic02': 'assets/images/'+str(board_dict['0']['2'])+'.png',
                      'pos10': board_dict['1']['0'], 'pic10': 'assets/images/'+str(board_dict['1']['0'])+'.png',
                      'pos11': board_dict['1']['1'], 'pic11': 'assets/images/'+str(board_dict['1']['1'])+'.png',
                      'pos12': board_dict['1']['2'], 'pic12': 'assets/images/'+str(board_dict['1']['2'])+'.png',
                      'pos20': board_dict['2']['0'], 'pic20': 'assets/images/'+str(board_dict['2']['0'])+'.png',
                      'pos21': board_dict['2']['1'], 'pic21': 'assets/images/'+str(board_dict['2']['1'])+'.png',
                      'pos22': board_dict['2']['2'], 'pic22': 'assets/images/'+str(board_dict['2']['2'])+'.png',
                      'on_turn': on_turn,
                      'time_left': time_left,
                      'game_id': game.id,
                      'rank': percentage_generator(user.profile)}
                return render_to_response('board.html', args, context_instance=RequestContext(request))
        else:
            if user.profile.is_host:
                return HttpResponseRedirect('/game/wait_room/')
            else:
                return HttpResponseRedirect('/home/')
    else:
        return HttpResponseRedirect('/home')

def get_board(request):
    print "getting board"
    reload_page=False
    user = auth.get_user(request)
    if(not user.is_authenticated() or not user.profile.in_game or user.profile.game_ended):
        reload_page=True
        args={'reload_page':reload_page,}
        return render_to_response('only_board.html', args, context_instance=RequestContext(request))
    else:
        if user.profile.is_host:  #user is host -> set up variables for host player
            user_sign='X'
            opponent_sign='O'
            try:
                game = user.profile.hosted_game
                print "GAME:", game
                opponent = game.join_player  #opponent may be = None -> opponent is bot
                print "OPPONENT:", opponent
            except:
                game = None
                opponent = None
        else:  #user is not host -> set up variables for not host player
            user_sign='O'
            opponent_sign='X'
            try:
                game = user.profile.joined_game
                print "GAME:", game
                opponent = game.host_player  #opponent wont be = None -> opponent is aways other playes
                print "OPPONENT:", opponent
            except:
                game = None
                opponent = None
        if user.profile.on_turn:  #check who is on turn
            on_turn = user
        elif opponent: #opponent is not None -> not bot
            on_turn = opponent.user
        else: #bot is on move, but bots move instantly... so host player will be on move when page renders!!!
            on_turn = user

        if(game == None):
            reload_page = True

    if(not reload_page):
        board = game.board #get game board status

        #cast from text field to dict object for easier access later on
        game_field_status = board.split(',')
        board_dict={
            '0':{'0':None, '1':None, '2':None},
            '1':{'0':None, '1':None, '2':None},
            '2':{'0':None, '1':None, '2':None},}
        for field in game_field_status:
            pos,sign=field.split(':')
            if sign=='_': sign=None
            board_dict[pos[0]][pos[1]]=sign

        tictactoe_game_obj=TicTacToe(board_dict)  #make new game object with current board fields

        if tictactoe_game_obj.win_lost_check(home=user_sign, away=opponent_sign):  #win/lost/tie check -> if True game ends
            current_game_score = unicode(tictactoe_game_obj.win_lost)  #force cast to unicode just in case

            user.profile.game_ended = True
            user.profile.current_game_score = current_game_score
            user.profile.save()

            if opponent:  #opponent not None (not bot) -> game ends for him too, set his profile
                opponent.game_ended = True
                if current_game_score==u'win':
                    opponent_score = u'lost'
                elif current_game_score==u'lost':
                    opponent_score = u'win'
                elif current_game_score==u'tie':
                    opponent_score = u'tie'
                else:
                    raise Exception('Current_game_score is not one of the possible scores! This should never happen!')
                opponent.current_game_score = opponent_score
                opponent.save()

            reload_page=True#return HttpResponseRedirect('/game/end_game/')  #game has ended -> redirect ot end game

        else:  #if no end game has occurred -> move on as usual
            time_left = game.time_to_move - timezone.now()  #compute time to auto move
            if( time_left.days<0 or (user.profile.on_turn==False and opponent==None)):  #eather time is up, or this is game with bot and he is on turn
                if user.profile.on_turn:  #time indeed is up -> bot will move instead of user on turn
                    tictactoe_game_obj.bot_move(sign=user_sign)  #bot move with user sign

                    user.profile.on_turn=False  #user is not on turn -> set his profile
                    user.profile.save()

                    if opponent: #opponent is not None (not bot) -> he is on turn, set his profile
                        opponent.on_turn=True
                        opponent.save()
                else:  #user is not on turn -> time is up or bot is on turn
                    tictactoe_game_obj.bot_move(sign=opponent_sign)  #bot move with opponent sign

                    user.profile.on_turn=True  #user is on turn -> set his profile
                    user.profile.save()

                    if opponent:  #opponent not None (not bot) -> he is not in turn, set his profile
                        opponent.on_turn=False
                        opponent.save()

                board_dict=tictactoe_game_obj.board  #get game board from tictactoe_game_obj

                #cast from dict object to text filed
                board = ''
                for i in sorted(board_dict):
                    for j in sorted(board_dict[i]):
                        sign=board_dict[i][j]
                        if sign==None: sign='_'
                        board+=i+j+':'+sign
                        if(not i==j=='2'): board+=','

                game.board = board  #set game board
                game.time_to_move =  timezone.now() + timezone.timedelta(seconds=60)  #opponent should move in 60 seconds from now!!!
                game.save()

                time_left = timezone.timedelta(seconds=60)  #time to next auto move 60 sec!!!

        if(reload_page):
            args={'reload_page':reload_page,}
        else:
            args={'pos00': board_dict['0']['0'], 'pic00': 'assets/images/'+str(board_dict['0']['0'])+'.png',
                  'pos01': board_dict['0']['1'], 'pic01': 'assets/images/'+str(board_dict['0']['1'])+'.png',
                  'pos02': board_dict['0']['2'], 'pic02': 'assets/images/'+str(board_dict['0']['2'])+'.png',
                  'pos10': board_dict['1']['0'], 'pic10': 'assets/images/'+str(board_dict['1']['0'])+'.png',
                  'pos11': board_dict['1']['1'], 'pic11': 'assets/images/'+str(board_dict['1']['1'])+'.png',
                  'pos12': board_dict['1']['2'], 'pic12': 'assets/images/'+str(board_dict['1']['2'])+'.png',
                  'pos20': board_dict['2']['0'], 'pic20': 'assets/images/'+str(board_dict['2']['0'])+'.png',
                  'pos21': board_dict['2']['1'], 'pic21': 'assets/images/'+str(board_dict['2']['1'])+'.png',
                  'pos22': board_dict['2']['2'], 'pic22': 'assets/images/'+str(board_dict['2']['2'])+'.png',
                  'on_turn': on_turn,
                  'time_left': time_left,
                  'reload_page':reload_page,
            }
        return render_to_response('only_board.html', args, context_instance=RequestContext(request))

def get_board_clumzy(request):  #not in use...
    game_id = request.GET['game_id']
    game=Game.objects.get(pk=game_id)

    board = game.board #get game board status

    #cast from text field to dict object for easier access later on
    game_field_status = board.split(',')
    board_dict={
        '0':{'0':None, '1':None, '2':None},
        '1':{'0':None, '1':None, '2':None},
        '2':{'0':None, '1':None, '2':None},}
    for field in game_field_status:
        pos,sign=field.split(':')
        if sign=='_': sign=None
        board_dict[pos[0]][pos[1]]=sign

    user = auth.get_user(request)
    if user.is_authenticated(): print('YES BABE!!!')

    on_turn = 'unknown'

    time_left = 0

    args={'pos00': board_dict['0']['0'], 'pic00': 'assets/images/'+str(board_dict['0']['0'])+'.png',
          'pos01': board_dict['0']['1'], 'pic01': 'assets/images/'+str(board_dict['0']['1'])+'.png',
          'pos02': board_dict['0']['2'], 'pic02': 'assets/images/'+str(board_dict['0']['2'])+'.png',
          'pos10': board_dict['1']['0'], 'pic10': 'assets/images/'+str(board_dict['1']['0'])+'.png',
          'pos11': board_dict['1']['1'], 'pic11': 'assets/images/'+str(board_dict['1']['1'])+'.png',
          'pos12': board_dict['1']['2'], 'pic12': 'assets/images/'+str(board_dict['1']['2'])+'.png',
          'pos20': board_dict['2']['0'], 'pic20': 'assets/images/'+str(board_dict['2']['0'])+'.png',
          'pos21': board_dict['2']['1'], 'pic21': 'assets/images/'+str(board_dict['2']['1'])+'.png',
          'pos22': board_dict['2']['2'], 'pic22': 'assets/images/'+str(board_dict['2']['2'])+'.png',
          'on_turn': on_turn,
          'time_left': time_left,
          }
    return render_to_response('only_board.html', args, context_instance=RequestContext(request))

def move(request, i, j):
    user = auth.get_user(request)
    if user.is_authenticated(): #user is Logged In
        if user.profile.in_game: #active game found
            if user.profile.on_turn: #user is on turn -> he belong here
                if user.profile.is_host:
                    game = user.profile.hosted_game
                    opponent = game.join_player
                    user_sign='X'
                else:
                    game = user.profile.joined_game
                    opponent = game.host_player
                    user_sign='O'
                board = game.board #get game board status

                #cast from text field to dict object
                game_field_status = board.split(',')
                board_dict={
                    '0':{'0':None, '1':None, '2':None},
                    '1':{'0':None, '1':None, '2':None},
                    '2':{'0':None, '1':None, '2':None},}
                for field in game_field_status:
                    pos,sign=field.split(':')
                    if sign==u'_': sign=None
                    board_dict[pos[0]][pos[1]]=sign

                if board_dict[i][j]==None:  #game filed is empty
                    board_dict[i][j]=user_sign  #change dict object
                    game.time_to_move = timezone.now() + timezone.timedelta(seconds=60) #reset timer for next move to 60 seconds
                else: #game field is not empty -> redirect to active game and try again
                    return HttpResponseRedirect('/game/active/')

                #cast from dict object to field text
                board = ''
                for i in sorted(board_dict):
                    for j in sorted(board_dict[i]):
                        sign=board_dict[i][j]
                        if sign==None: sign='_'
                        board+=i+j+':'+sign
                        if(not i==j=='2'): board+=','

                game.board = board  #set game board
                game.save()

                user.profile.on_turn=False  #user is not on turn -> set his profile
                user.profile.save()

                if opponent: #opponent not None (not bot) -> he is not in turn, set his profile
                    opponent.on_turn=True
                    opponent.save()

                return HttpResponseRedirect('/game/active/')
            else:  #user is not on turn -> redirect ot active game to wait for his turn
                return HttpResponseRedirect('/game/active/')
        else:
            if user.profile.is_host:
                return HttpResponseRedirect('/game/wait_room/')
            else:
                return HttpResponseRedirect('/home/')
    else:
        return HttpResponseRedirect('/home')

def surrender(request):
    user = auth.get_user(request)
    if user.is_authenticated():  #user is Logged
        if user.profile.game_ended:  #game has ended -> redirect ot end game
            return HttpResponseRedirect('/game/end_game/')
        elif user.profile.in_game:  #user is in game -> he belong here
            if user.profile.is_host:  #find opponent
                opponent = user.profile.hosted_game.join_player
            else:
                opponent = user.profile.joined_game.host_player

            #set up user profile for end game
            user.profile.game_ended = True
            user.profile.current_game_score = u'surrender'
            user.profile.save()

            if opponent:  #if opponent not None (not bot) -> set his profile for end game
                opponent.game_ended = True
                opponent.current_game_score = u'win'
                opponent.save()

            return HttpResponseRedirect('/game/end_game/')  #redirect to end game
        else:  #user not in game -> redirect to right location
            if user.profile.is_host:
                return HttpResponseRedirect('/game/wait_room/')
            else:
                return HttpResponseRedirect('/home/')
    else:
        return HttpResponseRedirect('/home')

def end_game(request):
    user = auth.get_user(request)
    if user.is_authenticated():  #user is Logged
        if( user.profile.in_game==False and user.profile.game_ended):  #user is no longer in game and game has ended -> redirect to score
            return HttpResponseRedirect('/game/game_score/')           #(this is possible when other player has been here first)
        elif( user.profile.in_game and user.profile.game_ended):  #user is in game and game has ended -> he belong here
            #get opponent and try to remove game from DB
            if user.profile.is_host:
                try:
                    opponent = user.profile.hosted_game.join_player  #Game may be deleted earlier by user opponent
                    user.profile.hosted_game.delete()
                except:
                    opponent = None
            else:
                try:
                    opponent = user.profile.joined_game.host_player  #Game may be deleted earlier by user opponent
                    user.profile.joined_game.delete()
                except:
                    opponent = None
            #set user profile for game score screen
            user.profile.in_game=False
            user.profile.is_host=False
            user.profile.on_turn=False
            user.profile.game_ended=True
            user.profile.save()

            if opponent:  #if opponent not None (not bot or game not deleted) -> set his profile for game score screen
                opponent.in_game=True
                opponent.is_host=False
                opponent.on_turn=False
                opponent.game_ended=True
                opponent.save()

            return HttpResponseRedirect('/game/game_score/')  #redirect user to game score page
        else:
            if user.profile.is_host:
                return HttpResponseRedirect('/game/wait_room/')
            else:
                return HttpResponseRedirect('/home/')
    else:
        return HttpResponseRedirect('/home')

def game_score(request):  #game has ended and all we have to do is look at the score and deliver some messages
    user = auth.get_user(request)
    if user.is_authenticated():  #user is Logged
        if user.profile.game_ended:  #game has indeed ended -> user belong here
            condition = user.profile.current_game_score  #get end game condition

            #clear last remaining game related fields from user profile
            user.profile.game_ended = False
            user.profile.current_game_score = ''

            #set message and give points if need be
            if condition==u"win":
                msg="Congrats, You win!"
                user.profile.points +=1
            elif condition==u"tie":
                msg="It's a tie!"
            elif condition==u"lost":
                msg="Alas, You lost!"
            elif condition==u"surrender":
                msg="Alas, You surrender!"
            else:
                raise Exception('Current_game_score is not one of the possible scores! This should never happen!')
            user.profile.save()

            args={'msg':msg, 'rank': percentage_generator(user.profile)}  #make arg dict
            return render_to_response('end_game.html', args, context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect('/home')
    else:
        return HttpResponseRedirect('/home')