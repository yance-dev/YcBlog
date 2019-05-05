from django import template
from django.db.models import Count
from blog import models

register = template.Library()


@register.inclusion_tag('classfication.html')
def get_calssfication_style(username):
    user = models.UserInfo.objects.filter(username=username).first()
    print(user.username)
    blog=user.blog
    nblog_id = user.blog_id
    print(nblog_id)

    cate_list = models.Category.objects.filter(blog_id=nblog_id).values("pk").annotate(c=Count("article__title")).values_list(
        "title", "c")
    print(cate_list)

    tag_list = models.Tag.objects.filter(blog_id=nblog_id).values("pk").annotate(c=Count("article")).values_list("title", "c")

    date_list = models.Article.objects.filter(user=user).extra(
        select={"y_m_date": "date_format(create_time,'%%Y/%%m')"}).values("y_m_date").annotate(
        c=Count("nid")).values_list("y_m_date", "c")
    print({"blog": blog, "cate_list": cate_list, "date_list": date_list, "tag_list": tag_list,"username":username})

    return {"blog": blog, "cate_list": cate_list, "date_list": date_list, "tag_list": tag_list,"username":username}
