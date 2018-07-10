# _*_ coding:utf-8 _*_
# 包的引用规则：
# 第一区域为Python自带包
# 第二区域为第三方包（如Django等）
# 第三区域为自己定义的包

from datetime import datetime

from django.db import models

from organization.models import CourseOrg, Teacher
# Create your models here.
# 课程管理app，含课程基本信息、


class Course(models.Model):
    """
    课程基本信息
    """
    course_org = models.ForeignKey(CourseOrg, verbose_name='课程机构', null=True, blank=True)
    name = models.CharField(max_length=52, verbose_name='课程名字')
    desc = models.CharField(max_length=300, verbose_name='课程描述')
    teacher = models.ForeignKey(Teacher, verbose_name='讲师', null=True, blank=True)
    detail = models.TextField(verbose_name='课程详情')
    degree = models.CharField(choices=(('cj', '初级'), ('zj', '中级'), ('gj', '高级')), max_length=2, verbose_name='难度')
    learn_times = models.IntegerField(default=0, verbose_name='学习时长(分钟数)')
    students = models.IntegerField(default=0, verbose_name='学习人数')
    fav_nums = models.IntegerField(default=0, verbose_name='收藏人数')
    image = models.ImageField(upload_to='courses/%Y/%m', verbose_name='封面图', max_length=100)
    click_nums = models.IntegerField(default=0, verbose_name='点击数')
    is_banner = models.BooleanField(default=False, verbose_name=u'是否是轮播图')
    category = models.CharField(default='后端', max_length=20, verbose_name='课程类别')
    tag = models.CharField(default='', verbose_name='课程标签', max_length=10)
    youneed_konw = models.CharField(default='', max_length=300, verbose_name='课前须知')
    teacher_tell = models.CharField(default='', max_length=300, verbose_name='老师告诉你能学什么')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '课程'
        verbose_name_plural = verbose_name

    def get_zj_nums(self):
        """
        一访问多，类名小写_set,获取课程章节的总数
        :return:
        """
        return self.lesson_set.all().count()

    def get_learn_users(self):
        """
        一访问多，外键在用户操作管理app中，获取用户学习过的课程中最新的5条记录
        :return:
        """
        return self.usercourse_set.all()[:5]

    def get_course_lesson(self):
        """
        获取该课程的所有章节
        :return:
        """
        return self.lesson_set.all()

    def __str__(self):
        return self.name


class BannerCourse(Course):
    """
    课程轮播图
    """
    class Meta:
        verbose_name = u'轮播课程'
        verbose_name_plural = verbose_name
        # 如果不设置 proxy ，就会再生成一个 BannerCourse 数据表
        proxy = True


class Lesson(models.Model):
    """
    章节信息详情
    """
    course = models.ForeignKey(Course, verbose_name='课程')
    name = models.CharField(max_length=100, verbose_name='章节名')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '章节'
        verbose_name_plural = verbose_name

    def get_lesson_video(self):
        """
        获取该章节视频
        :return:
        """
        return self.video_set.all()

    def __str__(self):
        return self.name


class Video(models.Model):
    """
    章节视频信息
    """
    lesson = models.ForeignKey(Lesson, verbose_name='章节')
    name = models.CharField(max_length=100, verbose_name='视频名')
    url = models.URLField(max_length=200, verbose_name='访问地址', default='www.baidu.com')
    learn_times = models.IntegerField(default=0, verbose_name='视频时长(分钟数)')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '视频'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CourseResource(models.Model):
    """
    课程资源，如课件等
    """
    course = models.ForeignKey(Course, verbose_name='课程')
    name = models.CharField(max_length=100, verbose_name='课件名')
    download = models.FileField(upload_to='course/resource/%Y/%m', verbose_name='资源文件', max_length=100)
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = u'课程资源'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
