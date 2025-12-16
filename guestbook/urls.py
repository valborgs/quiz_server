from django.urls import path
from .views import GuestbookListCreateView, GuestbookDeleteView

urlpatterns = [
    path('guestbook/', GuestbookListCreateView.as_view(), name='guestbook-list-create'),
    path('guestbook/<int:pk>/', GuestbookDeleteView.as_view(), name='guestbook-delete'),
]
