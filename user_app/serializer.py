from rest_framework import serializers
from .models import User, Farmer, Processor

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class FarmerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Farmer
        fields = '__all__'

class ProcessorSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Processor
        fields = '__all__'
