from fileinput import filename
from rest_framework import serializers

from account.models import Account, Upload, FileTest


class RegistrationSerializer(serializers.ModelSerializer):

	password2 				= serializers.CharField(style={'input_type': 'password'}, write_only=True)

	class Meta:
		model = Account
		fields = ['email', 'username', 'password', 'password2']
		extra_kwargs = {
				'password': {'write_only': True},
		}	


	def	save(self):

		account = Account(
					email=self.validated_data['email'],
					username=self.validated_data['username']
				)
		password = self.validated_data['password']
		password2 = self.validated_data['password2']
		if password != password2:
			raise serializers.ValidationError({'password': 'Passwords must match.'})
		account.set_password(password)
		account.save()
		return account


class AccountPropertiesSerializer(serializers.ModelSerializer):

	class Meta:
		model = Account
		fields = ['pk', 'email', 'username', ]




class ChangePasswordSerializer(serializers.Serializer):

	old_password 				= serializers.CharField(required=True)
	new_password 				= serializers.CharField(required=True)
	confirm_new_password 		= serializers.CharField(required=True)





def UPLOADED_FILES_USE_URL(instance, filename):
	return "test/{filename}".format({
		filename : filename
	})
# class UploadSerializer(serializers.Serializer):
# 	upload 						= serializers.ImageField(max_length=None, allow_empty_file=False, use_url=UPLOADED_FILES_USE_URL)






class UploadSerializer(serializers.ModelSerializer):

	class Meta:

		model = Upload
		fields = '__all__'


class FileTestSerializer(serializers.ModelSerializer):

	class Meta:

		model = FileTest
		fields = '__all__'