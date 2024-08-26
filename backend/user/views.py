from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from .models import User
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.response import Response

class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        # Fetch the data
        email = request.data.get('email')
        username = request.data.get('username')
        employee_id = request.data.get('employee_id')

        # Check if email, username, or employee_id already exists
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(employee_id=employee_id).exists():
            return Response({'error': 'Employee ID already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Use serializer to validate and save user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Respond with user data and tokens
        return Response({
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "employee_id": user.employee_id,
                "username": user.username,
            },
            "token": {
                "access": access_token,
                "refresh": refresh_token
            }
        }, status=status.HTTP_201_CREATED)


class LoginUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
            username = request.data.get('username')
            password = request.data.get('password')

            user = get_object_or_404(User, username=username)

            if not user.check_password(password):
                return Response(
                    {
                        'error': 'Invalid Credentials'
                    }, status=status.HTTP_401_UNAUTHORIZED
                    )

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response(
                {
                    'user': {
                        'id': user.id,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                        'employee_id': user.employee_id,
                        'username': user.username,
                    },
                    'token': {
                        'access': access_token,
                        'refresh': refresh_token
                    }
                }, status=status.HTTP_200_OK
            )
            
            
class LogoutUserView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh_token')
        
        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {
                    'message': 'User Logged Out Successfuly'
                },
                status=status.HTTP_205_RESET_CONTENT
            )
        except InvalidToken:
            return Response(
                {
                    'error': 'Invalid Token'
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )