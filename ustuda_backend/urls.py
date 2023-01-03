
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from ustuda.views import announcement_update, tutors_date_actions, tutors_actions, reset_token ,reset_request, all_comments, comments,courses_all, school_courses_search, GoogleAuthApiView, verify_payment, continue_reg, get_profile, my_courses_and_inventories, material_detail, ongoing_skill_detail, skill_detail, notifications, ongoing_tutorial_detail,tutorial_detail,userPaidTutorial, testing,ongoing_course_detail, userPaid,home,registerUser,schools,courses,skills,materials,tutorials,classes,school_detail,course_detail,school_courses,MyTokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('api/home', home),
    path('api/testing', testing),
    path('api/schools', schools),
    path('api/courses', courses),
    path('api/skills', skills),
    path('api/classes', classes),
    path('api/tutorials', tutorials),
    path('api/my_courses_and_inventories', my_courses_and_inventories),
    path('api/register', registerUser),
    path('api/notifications', notifications),
    path('api/courses_all', courses_all),
    path('api/login', MyTokenObtainPairView.as_view()),
    path('api/google_login', GoogleAuthApiView.as_view()),
    path('api/verify_payment', verify_payment),
    path('api/materials', materials),
    path('api/get_profile', get_profile),
    path('api/continue_reg', continue_reg),
    path('api/comments', comments),
    path('api/announcement_update', announcement_update),
    path('api/reset_token', reset_token),
    path('api/reset_request', reset_request),
    path('api/tutors_date_actions/<str:pk>', tutors_date_actions),
    path('api/material_detail/<str:pk>', material_detail),
    path('api/tutors_actions/<str:pk>', tutors_actions),
    path('api/materials/<str:pk>', materials),
    path('api/skill_detail/<str:pk>', skill_detail),
    path('api/all_comments/<str:pk>', all_comments),
    path('api/skills/<str:skill>', skills),
    path('api/ongoing_course_detail/<str:pk>', ongoing_course_detail),
    path('api/ongoing_skill_detail/<str:pk>', ongoing_skill_detail),
    path('api/ongoing_tutorial_detail/<str:pk>', ongoing_tutorial_detail),
    path('api/school_detail/<str:pk>', school_detail),
    path('api/user_paid/<str:pk>', userPaid),
    path('api/user_paid_tutorial/<str:pk>', userPaidTutorial),
    path('api/tutorial_detail/<str:pk>', tutorial_detail),
    path('api/course_detail/<str:pk>', course_detail),
    path('api/school_courses/<str:pk>', school_courses),
    path('api/school_courses_search/<str:pk>', school_courses_search),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
