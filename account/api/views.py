import email
from fileinput import filename
from numpy import unicode_
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication, BaseAuthentication, SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from account.api.serializers import (
	 RegistrationSerializer, 
	 AccountPropertiesSerializer, 
	 ChangePasswordSerializer,
	 UploadSerializer,
	 FileTestSerializer
)
from account.models import Account
from rest_framework.authtoken.models import Token

from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate, get_user_model, login

# Register
# Response: https://gist.github.com/mitchtabian/c13c41fa0f51b304d7638b7bac7cb694
# Url: https://<your-domain>/api/account/register
@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def registration_view(request):

	if request.method == 'POST':
		data = {}
		email = request.data.get('email', '0').lower()
		if validate_email(email) != None:
			data['error_message'] = 'That email is already in use.'
			data['response'] = 'Error'
			return Response(data)

		username = request.data.get('username', '0')
		if validate_username(username) != None:
			data['error_message'] = 'That username is already in use.'
			data['response'] = 'Error'
			return Response(data)

		serializer = RegistrationSerializer(data=request.data)
		
		if serializer.is_valid():
			account = serializer.save()
			data['response'] = 'successfully registered new user.'
			data['email'] = account.email
			data['username'] = account.username
			data['pk'] = account.pk
			token = Token.objects.get(user=account).key
			data['token'] = token
		else:
			data = serializer.errors
		return Response(data)

def validate_email(email):
	account = None
	try:
		account = Account.objects.get(email=email)
	except Account.DoesNotExist:
		return None
	if account != None:
		return email

def validate_username(username):
	account = None
	try:
		account = Account.objects.get(username=username)
	except Account.DoesNotExist:
		return None
	if account != None:
		return username


# Account properties
# Response: https://gist.github.com/mitchtabian/4adaaaabc767df73c5001a44b4828ca5
# Url: https://<your-domain>/api/account/
# Headers: Authorization: Token <token>
@api_view(['GET', ])
@permission_classes((IsAuthenticated, ))
def account_properties_view(request):

	try:
		account = request.user
	except Account.DoesNotExist:
		return Response(status=status.HTTP_404_NOT_FOUND)

	if request.method == 'GET':
		serializer = AccountPropertiesSerializer(account)
		return Response(serializer.data)


# Account update properties
# Response: https://gist.github.com/mitchtabian/72bb4c4811199b1d303eb2d71ec932b2
# Url: https://<your-domain>/api/account/properties/update
# Headers: Authorization: Token <token>
@api_view(['PUT',])
@permission_classes((IsAuthenticated, ))
def update_account_view(request):

	try:
		account = request.user
	except Account.DoesNotExist:
		return Response(status=status.HTTP_404_NOT_FOUND)
		
	if request.method == 'PUT':
		serializer = AccountPropertiesSerializer(account, data=request.data)
		data = {}
		if serializer.is_valid():
			serializer.save()
			data['response'] = 'Account update success'
			return Response(data=data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# LOGIN
# Response: https://gist.github.com/mitchtabian/8e1bde81b3be342853ddfcc45ec0df8a
# URL: http://127.0.0.1:8000/api/account/login
class ObtainAuthTokenView(APIView):

	authentication_classes = []
	permission_classes = []

	def post(self, request):
		context = {}

		email = request.POST.get('username')
		password = request.POST.get('password')
		account = authenticate(email=email, password=password)
		if account:
			try:
				token = Token.objects.get(user=account)
			except Token.DoesNotExist:
				token = Token.objects.create(user=account)
			context['response'] = 'Successfully authenticated.'
			context['pk'] = account.pk
			context['email'] = email.lower()
			context['token'] = token.key
		else:
			context['response'] = 'Error'
			context['error_message'] = 'Invalid credentials'

		return Response(context)





class ExampleAuthentication(BaseAuthentication):

	def authenticate(self, request):

		# Get the username and password
		email = request.data.get('username', None)
		password = request.data.get('password', None)

		if not email or not password:
			raise AuthenticationFailed('No credentials provided.')

		user = authenticate(email=email, password=password)

		if user is None:
			raise AuthenticationFailed('Invalid username/password.')

		if not user.is_active:
			raise AuthenticationFailed('User inactive or deleted.')

		return (user, None)  # authentication successful


class SessionLogInView(APIView):
	authentication_classes = (SessionAuthentication, ExampleAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, format=None):    
		login(request, request.user)
		content = {
			'user': unicode_(request.user),
			'auth': unicode_(request.auth),  # None
		}
		return Response(content)




@api_view(['GET', ])
@permission_classes([])
@authentication_classes([])
def does_account_exist_view(request):

	if request.method == 'GET':
		email = request.GET['email'].lower()
		data = {}
		try:
			account = Account.objects.get(email=email)
			data['response'] = email
		except Account.DoesNotExist:
			data['response'] = "Account does not exist"
		return Response(data)



class ChangePasswordView(UpdateAPIView):

	serializer_class = ChangePasswordSerializer
	model = Account
	permission_classes = (IsAuthenticated,)
	authentication_classes = (TokenAuthentication,)

	def get_object(self, queryset=None):
		obj = self.request.user
		return obj

	def update(self, request, *args, **kwargs):
		self.object = self.get_object()
		serializer = self.get_serializer(data=request.data)

		if serializer.is_valid():
			# Check old password
			if not self.object.check_password(serializer.data.get("old_password")):
				return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

			# confirm the new passwords match
			new_password = serializer.data.get("new_password")
			confirm_new_password = serializer.data.get("confirm_new_password")
			if new_password != confirm_new_password:
				return Response({"new_password": ["New passwords must match"]}, status=status.HTTP_400_BAD_REQUEST)

			# set_password also hashes the password that the user will get
			self.object.set_password(serializer.data.get("new_password"))
			self.object.save()
			return Response({"response":"successfully changed password"}, status=status.HTTP_200_OK)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)












from .utils import save_file
# @api_view(['POST', ])
# @permission_classes([])
# @authentication_classes([])
# def upload_image(request):

# 	if request.method == 'POST':
# 		serializer = UploadSerializer(data=request.data)

# 		if serializer.is_valid():
# 			file_name = request.data["upload"].name
# 			print(file_name)
# 			print(serializer.data)
# 			file_path = 'image/'
# 			url = save_file(request.data["upload"], file_path=file_path, file_name=file_name)
# 			print(url)
# 			return Response({
# 				"uploaded" : True,
# 				"url" : "http://127.0.0.1:8000/" + url
# 			})
# 		else:
# 			return Response({
# 				"uploaded" : False,
# 				"url" : ""
# 			}, status=400)


@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def upload_image(request):

	if request.method == 'POST':
		serializer = UploadSerializer(data=request.data)

		if serializer.is_valid():
			data = serializer.save()
			return Response({
				"uploaded" : True,
				"url" : "https://educodiv.com" + data.upload.url
			})
		else:
			return Response({
				"uploaded" : False,
				"url" : ""
			}, status=400)





@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def file_test_view(request):

	if request.method == 'POST':
		serializer = FileTestSerializer(data=request.data)

		if serializer.is_valid():
			data = serializer.save()
			return Response({
				"uploaded" : True,
				"url" : "https://playreviewhub.com" + data.file.url
			})
		else:
			return Response({
				"uploaded" : False,
				"url" : ""
			}, status=400)





@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def test(request):

	if request.method == 'POST':
		print(request.data)
		return Response({})





