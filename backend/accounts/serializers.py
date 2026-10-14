from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class LoginSerializer(TokenObtainPairSerializer):
    username_field = "username"

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.get_username()
        token["email"] = user.email
        return token


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = __import__("django.contrib.auth", fromlist=["get_user_model"]).get_user_model()
        fields = ("id", "username", "email", "first_name", "last_name", "is_staff")
        read_only_fields = fields


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    password_confirm = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_username(self, value):
        from django.contrib.auth import get_user_model
        if get_user_model().objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Usuário já cadastrado.")
        return value

    def validate_email(self, value):
        from django.contrib.auth import get_user_model
        if get_user_model().objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("E-mail já cadastrado.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "As senhas não coincidem."})
        return attrs

    def create(self, validated_data):
        from django.contrib.auth import get_user_model
        validated_data.pop("password_confirm")
        return get_user_model().objects.create_user(**validated_data)
