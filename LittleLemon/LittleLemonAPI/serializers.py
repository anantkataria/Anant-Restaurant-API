from rest_framework import serializers
from . import models
from django.contrib.auth.models import User, Group

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['id', 'slug', 'title']
        extra_kwargs = {
            'id' : {'read_only': True},
        }
        
    def __str__(self) -> str:
        return self.title
        
class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(read_only = True)
    category_id = serializers.IntegerField(min_value=1, max_value=5)
    class Meta:
        model = models.MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']
        
class ManagersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        extra_kwargs = {
            'id' : {'read_only': True},
            'email' : {'read_only': True},
        }
        
class CartSerializer(serializers.ModelSerializer):
    menuitem = serializers.StringRelatedField(read_only=True)
    menuitem_id = serializers.IntegerField()
    class Meta:
        model = models.Cart
        fields = ['menuitem', 'menuitem_id', 'quantity', 'unit_price', 'price']
        extra_kwargs = {
            'price' : {'read_only': True},
            'unit_price' : {'read_only': True},
        }
    
class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.StringRelatedField(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    delivery_crew = serializers.StringRelatedField(read_only=True)
    class Meta():
        model = models.Order
        fields = ['id', 'user', 'order_items', 'total', 'status', 'delivery_crew', 'date']
        extra_kwargs = {
            'total' : {'read_only': True},
            'status': {'read_only': True},
            'date': {'read_only': True},
        }
        
class SingleOrderSerializer(serializers.ModelSerializer):
    order_items = serializers.StringRelatedField(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    delivery_crew = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    class Meta():
        model = models.Order
        fields = ['id', 'user', 'order_items', 'total', 'status', 'delivery_crew', 'date']
        extra_kwargs = {
            'total' : {'read_only': True},
            'date' : {'read_only': True},
        }   