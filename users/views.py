from django.shortcuts import render
from rest_framework.decorators import api_view

from users.models import MyUser
from users.serializers import UserSerializer


# Create your views here.


@api_view(['GET'])
def user_list(request, ):
	users = MyUser.objects.all().order_by('username')
	serializer = UserSerializer(instance=users, many=True)
	from rest_framework.response import Response
	return Response(serializer.data)

