from django.urls import path

from . import views

urlpatterns = [
    path('',views.MainPage.as_view(), name='main'),
    path('about/', views.About.as_view(), name='about'),
    path('post/<slug:event_slug>/', views.ShowPost.as_view(), name='detail'),
    path('category/<slug:category_slug>', views.show_by_category, name='category'),
    path('authors_by_category/<slug:category_slug>', views.show_by_category, name='authors_by_category'),
    path('response/post/<int:event_id>', views.AllResponses.as_view(), name='response'),
    path('answer/response/<int:resp_id>', views.AllAnswers.as_view(), name='show answers to response'),
    path('create/answer/<int:resp_id>', views.CreateAnswerToResponse.as_view(), name='create answer'),
    path('update/answer/<int:answ_id>', views.UpdateAnswerToResponse.as_view(), name='update answer'),
    path('delete/answer/<int:answ_id>', views.delete_answer, name='delete answer'),
    path('delete/response/<int:resp_id>', views.delete_response, name='delete response'),
    path('create/event/', views.CreateEvent.as_view(), name='create_event'),
    path('edit/event/<int:event_id>', views.UpdateEvent.as_view(), name='update event'),
    path('search/post', views.PostSearch.as_view(), name='search_event'),
    path('search/author', views.SearchProfile.as_view(), name='search_player'),
    path('player/<int:player_id>', views.PlayerProfile.as_view(), name='player'),
    path('authors', views.AllAuthors.as_view(), name='authors'),
    path('create/profile', views.CreateProfile.as_view(), name='create profile'),
    path('edit/author/<int:player_id>', views.UpdateProfile.as_view(), name='edit author'),
    path('delete/author/<int:player_id>', views.DeleteProfile.as_view(), name='delete author'),
    path('response_create/<int:event_id>', views.CreateResponse.as_view(), name='create_response'),
    path('response_edit/<int:resp_id>', views.UpdateResponse.as_view(), name='update response'),
    path('delete_post/<slug:event_slug>', views.delete_post, name='delete of post'),
    path('successful_delete/<slug:event_slug>', views.successful_delete, name='successful delete'),
    path('private_web_page/<int:player_id>', views.PrivateWebPage.as_view(), name='private webpage'),
    path('take_player/resp/<int:resp_id>',views.take_player_by_response, name='take player by response')
]