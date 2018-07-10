# _*_ coding:utf-8 _*_

import xadmin
from xadmin import views
from xadmin.plugins.auth import UserAdmin
from .models import EmailVerifyRecord, Banner, UserProfile


# ----- adminx 全局配置
class BaseSetting:
    """
    后台修改需要的配置
    """
    enable_themes = True
    use_bootswatch = True


class GlobalSettings:
    """
    后台修改
    """
    site_title = '后台管理系统'
    site_footer = '在线学习网'
    menu_style = 'accordion'


class EmailVerifyRecordAdmin:
    """
    邮箱验证管理
    """
    list_display = ['code', 'email', 'send_type', 'send_time']  # 显示项目
    search_fields = ['code', 'email', 'send_type']      # 搜索字段
    list_filter = ['code', 'email', 'send_type', 'send_time']  # 过滤字段


class BannerAdmin:
    """
    轮播图管理
    """
    list_display = ['title', 'image', 'url', 'index', 'add_time']
    search_fields = ['title', 'image', 'url', 'index']
    list_filter = ['title', 'image', 'url', 'index', 'add_time']


xadmin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
xadmin.site.register(Banner, BannerAdmin)
xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)
