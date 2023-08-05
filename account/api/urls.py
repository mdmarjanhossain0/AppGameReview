from django.urls import path
from account.api.views import(
	registration_view,
	ObtainAuthTokenView,
	account_properties_view,
	update_account_view,
	does_account_exist_view,
	ChangePasswordView,
	SessionLogInView,
	upload_image,
	test
)
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'account'

urlpatterns = [
	path('check_if_account_exists/', does_account_exist_view, name="check_if_account_exists"),
	path('change_password/', ChangePasswordView.as_view(), name="change_password"),
	path('properties', account_properties_view, name="properties"),
	path('properties/update', update_account_view, name="update"),
 	path('login', ObtainAuthTokenView.as_view(), name="login"), 
	path('register', registration_view, name="register"),
	path('logins', SessionLogInView.as_view(), name="session_login"),
	path("upload", upload_image, name="upload"),

	path("test", test, name="test")
]