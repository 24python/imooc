# _*_ coding:utf-8 _*_
# django 自带的form验证，可在view之前对用户输入信息进行验证
# 字段名称必须同页面input的名称一致

from django import forms
from captcha.fields import CaptchaField

from .models import UserProfile


class LoginForm(forms.Form):
    """登录信息验证"""
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, min_length=5)


class RegisterForm(forms.Form):
    """注册信息验证"""
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=5)
    captcha = CaptchaField(error_messages={'invalid': '验证码错误！'})  # 验证用户输入的验证码,抛出异常可自定义


class ForgetForm(forms.Form):
    """找回密码信息验证"""
    email = forms.EmailField(required=True)
    captcha = CaptchaField(error_messages={'invalid': '验证码错误！'})


class ModifyPwdForm(forms.Form):
    """重置密码信息验证"""
    password1 = forms.CharField(required=True, min_length=5)
    password2 = forms.CharField(required=True, min_length=5)


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['nick_name', 'gender', 'birthday', 'address', 'mobile']