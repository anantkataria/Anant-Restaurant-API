from django.urls import path
from . import views

from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('api-token-auth', obtain_auth_token),
    
    path('category-list', views.CategoryItemsView.as_view()),
    path('menu-items', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    
    path('groups/manager/users', views.ManagersView.as_view()),
    path('groups/manager/users/<int:pk>', views.SingleManagersView.as_view()),
    path('groups/delivery-crew/users', views.DeliveryCrewView.as_view()),
    path('groups/delivery-crew/users/<int:pk>', views.SingleDeliveryCrewView.as_view()),
    
    path('cart/menu-items', views.CartItemsView.as_view()),
    
    path('orders', views.OrdersView.as_view()),
    path('orders/<int:pk>', views.SingleOrderItemsView.as_view()),
]