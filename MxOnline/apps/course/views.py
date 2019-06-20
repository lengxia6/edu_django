
# Create your views here.

from django.shortcuts import render
from django.views.generic import View
from .models import Course,CourseResource
from operation.models import UserFavorite,CourseComments,UserCourse
from pure_pagination import Paginator,EmptyPage,PageNotAnInteger
from django.http import HttpResponse
from utils.mixin_utils import LoginRequiredMixin

class CourseListView(View):
    def get(self, request):

        all_courses = Course.objects.all().order_by('-add_time')
        # 热门课程推荐

        hot_courses = Course.objects.all().order_by('-click_nums')[:3]
        # 排序
        sort = request.GET.get('sort',"")

        if sort:
            if sort == "students":
                all_courses = all_courses.order_by("-students")

            elif sort == "hot":
                all_courses = all_courses.order_by("-click_nums")


        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_courses, 2, request=request)
        courses = p.page(page)

        return render(request, "course_list.html",{
            'all_courses':courses,
            "sort":sort,
            "hot_courses":hot_courses,


        })


class CourseDetailView(View):
    """课程详情"""
    def get(self,request,course_id):
        course = Course.objects.get(id=int(course_id))

        # 课程点击数加1
        course.click_nums +=1
        course.save()
        # 课程标签
        # 通过当前标签，查找数据库中的课程
        has_fav_course = False
        has_fav_org = False

        # 必须是用户已登录我们才需要判断
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user,fav_id=course.id,fav_type=1):
                has_fav_course = True

            if UserFavorite.objects.filter(user=request.user,fav_id=course.course_org.id,fav_type=2):
                has_fav_org = True

        tag = course.tag
        if tag:
            # 需要从1开始不然会推荐自己
            relate_courses = Course.objects.filter(tag=tag)[:2]

        else:
            relate_courses = []


        return render(request,"course-detail.html",{
            'course':course,
            'relate_courses':relate_courses,
            "has_fav_course":has_fav_course,
            "has_fav_org":has_fav_org,
        })


class CourseInfoView(LoginRequiredMixin,View):
    '''课程章节信息'''
    def get(self, request, course_id):

        course = Course.objects.get(id=int(course_id))
        for yy in course.get_learn_users:
            print("???",yy.id)

        # 查询用户是否已经学习了该课程

        user_courses = UserCourse.objects.filter(user=request.user,course=course)
        if not user_courses:
            # 如果没有学习该门课程就关联起来
            user_course = UserCourse(user=request.user,course=course)
            user_course.save()


        # 相关课程推荐
        # 找到学习这门课的所有用户
        user_courses = UserCourse.objects.filter(course=course)
        for u in user_courses:
            print("学习这门课的所有用户：",u)
        # print("***",user_courses)


        # 找到学习这门课的所有用户的id
        user_ids = [user_courses.user_id for user_courses in user_courses]
        print("学习这门课的所有用户的id：",user_ids)

        #  通过所有用户的id，找到所有用户学习过的所有课程
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        for i in all_user_courses:
            print("所有用户学习过课程：",i.user,i.course)


        # 取出所有课程id
        course_ids = [all_user_course.course_id for all_user_course in all_user_courses]
        for x in course_ids:
            print("取出所有课程id:",x)

        # 通过所有课程的id，找到所有所有的课程，按点击量去五个
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:5]
        for u in relate_courses:
            print("通过所有课程的id，找到所有所有的课程，按点击量去五个:",u)


        # 资源
        all_resources = CourseResource.objects.filter(course=course)
        print("资源：",all_resources)


        return render(request, "course-video.html", {
            "course": course,
            "all_resources":all_resources,
            "relate_courses":relate_courses,
        })


class CommentsView(LoginRequiredMixin,View):

    """课程评论"""

    def get(self,request,course_id):
        course = Course.objects.get(id=int(course_id))

        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.all()
        return render(request,"course-comment.html",{
            "course":course,
            "all_resources":all_resources,
            "al_comments":all_comments,
        })


# 添加评论
class AddCommentsView(View):
    """用户评论"""

    def post(self,request):
        if not request.user.is_authenticated:
            # 未登录时返回json提示未登录，跳转到登录页面是在ajax中做的
            return HttpResponse('{"status":"fail","msg":"用户未登录"}',content_type='application/json')
        course_id = request.POST.get("course_id",0)
        comments = request.POST.get("comments","")

        if int(course_id) > 0 and comments:
            # 实例化一个course_comments对象

            course_comments = CourseComments()
            # 获取评论的是哪门课程

            course = Course.objects.get(id = int(course_id))
            # 分别把评论的课程、评论的内容和评论的用户保存到数据库

            course_comments.course = course

            course_comments.comments = comments

            course_comments.user = request.user

            return HttpResponse('{"status":"success","msg":"评论成功"}',content_type='application/json')

        else:
            return HttpResponse('{"status":"fail","msg":"评论失败"}',content_type='application/json')






























