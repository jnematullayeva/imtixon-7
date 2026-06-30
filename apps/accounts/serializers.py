from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password2',
            'first_name', 'last_name', 'phone', 'date_of_birth',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'Parollar mos kelmadi.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    master_profile_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'date_of_birth', 'avatar', 'is_master',
            'master_profile_id', 'is_active', 'is_staff', 'date_joined',
        ]
        read_only_fields = ['id', 'username', 'is_master', 'is_staff', 'is_active', 'date_joined']

    def get_master_profile_id(self, obj):
        profile = getattr(obj, 'master_profile', None)
        return profile.id if profile else None


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'date_of_birth', 'avatar', 'is_master',
            'is_active', 'is_staff', 'date_joined',
        ]
        read_only_fields = ['id', 'date_joined']
