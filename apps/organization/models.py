# _*_ coding:utf-8 _*_
# 包的引用规则：
# 第一区域为Python自带包
# 第二区域为第三方包（如Django等）
# 第三区域为自己定义的包

from datetime import datetime

from django.db import models

# Create your models here.


class CityDict(models.Model):
    """
    城市管理模块
    """
    name = models.CharField(max_length=20, verbose_name='城市')
    desc = models.TextField(verbose_name='城市描述')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '城市'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CourseOrg(models.Model):
    """
    课程机构信息
    """
    name = models.CharField(max_length=50, verbose_name='机构名称')
    category = models.CharField(max_length=20, choices=(('pxjg', '培训机构'), ('gr', '个人'), ('gx', '高校')),
                                default='pxjg', verbose_name='机构类别')
    desc = models.TextField(verbose_name='机构描述')
    tag = models.CharField(default=u'全国知名', max_length=10, verbose_name=u'机构标签')
    click_nums = models.IntegerField(default=0, verbose_name='点击数')
    fav_nums = models.IntegerField(default=0, verbose_name='收藏数')
    image = models.ImageField(default='', upload_to='org/%Y/%m', verbose_name='封面图', max_length=100)
    address = models.CharField(max_length=150, verbose_name='机构地址')
    city = models.ForeignKey(CityDict, verbose_name='所在城市')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')
    students = models.IntegerField(default=0, verbose_name='学习人数')

    class Meta:
        verbose_name = '课程机构'
        verbose_name_plural = verbose_name

    def get_teacher_nums(self):
        """
        获取该机构所有的讲师数量
        :return:
        """
        return self.teacher_set.all().count()

    def course_nums(self):
        """
        获取该机构所有的课程数量
        :return:
        """
        return self.course_set.all().count()

    def __str__(self):
        return self.name


class Teacher(models.Model):
    """
    讲师基本信息模块
    """
    org = models.ForeignKey(CourseOrg, verbose_name='所属机构')
    name = models.CharField(max_length=50, verbose_name='教师名字')
    work_years = models.IntegerField(default=0, max_length=60, verbose_name='工作年限')
    work_company = models.CharField(max_length=50, verbose_name='就职公司')
    work_position = models.CharField(max_length=50, verbose_name='公司职位')
    points = models.CharField(max_length=50, verbose_name='教学特点')
    click_nums = models.IntegerField(default=0, verbose_name='点击数')
    fav_nums = models.IntegerField(default=0, verbose_name='收藏数')
    age = models.IntegerField(default=30, max_length=100, verbose_name='年龄')
    image = models.ImageField(default='', upload_to='teacher/%Y/%m', verbose_name='头像', max_length=100)
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '教师'
        verbose_name_plural = verbose_name

    def get_course_nums(self):
        """
        获取该讲师所有课程数量
        :return:
        """
        return self.course_set.all().count()

    def __str__(self):
        return self.name
