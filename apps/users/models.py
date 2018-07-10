# _*_ coding:utf-8 _*_
# 包的引用规则：
# 第一区域为Python自带包
# 第二区域为第三方包（如Django等）
# 第三区域为自己定义的包

from datetime import datetime

from django.db import models

from django.contrib.auth.models import AbstractUser


# Create your models here.
# 此APP为用户信息管理，包含用户的基本信息、邮箱验证、轮播图，其中后两部分为单独模块，放到这里一起处理


class UserProfile(AbstractUser):
    """
    继承AbstractUser类
    创建用户基本信息模型
    """
    nick_name = models.CharField(max_length=50, verbose_name='昵称', default='')
    birthday = models.DateField(null=True, blank=True, verbose_name='生日')
    gender = models.CharField(max_length=6, choices=(('male', '男'), ('female', '女')), default='female',
                              verbose_name='性别')
    address = models.CharField(max_length=100, default='', verbose_name='地址')
    mobile = models.CharField(max_length=11, null=True, blank=True, verbose_name='手机号')
    image = models.ImageField(max_length=100, upload_to='image/%Y/%m', default='image?default.png', verbose_name='头像')

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def get_unread_nums(self):
        """
        从用户操作管理引入用户消息，显示未读消息总数
        """
        # 获取用户未读数据数量
        from operation.models import UserMessage
        return UserMessage.objects.filter(user=self.id, has_read=False).count()

    def __str__(self):
        return self.username


class EmailVerifyRecord(models.Model):
    """
    邮箱验证，用于注册、修改/找回密码时使用
    """
    code = models.CharField(max_length=20, verbose_name='验证码')
    email = models.EmailField(max_length=50, verbose_name='邮箱')
    send_type = models.CharField(max_length=18,
                                 choices=(('register', '邮箱'), ('forget', '修改密码'), ('update_email', '修改邮箱')),
                                 verbose_name='验证码类型')
    send_time = models.DateField(default=datetime.now, verbose_name='发送时间')
    # 使用now()时，如果带括号将引用模块编写的时间生成默认时间
    # 去掉()，则根据实例化的时间为默认时间

    class Meta:
        verbose_name = '邮箱验证码'
        verbose_name_plural = '邮箱验证码'


class Banner(models.Model):
    """
    轮播图，用于首页展示
    """
    title = models.CharField(max_length=100, verbose_name='标题')
    image = models.ImageField(upload_to='banner/%Y/%m', max_length=100, verbose_name='轮播图')
    url = models.URLField(max_length=200, verbose_name='访问地址')
    index = models.IntegerField(default=100, verbose_name='顺序')
    add_time = models.DateField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '轮播图'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title
