# _*_ coding:utf-8 _*_
# 包的引用规则：
# 第一区域为Python自带包
# 第二区域为第三方包（如Django等）
# 第三区域为自己定义的包
from datetime import datetime

from django.db import models

from users.models import UserProfile
from courses.models import Course
# Create your models here.


class UserAsk(models.Model):
    """
    用户咨询的小窗口模块
    """
    name = models.CharField(max_length=20, verbose_name='姓名')
    mobile = models.CharField(max_length=11, verbose_name='手机号')
    course_name = models.CharField(max_length=50, verbose_name='课程名')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '用户咨询'
        verbose_name_plural = verbose_name


class CourseComments(models.Model):
    """
    用户对课程的评论模块
    """
    user = models.ForeignKey(UserProfile, verbose_name='用户')
    course = models.ForeignKey(Course, verbose_name='课程')
    comments = models.CharField(max_length=200, verbose_name='评论')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '课程评论'
        verbose_name_plural = verbose_name


class UserFavorite(models.Model):
    """
    用户收藏的模块，可实现对课程、机构、讲师的收藏
    """
    user = models.ForeignKey(UserProfile, verbose_name='用户')
    # ID 是课程的 ID 或者是 讲师、课程机构的 ID
    fav_id = models.IntegerField(default=0, verbose_name='收藏数据 Id')
    fav_type = models.IntegerField(choices=( (1, '课程'), (2, '课程机构'), (3, '讲师') ), default=1, verbose_name='收藏类型')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '用户收藏'
        verbose_name_plural = verbose_name

    # 初始化判断是否收藏
    # has_fav = False
    # if request.user.is_authenticated():
    #     if UserProfile.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
    #         has_fav = True


class UserMessage(models.Model):
    """
    用户消息管理
    """
    # 如果 为 0 代表全局消息，否则就是用户的 ID
    user = models.IntegerField(default=0, verbose_name='接受用户')
    message = models.CharField(max_length=500, verbose_name='消息内容')
    has_read = models.BooleanField(default=False, verbose_name='是否已读')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '用户消息'
        verbose_name_plural = verbose_name


# CourseComments 和 UserCourse 字段差不多，可以使用 UserCourse 继承 CourseComments
class UserCourse(models.Model):
    """
    用户学习过的课程模块
    """
    user = models.ForeignKey(UserProfile, verbose_name='用户')
    course = models.ForeignKey(Course, verbose_name='课程')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '用户学习过的课程'
        verbose_name_plural = verbose_name

