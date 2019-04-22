from pure_pagination import Paginator,EmptyPage,PageNotAnInteger
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.views.generic.base import View
from .models import CityDict,CourseOrg

class OrgView(View):
    '''课程机构'''

    def get(self, request):
        # 课程机构
        all_orgs = CourseOrg.objects.all()
        org_nums = CourseOrg.objects.count()
        # 所有城市
        all_citys = CityDict.objects.all()

        # 课程分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 2 表示每页的数量
        p = Paginator(all_orgs, 3, request=request)
        orgs = p.page(page)

        return render(request, "org-list.html", {'all_orgs': orgs, 'all_citys': all_citys, 'org_nums': org_nums})

