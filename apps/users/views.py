from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout  # authentucate验证用户名、密码是否匹配的模块
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.views.generic.base import View
from django.contrib.auth.hashers import make_password  # 对明文进行加密
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.core.urlresolvers import reverse

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from .models import UserProfile, EmailVerifyRecord, Banner
from .forms import LoginForm, RegisterForm, ForgetForm, ModifyPwdForm, UploadImageForm, UserInfoForm
from utils.email_send import send_register_email
from utils.mixin_utils import LoginRequiredMixin
from operation.models import UserCourse, UserFavorite, UserMessage
from organization.models import CourseOrg, Teacher
from courses.models import Course

import json

# Create your views here.


# 让用户可以用邮箱登录
# setting 里要有对应的配置

class CustomBackend(ModelBackend):
    """重定义user，实现邮箱登录功能"""
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            # 将判断结果作为对象，返回给user，使用get
            # 方法，确认只有一个用户，如果有多个用户会失败
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            # 使用的UserProfile继承的是AbstractUser类，有check_password方法
            # 将明文password传到后台同数据库中的密文密码做对比，验证是否一致
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class LoginView(View):
    """用户登录"""
    def get(self, request):  # view 方法，常用的就是get和post
        return render(request, 'login.html')

    def post(self, request):
        login_form = LoginForm(request.POST)  # 参数为字典，将用户输入的用户名和密码传入form进行判断
        if login_form.is_valid():              # form的方法，判断form验证的结果
            user_name = request.POST.get('username', '')
            password = request.POST.get('password', '')
            # 上面的 authenticate 方法 return user
            user = authenticate(username=user_name, password=password)  # 用户名、密码登录，django自带的用户名、密码验证，参数名称固定

            if user is not None:
                if user.is_active:
                    login(request, user)  # 如果登录成功，django会在request里面添加登录信息，在数据库中生成用户id
                    return HttpResponsePermanentRedirect(reverse('index'))
                return render(request, 'login.html', {'msg': '用户未激活！'})
            return render(request, 'login.html', {'msg': '用户名或者密码错误！'})
        else:
            return render(request, 'login.html', {'form_errors': login_form.errors})


#用户登出
class LogoutView(View):
    def get(self, request):
        logout(request)   # django内置登出方法
        return HttpResponsePermanentRedirect(reverse('index'))


class RegisterView(View):
    """用户注册功能"""
    def get(self, request):
        # get 请求的时候，把验证码组件一系列的 HTML render 到 register.html 里
        register_form = RegisterForm()
        return render(request, 'register.html', {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)  # 通过POST方式传入参数，字典
        if register_form.is_valid():  # form验证邮箱、密码是否符合要求，验证成功后执行注册

            # 获取用户输入的邮箱及密码
            email = request.POST.get('email', '')
            if UserProfile.objects.filter(email=email):
                return render(request, 'register.html', {'register_form': register_form, 'msg': '用户已经存在！'})
            password = request.POST.get('password', '')

            # 将用户注册信息保存到数据库中
            user_profile = UserProfile()
            user_profile.username = email
            user_profile.email = email
            user_profile.password = make_password(password)  # 对明文密码进行加密
            user_profile.is_active = False  # django 自带的is_active字段，非UserProfile()定义
            user_profile.save()

            # 注册时发送一条消息
            user_message = UserMessage()
            user_message.user = user_profile.id
            user_message.message = '欢迎注册在线学习网！'
            user_message.save()

            send_register_email(email, 'register')
            return render(request, 'send_success.html')
        else:
            return render(request, 'register.html', {'register_form': register_form})


class ActiveUserView(View):
    """
    激活判断，用户点击邮箱里的链接后调用
    """
    def get(self, request, active_code):
        # 为什么用 filter ？ ---因为用户可能注册了好多次，一个 email 对应了好多个 code
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for records in all_records:
                email = records.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
                return render(request, 'login.html')
        else:
            return render(request, 'active_fail.html')


class ForgetPwdView(View):
    """忘记密码的链接"""
    def get(self, request):
        forget_form = ForgetForm()
        return render(request, 'forgetpwd.html', {'forget_form': forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)    # 进行form判断
        if forget_form.is_valid():
            email = request.POST.get('email', '')
            send_register_email(email, 'forget')
            return render(request, 'send_success.html')
        else:
            return render(request, 'forgetpwd.html', {'forget_form': forget_form})


class ResetView(View):
    """用户点击邮件里的密码重置链接"""
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for records in all_records:
                email = records.email
                # EmailVerifyRecord.objects.delete(code=active_code) # 删除数据库中的验证码记录，再次点击时无效
                return render(request, 'password_reset.html', {'email': email})
        else:
            return render(request, 'active_fail.html')


class ModifyPwdView(View):
    """密码重置页面，接收用户提交的新密码"""
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        email = request.POST.get('email', '')
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            if pwd1 != pwd2:
                return render(request, 'password_reset.html', {'email': email, 'msg': '密码不一致！'})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd2)
            user.save()
            return render(request, 'login.html')
        return render(request, 'password_reset.html', {'email': email, 'modify_form': modify_form})


# userprofile
class UserInfoView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'usercenter-info.html')

    # 用户修改昵称，手机号，地址，生日
    def post(self, request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        res = dict()

        if user_info_form.is_valid():
            user_info_form.save()
            res['status'] = 'success'

        else:
            res = user_info_form.errors

        return HttpResponse(json.dumps(res), content_type='application/json')


# 用户修改头像
class UploadImageView(LoginRequiredMixin, View):
    def post(self, request):
        # image_form = UploadImageForm(request.POST, request.FILES)
        # if image_form.is_valid():
        #     image = image_form.cleaned_data['image']
        #     request.user.image = image
        #     request.user.save()
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        res = dict()
        if image_form.is_valid():
            image_form.save()
            res['status'] = 'success'
            res['msg'] = '头像修改成功'
        else:
            res['status'] = 'fail'
            res['msg'] = '头像修改失败'
        return HttpResponse(json.dumps(res), content_type='application/json')


#用户修改密码
# 用户在个人中心修改密码
class UpdatePwdView(LoginRequiredMixin, View):
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        res = dict()

        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            if pwd1 != pwd2:
                res['status'] = 'fail'
                res['msg'] = '两次密码不一致'
                return HttpResponse(json.dumps(res), content_type='application/json')

            user = request.user
            user.password = make_password(pwd2)
            user.save()

            res['status'] = 'success'
            res['msg'] = '密码修改成功'
        else:
            res = modify_form.errors

        return HttpResponse(json.dumps(res), content_type='application/json')


# 发送修改邮箱时的邮箱验证码
class SendEmailCodeView(LoginRequiredMixin, View):
    def get(self, request):
        email = request.GET.get('email', '')

        res = dict()
        if UserProfile.objects.filter(email=email):
            res['email'] = '邮箱已注册'
            return HttpResponse(json.dumps(res), content_type='application/json')
        send_register_email(email, 'update_email')
        res['status'] = 'success'
        res['msg'] = '发送验证码成功'
        return HttpResponse(json.dumps(res), content_type='application/json')


# 修改个人邮箱
class UpdateEmailView(LoginRequiredMixin, View):
    def post(self, request):
        email = request.POST.get('email', '')
        code = request.POST.get('code', '')

        existed_records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type='update_email')
        res = dict()
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            res['status'] = 'success'
            res['msg'] = '邮箱修改成功！'
        else:
            res['status'] = 'fail'
            res['msg'] = '验证码出错！'

        return HttpResponse(json.dumps(res), content_type='application/json')


# 我的课程
class MyCourseView(LoginRequiredMixin, View):
    def get(self, request):
     user_courses = UserCourse.objects.filter(user=request.user)
     return render(request, 'usercenter-mycourse.html', {
         'user_courses': user_courses,
     })


# 我收藏的课程机构
class MyFavOrgView(LoginRequiredMixin, View):
    def get(self, request):
     org_list = []
     fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
     for fav_org in fav_orgs:
         org_id = fav_org.fav_id
         org = CourseOrg.objects.get(id=org_id)
         org_list.append(org)
     return render(request, 'usercenter-fav-org.html', {
         'org_list': org_list,
     })


# 我收藏的授课讲师
class MyFavTeacherView(LoginRequiredMixin, View):
    def get(self, request):
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            teacher_id = fav_teacher.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)
        return render(request, 'usercenter-fav-teacher.html', {
            'teacher_list': teacher_list,
        })


# 我收藏的课程
class MyFavCourseView(LoginRequiredMixin, View):
    def get(self, request):
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            course = Course.objects.get(id=course_id)
            course_list.append(course)
        return render(request, 'usercenter-fav-course.html', {
            'course_list': course_list,
        })


# 我的消息
class MyMessageView(LoginRequiredMixin, View):
    def get(self, request):
        # 如果 user = 0 ，代表全局消息，所有用户都能收到
        all_message = UserMessage.objects.filter(user=request.user.id)

        #进入到我的消息页面后，把已读的消息清空
        all_unread_message = UserMessage.objects.filter(user=request.user.id, has_read=False)
        for unread_message in all_unread_message:
            unread_message.has_read = True
            unread_message.save()

        # 对个人消息分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_message, 2, request=request)
        messages = p.page(page)

        return render(request, 'usercenter-message.html', {
            'messages': messages,
        })


# 在线网首页
class IndexView(View):
    def get(self, request):
        # 取出轮播图
        all_banners = Banner.objects.all().order_by('index')
        courses = Course.objects.filter(is_banner=False)[:6]
        banner_courses = Course.objects.filter(is_banner=True)[:3]
        course_orgs = CourseOrg.objects.all()[:15]
        return render(request, 'index.html', {
            'all_banners': all_banners,
            'courses': courses,
            'banner_courses': banner_courses,
            'course_orgs': course_orgs,
        })


# 全局 404 处理函数
def page_not_found(request):
    from django.shortcuts import render_to_response
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response


# 全局 500 处理函数
def page_error(request):
    from django.shortcuts import render_to_response
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response