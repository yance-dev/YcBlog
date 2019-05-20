from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.contrib import auth
from blog.ultils.validcode import get_valid_code_img
from blog.Myform import *
from blog import models
import json
from django.db.models import F
from django.db import transaction
from django.contrib.auth.decorators import login_required
import os
from cnblog import settings
from bs4 import BeautifulSoup
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from cnblog.settings import BASE_DIR


# Create your views here.
def supreme(request):
    """
    这是数据初始化视图，将会生成99条测试数据，用户名为管理员输入的字符后，加1_99.
    密码为管理员填入的密码
    :param request:
    :return:
    """
    tag_title = ['BASIC', 'C',
                 'C++', 'PASCAL', 'FORTRAN', 'LISP', 'Prolog', 'CLIPS', 'OpenCyc', 'Fazzy', 'Python', 'PHP', 'Ruby',
                 'Lua']
    category_titles = ['非技术区',
                       '软件测试',
                       '代码与软件发布',
                       '计算机图形学',
                       '游戏开发',
                       '程序人生',
                       '求职面试',
                       '读书区',
                       '转载区',
                       'Windows',
                       '翻译区',
                       '开源研究',
                       'Flex']
    userlist = []
    bolglist = []
    article_list = []
    tag_list = []
    cat_list = []
    article2tag_list = []

    if request.is_ajax():

        form = UserForm(request.POST)
        response = {'user': None, 'msg': None}
        if form.is_valid():

            response['user'] = form.cleaned_data.get('user')
            # 生成一条用户记录
            user = form.cleaned_data.get('user')

            pwd = form.cleaned_data.get('pwd')
            email = form.cleaned_data.get('email')
            avatar_obj = request.FILES.get('avatar')
            extra = {}
            if avatar_obj:
                extra['avatar'] = avatar_obj
                with transaction.atomic():
                    for i in range(1, 100):
                        bolglist.append(Blog(title='blog%s' % i))
                        # Blog.objects.create(title='blog%s' % i)
                        # userlist.append(UserInfo(username='hyc' + str(i), password=avatars, email=email,**extra))

                        # UserInfo.objects.create_user(username=user + str(i), password=pwd, email=email, **extra)
                        #
                        # UserInfo.objects.filter(username=user + str(i)).update(blog_id=i)

                        for title in tag_title:
                            tag_list.append(Tag(title=title, blog_id=i))

                        for cat in category_titles:
                            cat_list.append(Category(title=cat, blog_id=i))
                        import random
                        for c in range(1, 7):
                            with open(os.path.join(BASE_DIR, "static/superme/%s.txt" % c), 'r',
                                      encoding='utf-8') as f:
                                content = f.read()

                            soup = BeautifulSoup(content, "html.parser")
                            for tag in soup.find_all():
                                if tag.name == "script":
                                    tag.decompose()
                            desc = soup.text[0:150] + "..."
                            c_id = 13 * (i - 1) + random.randrange(1, 9)

                            article_list.append(
                                Article(desc=desc, title='article%s' % c, content=content, user_id=i, category_id=c_id))
                    Blog.objects.bulk_create(bolglist)
                    count=1
                    for user in userlist:
                        UserInfo.objects.create_user(username='hyc' + str(i), password=123, email=email,**extra)
                        UserInfo.objects.filter(username=user.username).update(blog_id=count)
                        count+=1
                    Category.objects.bulk_create(cat_list)
                    Tag.objects.bulk_create(tag_list)
                    Article.objects.bulk_create(article_list)

        else:
            response['msg'] = form.errors
        return JsonResponse(response)

    my_from = UserForm

    return render(request, 'supreme.html', {'from': my_from})


def login(request):
    """
    测试账户
    mark
    mark1234
    :param request:
    :return:
    """
    if request.method == 'POST':
        response = {'user': None, 'msg': None}
        input_user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        valid_code = request.POST.get('valid_code')
        valid_code_str = request.session.get('valid_code_str')
        if valid_code.upper() == valid_code_str.upper():
            print(input_user,pwd)

            user = auth.authenticate(username=input_user, password=pwd)
            if user:
                auth.login(request, user)
                response['user'] = user.username
            else:
                response['msg'] = '账号或密码错误'

        else:
            response['msg'] = '验证码错误'
        return JsonResponse(response)

    return render(request, 'login.html')


def get_validCode_img(request):
    data = get_valid_code_img(request)

    return HttpResponse(data)


def my_paginator(request, article_list):
    paginator = Paginator(article_list, 10)
    page = request.GET.get('page', 1)
    currentPage = int(page)

    #  如果页数十分多时，换另外一种显示方式
    if paginator.num_pages > 11:
        if currentPage - 5 < 1:
            pageRange = range(1, 11)
        elif currentPage + 5 > paginator.num_pages:
            pageRange = range(currentPage - 5, paginator.num_pages + 1)
        else:
            pageRange = range(currentPage - 5, currentPage + 5)
    else:
        pageRange = paginator.page_range
    try:
        article_list = paginator.page(page)
    except PageNotAnInteger:
        article_list = paginator.page(1)
    except EmptyPage:
        article_list = paginator.page(paginator.num_pages)
    return pageRange, paginator, article_list


def index(request):
    article_list = Article.objects.order_by('pk').all().reverse()
    top_up = Article.objects.all().order_by('up_count').all().reverse()[0:10]
    pageRange, paginator, article_list = my_paginator(request, article_list)

    return render(request, 'index.html',
                  {'article_list': article_list, 'top_up': top_up, 'paginator': paginator, 'pageRange': pageRange})


def logout(request):
    """
    注销视图
    :param request:
    :return:
    """
    auth.logout(request)
    return redirect('/login/')


def register(request):
    if request.is_ajax():

        form = UserForm(request.POST)
        response = {'user': None, 'msg': None}
        if form.is_valid():

            response['user'] = form.cleaned_data.get('user')
            # 生成一条用户记录
            user = form.cleaned_data.get('user')
            pwd = form.cleaned_data.get('pwd')

            email = form.cleaned_data.get('email')
            avatar_obj = request.FILES.get('avatar')
            extra = {}
            if avatar_obj:
                extra['avatar'] = avatar_obj
            UserInfo.objects.create_user(username=user, password=pwd, email=email, **extra)

        else:
            response['msg'] = form.errors
        return JsonResponse(response)

    my_from = UserForm
    return render(request, 'register.html', {'from': my_from})


def home_site(request, username, **kwargs):
    user = UserInfo.objects.filter(username=username).first()
    username = username
    if not user:
        return render(request, 'not_found.html')
    blog = user.blog
    article_list = models.Article.objects.filter(user=user)
    right_tag = Article.objects.filter(user=user).values('category__title')

    if kwargs:
        condition = kwargs.get("condition")
        param = kwargs.get("param")  # 2012-12

        if condition == "category":
            article_list = article_list.filter(category__title=param)
        elif condition == "tag":
            article_list = article_list.filter(tags__title=param)
        else:
            year, month = param.split("/")
            article_list = article_list.filter(create_time__year=year, create_time__month=month)
        pageRange, paginator, article_list = my_paginator(request, article_list)

    return render(request, 'home_site.html', locals())


def article_detail(request, username, article_id):
    user = UserInfo.objects.filter(username=username).first()
    username = username
    blog = user.blog
    article_obj = models.Article.objects.filter(pk=article_id).first()

    comment_list = models.Comment.objects.filter(article_id=article_id)

    return render(request, "article_detail.html", locals())


def digg(request):
    """
    点赞功能
    :param request:
    :return:
    """

    article_id = request.POST.get("article_id")
    is_up = json.loads(request.POST.get("is_up"))  # "true"
    # 点赞人即当前登录人
    user_id = request.user.pk
    obj = models.ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()

    response = {"state": True}
    if not obj:
        models.ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)

        queryset = models.Article.objects.filter(pk=article_id)
        if is_up:
            queryset.update(up_count=F("up_count") + 1)
        else:
            queryset.update(down_count=F("down_count") + 1)
    else:
        response["state"] = False
        response["handled"] = obj.is_up

    return JsonResponse(response)


def comment(request):
    article_id = request.POST.get("article_id")
    pid = request.POST.get("pid")
    content = request.POST.get("content")
    user_id = request.user.pk

    article_obj = models.Article.objects.filter(pk=article_id).first()

    # 事务操作
    with transaction.atomic():
        comment_obj = models.Comment.objects.create(user_id=user_id, article_id=article_id, content=content,
                                                    parent_comment_id=pid)
        models.Article.objects.filter(pk=article_id).update(comment_count=F("comment_count") + 1)

    response = {}

    response["create_time"] = comment_obj.create_time.strftime("%Y-%m-%d %X")
    response["username"] = request.user.username
    response["content"] = content
    response['parent_con'] = ''
    response['parent_user'] = ''

    if pid:
        response['parent_con'] = comment_obj.parent_comment.content
        response['parent_user'] = comment_obj.parent_comment.user.username

    from django.core.mail import send_mail
    from cnblog import settings
    import threading
    t = threading.Thread(target=send_mail, args=("您的文章%s新增了一条评论内容" % article_obj.title,
                                                 content,
                                                 settings.EMAIL_HOST_USER,
                                                 ["hyc554@gmail.com"]))
    t.start()
    return JsonResponse(response)


def get_comment_tree(request):
    article_id = request.GET.get('article_id')
    response = list(models.Comment.objects.filter(article_id=article_id).order_by('pk').values('pk', 'content',
                                                                                               'parent_comment_id'))
    return JsonResponse(response, safe=False)


@login_required
def cn_backend(request):
    """
    后台管理的首页
    :param request:
    :return:
    """
    article_list = models.Article.objects.filter(user=request.user)

    return render(request, "backend/backend.html", locals())


@login_required
def add_article(request):
    """
    后台管理的添加书籍视图函数
    :param request:
    :return:
    """
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        # 防止xss攻击,过滤script标签
        soup = BeautifulSoup(content, "html.parser")
        for tag in soup.find_all():

            if tag.name == "script":
                tag.decompose()

        # 构建摘要数据,获取标签字符串的文本前150个符号

        desc = soup.text[0:150] + "..."

        models.Article.objects.create(title=title, desc=desc, content=str(soup), user=request.user)
        return redirect("/cn_backend/")

    return render(request, "backend/add_article.html")


def upload(request):
    """
    编辑器上传文件接受视图函数
    :param request:
    :return:
    """

    img_obj = request.FILES.get("upload_img")

    path = os.path.join(settings.MEDIA_ROOT, "add_article_img", img_obj.name)

    with open(path, "wb") as f:
        for line in img_obj:
            f.write(line)
    response = {
        'error': 0,
        'url': '/media/add_article_img/%s' % img_obj.name
    }

    return HttpResponse(json.dumps(response))

@login_required
def delete_article(request, article_id):
    """
    删除博客文章
    :param request:
    :param article_id:
    :return:
    """
    Article.objects.filter(pk=article_id).delete()
    return redirect('cn_backend')

@login_required
def edit_article(request, article_id):
    """
    博客文章编辑功能
    :param request:
    :param article_id:
    :return: 返回管理界面
    """

    article_obj = Article.objects.filter(pk=article_id).first()
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        # 防止xss攻击,过滤script标签
        soup = BeautifulSoup(content, "html.parser")
        for tag in soup.find_all():

            if tag.name == "script":
                tag.decompose()

        # 构建摘要数据,获取标签字符串的文本前150个符号

        desc = soup.text[0:150] + "..."

        models.Article.objects.filter(pk=article_id).update(title=title, desc=desc, content=str(soup))
        return redirect("/cn_backend/")

    return render(request, 'backend/edit.html', {'article_obj': article_obj})
