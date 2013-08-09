from django.conf.urls import patterns, url, include

#setting up the game url patterns
urlpatterns = patterns('',
    url(r'^host_game/$', 'game.views.host_game'),
    url(r'^join_game/(?P<game_id>\d+)/$', 'game.views.join_game'),
    url(r'^wait_room/$', 'game.views.wait_room'),
    url(r'^bot/$', 'game.views.bot_play'),
    url(r'^active/$', 'game.views.active_game'),
    url(r'^move/(?P<i>\d{1})/(?P<j>\d{1})/$', 'game.views.move'),
    url(r'^end_game/$', 'game.views.end_game'),
    url(r'^game_score/$', 'game.views.game_score'),
    url(r'^surrender/$', 'game.views.surrender'),
    url(r'^get_board/$', 'game.views.get_board'),
)