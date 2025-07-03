from django.contrib.auth.models import User, Group
from rest_framework import serializers
from django.contrib.auth.hashers import make_password

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')

class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    group_ids = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        many=True,
        write_only=True,
        source='groups',
        allow_empty=True,
        required=False
    )
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = [
            'id', 'username', 'password', 'password_confirm', 'first_name',
            'last_name', 'email', 'is_staff', 'is_active',
            'groups', 'group_ids', 'date_joined', 'last_login'
        ]
        read_only_fields = ('date_joined', 'last_login')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        if not self.instance and not password:
            raise serializers.ValidationError({"password": "La contraseña es requerida para nuevos usuarios."})
        if password or password_confirm:
            if password != password_confirm:
                raise serializers.ValidationError({"password_confirm": "Las contraseñas no coinciden."})
        attrs.pop('password_confirm', None)
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        group_objs = validated_data.pop('groups', [])
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        if group_objs:
            user.groups.set(group_objs)
        return User.objects.get(pk=user.pk)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        group_objs = validated_data.pop('groups', None)
        if password:
            instance.set_password(password)
        if group_objs is not None:
            instance.groups.set(group_objs)
        instance = super().update(instance, validated_data)
        instance.save()
        return User.objects.get(pk=instance.pk)
