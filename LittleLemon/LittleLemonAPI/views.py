from . import models
from . import serializers
import decimal
from .permissions import IsUserManagerOrReadOnly, IsUserManager
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404

class CategoryItemsView(generics.ListCreateAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    permission_classes = [IsAuthenticated, IsUserManagerOrReadOnly | IsAdminUser]
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    ordering_fields = ['title']
    search_fields = ['title']

class MenuItemsView(generics.ListCreateAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    permission_classes = [IsAuthenticated, IsUserManagerOrReadOnly | IsAdminUser]
    serializer_class = serializers.MenuItemSerializer
    ordering_fields = ['price']
    search_fields = ['title', 'category__title']
    
    def get_queryset(self):
        queryset = models.MenuItem.objects.select_related('category').all()
        category_name = self.request.query_params.get('category')
        if category_name:
            return queryset.filter(category__title=category_name)
        return queryset
        
    
class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    permission_classes = [IsAuthenticated, IsUserManagerOrReadOnly | IsAdminUser]
    queryset = models.MenuItem.objects.select_related('category').all()
    serializer_class = serializers.MenuItemSerializer

class ManagersView(generics.ListCreateAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    permission_classes = [IsAuthenticated, IsUserManager | IsAdminUser]
    queryset = User.objects.filter(groups__name = 'Manager').all().order_by('id')
    serializer_class = serializers.ManagersSerializer
    ordering_fields = ['username']
    search_fields = ['username']
    
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', None)
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"message": username + " does not exist in the user list"}, status=status.HTTP_404_NOT_FOUND)
            
            if user.groups.filter(name = 'Manager').exists():
                return Response({"message": "User is already a manager"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                Group.objects.get(name='Manager').user_set.add(user)
                return Response({"message": username + " is now a manager"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "A valid username is required"}, status=status.HTTP_400_BAD_REQUEST)
        
    
class SingleManagersView(generics.RetrieveDestroyAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    permission_classes = [IsAuthenticated, IsUserManager | IsAdminUser]
    queryset = User.objects.filter(groups__name = 'Manager').all().order_by('id')
    serializer_class = serializers.ManagersSerializer
    
    def destroy(self, request, *args, **kwargs):
        # not overriding this method completely erases user data instead of only removing the user from manager role
        pk = kwargs['pk']
        user = get_object_or_404(User, id=pk)
        Group.objects.get(name='Manager').user_set.remove(user)
        return Response({"message": user.username + " is removed from Managers group"}, status=status.HTTP_200_OK)
    
class DeliveryCrewView(generics.ListCreateAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    permission_classes = [IsAuthenticated, IsUserManager | IsAdminUser]
    queryset = User.objects.filter(groups__name = 'Delivery Crew').all().order_by('id')
    ordering_fields = ['username']
    search_fields = ['username']
    
    # manager serializer is used here because at the end delivery-crew and manager both are subset for User class
    serializer_class = serializers.ManagersSerializer
    
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', None)
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"message": username + " does not exist in the user list"}, status=status.HTTP_404_NOT_FOUND)
            
            if user.groups.filter(name = 'Delivery Crew').exists():
                return Response({"message": "User is already in the delivery crew"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                Group.objects.get(name='Delivery Crew').user_set.add(user)
                return Response({"message": username + " is now in the delivery crew"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "A valid username is required"}, status=status.HTTP_400_BAD_REQUEST)

class SingleDeliveryCrewView(generics.RetrieveDestroyAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    permission_classes = [IsAuthenticated, IsUserManager | IsAdminUser]
    queryset = User.objects.filter(groups__name = 'Delivery Crew').all().order_by('id')
    serializer_class = serializers.ManagersSerializer
    
    def destroy(self, request, *args, **kwargs):
        # not overriding this method completely erases user data instead of only removing the user from manager role
        pk = kwargs['pk']
        user = get_object_or_404(User, id=pk)
        Group.objects.get(name='Delivery Crew').user_set.remove(user)
        return Response({"message": user.username + " is removed from the delivery crew"}, status=status.HTTP_200_OK)
    
class CartItemsView(generics.ListCreateAPIView, generics.DestroyAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CartSerializer
    ordering_fields = ['menuitem__title', 'price']
    search_fields = ['menuitem__title']
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Cart.objects.select_related('menuitem').filter(user = self.request.user).order_by('id')
        return None
    
    def post(self, request, *args, **kwargs):
        serialized_item = serializers.CartSerializer(data = request.data)
        serialized_item.is_valid(raise_exception=True)
        menuitem_id = request.data['menuitem_id']
        quantity = request.data['quantity']
        
        try:
            menuitem = models.MenuItem.objects.get(id=menuitem_id)
        except models.MenuItem.DoesNotExist:
            return Response({"message": "item with id:" + menuitem_id + " does not exist in the menu-items list"}, status=status.HTTP_404_NOT_FOUND)
        
        price = int(quantity) * menuitem.price

        try:
            models.Cart.objects.create(user=request.user, menuitem=menuitem, quantity=quantity, unit_price=menuitem.price, price=price)
        except:
            return Response({"message": "Item already exists in the cart"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"message": "Item added to cart successfully"}, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        models.Cart.objects.filter(user = request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class OrdersView(generics.ListCreateAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.OrderSerializer
    ordering_fields = ['delivery_crew__username', 'status', 'total', 'user__username']
    search_fields = ['user__username', 'delivery_crew__username', 'order_items']
    
    def get_queryset(self):
        user = self.request.user
        queryset = models.Order.objects.prefetch_related('order_items').all().order_by('id')
        if user.is_superuser or user.groups.filter(name = 'Manager').exists():
            return queryset
        elif user.groups.filter(name = 'Delivery Crew').exists():
            return queryset.filter(user = user) | queryset.filter(delivery_crew=user)
        return queryset.filter(user=user)
    
    
    def post(self, request, *args, **kwargs):
        cart_items = models.Cart.objects.select_related('menuitem').filter(user = request.user).all()
        if not cart_items:
            return Response({"message": "Your cart is empty, please add something to place an order"}, status = status.HTTP_400_BAD_REQUEST)
        
        newOrder = models.Order.objects.create(user=request.user, total=0)
        totalOverall = decimal.Decimal(0)
        for item in cart_items:
            models.OrderItem.objects.create(order=newOrder, menuitem=item.menuitem, quantity=item.quantity, unit_price=item.unit_price, price=item.price)
            totalOverall += item.price
        cart_items.delete()
        newOrder.total = totalOverall
        newOrder.save()
        
        return Response({"message": "Order Successfully created"}, status=status.HTTP_201_CREATED)
    
class SingleOrderItemsView(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.SingleOrderSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = models.Order.objects.prefetch_related('order_items').all()
        if user.is_superuser or user.groups.filter(name = 'Manager').exists():
            return queryset
        elif user.groups.filter(name = 'Delivery Crew').exists():
            return queryset.filter(user = user) | queryset.filter(delivery_crew=user)
        return queryset.filter(user=user)
    
    # In put and patch methods,
    # manager can update 'delivery_crew', 'status'
    # delivery crew can update 'status'
    # normal customer can not update any field in the order
    def put(self, request, *args, **kwargs):
        serialized_item = serializers.SingleOrderSerializer(data = request.data)
        serialized_item.is_valid(raise_exception=True)
        
        user = request.user
        original_order = get_object_or_404(models.Order, id=kwargs['pk'])
        
        isManager = True if user.groups.filter(name='Manager').exists() or user.is_superuser else False
        isDeliveryCrew = True if user.groups.filter(name='Delivery Crew').exists() and original_order.delivery_crew == user else False
        if not isManager and not isDeliveryCrew:
            return Response({"message": "You do not have permission to change order details"}, status=status.HTTP_401_UNAUTHORIZED)

        order_status = request.POST.get('status')
        delivery_crew_username = request.POST.get('delivery_crew')
        try:
            order_status = order_status or request.data['status']
        except:
            pass
        try:
            delivery_crew_username = delivery_crew_username or request.data['delivery_crew']
        except:
            pass
                
        if isManager:
            if delivery_crew_username:
                delivery_crew_user = get_object_or_404(User, username=delivery_crew_username)
                if not delivery_crew_user.groups.filter(name = 'Delivery Crew').exists():
                    return Response({"message": delivery_crew_username + " is not part of the delivery crew"}, status=status.HTTP_400_BAD_REQUEST)
                original_order.delivery_crew = delivery_crew_user
            else:
                original_order.delivery_crew = None
        elif delivery_crew_username:
            return Response({"message": "You can not change delivery crew"}, status=status.HTTP_401_UNAUTHORIZED)
        
        if str(order_status).lower() == 'true':
            original_order.status = True
        else:
            original_order.status = False
    
        original_order.save()
        return Response({"message": "order updated successfully"}, status=status.HTTP_200_OK)
            
    def patch(self, request, *args, **kwargs):
        serialized_item = serializers.SingleOrderSerializer(data = request.data)
        serialized_item.is_valid(raise_exception=True)
        
        user = request.user
        original_order = get_object_or_404(models.Order, id=kwargs['pk'])
        
        isManager = True if user.groups.filter(name='Manager').exists() or user.is_superuser else False
        isDeliveryCrew = True if user.groups.filter(name='Delivery Crew').exists() and original_order.delivery_crew == user else False
        if not isManager and not isDeliveryCrew:
            return Response({"message": "You do not have permission to change order details"}, status=status.HTTP_401_UNAUTHORIZED)

        order_status = request.POST.get('status')
        delivery_crew_username = request.POST.get('delivery_crew')
        try:
            order_status = order_status or request.data['status']
        except:
            pass
        try:
            delivery_crew_username = delivery_crew_username or request.data['delivery_crew']
        except:
            pass
                
        if isManager:
            if delivery_crew_username:
                delivery_crew_user = get_object_or_404(User, username=delivery_crew_username)
                if not delivery_crew_user.groups.filter(name = 'Delivery Crew').exists():
                    return Response({"message": delivery_crew_username + " is not part of the delivery crew"}, status=status.HTTP_400_BAD_REQUEST)
                original_order.delivery_crew = delivery_crew_user
            else:
                original_order.delivery_crew = None
        elif delivery_crew_username:
            return Response({"message": "You can not change delivery crew"}, status=status.HTTP_401_UNAUTHORIZED)
        
        if str(order_status).lower() == 'true':
            original_order.status = True
        else:
            original_order.status = False
    
        original_order.save()
        return Response({"message": "order updated successfully"}, status=status.HTTP_200_OK)
    
    # only manager can perform the delete action
    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.groups.filter(name = 'Manager').exists():
            return super().destroy(request, *args, **kwargs)
        return Response({"message": "Only manager or admin can delete an order"}, status=status.HTTP_401_UNAUTHORIZED)

















################# INITIAL VERSION CODES, TO BE IGNORED #####################

# @api_view()
# def trialFunc(request, menuItem=0):
#     return Response('trial function ' + str(menuItem), status=status.HTTP_404_NOT_FOUND)    

# @api_view()
# @permission_classes([IsAuthenticated])
# def authTrialFunc(request):
#     return Response({"message": "secret message"})

# @api_view()
# @permission_classes([IsAuthenticated])
# def authorisationTrialFunc(request):
#     if request.user.groups.filter(name='Manager').exists():
#         return Response({"message": "Only managers can see this"}, status=status.HTTP_200_OK)
#     else:
#         return Response({"message": "You are not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

# @api_view(['GET', 'POST', 'DELETE'])
# @permission_classes([IsAuthenticated])
# def cartItems(request):
#     if request.method == 'GET':
#         items = models.Cart.objects.select_related('menuitem').filter(user = request.user)
#         serialized_item = serializers.CartSerializer(items, many=True)
#         return Response(serialized_item.data)
#     elif request.method == 'POST':
#         serialized_item = serializers.CartSerializer(data = request.data)
#         serialized_item.is_valid(raise_exception=True)
#         serialized_item.save()
#         return Response(serialized_item.validated_data, status.HTTP_201_CREATED)
#     elif request.method == 'DELETE':
#         items = models.Cart.objects.select_related('menuitem').filter(user = request.user).delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#     return Response(status=status.HTTP_404_NOT_FOUND)

# class OrderItemsView(generics.ListCreateAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = serializers.OrderItemSerializer
    
#     def get_queryset(self):
#         if self.request.user.groups.filter(name = 'Manager').exists():
#             return models.OrderItem.objects.all()
#         elif self.request.user.groups.filter(name = 'Delivery Crew').exists():
#             return models.OrderItem.objects.filter(delivery_crew = self.request.user)
#         return models.OrderItem.objects.filter(user = self.request.user)

#     def post(self, request, *args, **kwargs):
        
#         cart_items = models.Cart.objects.filter(user = request.user).all()
#         if not cart_items:
#             return Response({"message": "Your cart is empty, please add something to place an order"}, status = status.HTTP_400_BAD_REQUEST)
        
#         newOrder = models.Order.objects.create(user=request.user, total=0)
#         totalOverall = decimal.Decimal(0)
#         for item in cart_items:
#             models.OrderItem.objects.create(order=newOrder, menuitem=item.menuitem, quantity=item.quantity, unit_price=item.unit_price, price=item.price)
#             totalOverall += item.price
#         cart_items.delete()
#         newOrder.total = totalOverall
#         newOrder.save()
        
#         return Response({"message": "Order Successfully created"}, status=status.HTTP_201_CREATED)