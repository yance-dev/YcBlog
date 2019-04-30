"""cnblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.txt.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2.txt. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2.txt. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2.txt. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from blog import views
from django.views.static import serve
from cnblog import settings

urlpatterns = [
    # 文本编辑器上传图片url
    path('upload/', views.upload),
    # 后台管理url
    re_path("cn_backend/$", views.cn_backend, name='cn_backend'),
    re_path("cn_backend/add_article/$", views.add_article),
    # 初始化测试数据
    path('supreme/', views.supreme),
    # 点赞
    path("digg/", views.digg),
    path('comment/', views.comment),
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('index/', views.index),
    re_path('^$', views.index, name='port'),
    path('register/', views.register),
    path('get_validCode_img/', views.get_validCode_img),
    path('logout/', views.logout),
    path('get_comment_tree/', views.get_comment_tree),
    re_path('^delete_article/(?P<article_id>\d+)$', views.delete_article),
    re_path('^edit_article/(?P<article_id>\d+)$', views.edit_article),

    # media 配置
    re_path(r"media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path('^(?P<username>\w+)/articles/(?P<article_id>\d+)$', views.article_detail),
    # article_detail(request,username="yuan","article_id":article_id)

    # 个人站点url
    re_path('^(?P<username>\w+)/$', views.home_site),  # home_site(reqeust,username="yuan")
    # 个人站点的跳转

    re_path('^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)/$', views.home_site,
            name='blog_info'),  # home_site(reqeust,username="yuan",condition="tag",param="python")

]
