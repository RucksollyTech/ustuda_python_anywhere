from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from .models import Logged_In_User_Jwt_Rec, Comments,Announcements, Comments_Holder, Tokens, Payment_Information, Courses,Profile, Skills, Tutorial,Schools,Materials,Classes,Notification
from django.db.models import Q,F
from .serializers import CommentSerializer, AnnouncementsSerializer, UserSerializer, GeneralSerializer, SkillsSerializer,TutorialSerializer,SchoolsSerializer,MaterialsSerializer,ClassesSerializer,NotificationSerializer,ProfileSerializer,CoursesSerializer,UserSerializerWithToken
import json
from django.conf import settings
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.hashers import make_password
from rest_framework import status
from pypaystack import Transaction
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from itertools import chain
from datetime import timedelta,datetime

from dateutil.relativedelta import relativedelta

# from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from google.oauth2 import id_token
from google.auth.transport.requests import Request as GoogleRequest
import requests

from rest_framework.views import APIView
from django.core.mail import EmailMultiAlternatives,send_mail
from decouple import config
from django.utils import timezone

JWT_authenticator = JWTAuthentication()

@api_view(['GET'])
def home(request,*args,**kwargs):
    obj = Courses.objects.filter(is_featured = False).all()[:5]
    obj2 = Schools.objects.all()[:10]
    obj3 = Courses.objects.all()[:70]
    obj4 = Tutorial.objects.all()[:5]
    objx5 = Courses.objects.filter(is_featured = True).all()[:5]

    
    active_courses= None
    if not obj:
        return Response({},status=404)
    try:
        user = request.user.id
        profile = Profile.objects.filter(user__id = user).first()
        
        if profile:
            objx = Courses.objects.filter(
                Q(title=profile.cat1) | Q(title=profile.cat2) | Q(title=profile.cat3) | Q(title=profile.cat4)
            ).all()[:5]
            obj = list(chain(objx,obj))[:5]
            
            objx2 = Tutorial.objects.filter(
                Q(course_name=profile.cat1) | Q(course_name=profile.cat2) | Q(course_name=profile.cat3) | Q(course_name=profile.cat4)
            ).all()[:5]
            obj4 = list(chain(objx2,obj4))[:5]
            
            
            cox = Courses.objects.filter(students__id =user).all()
            
            if cox:
                active_c = CoursesSerializer(cox[:2],many=True)
                active_courses = active_c.data
    except:
        pass
    
    obj = list(dict.fromkeys(obj))
    obj4 = list(dict.fromkeys(obj4))
    objx5 = list(dict.fromkeys(objx5))
    
    serializer = CoursesSerializer(obj,many=True)
    serializers = CoursesSerializer(objx5,many=True)
    schools = SchoolsSerializer(obj2,many=True) 
    all_courses = CoursesSerializer(obj3,many=True)
    tutorials = TutorialSerializer(obj4,many=True)
    
    context ={
        "featured": serializers.data,
        "active_courses": active_courses,
        "courses" :serializer.data,
        "schools": schools.data,
        "all_courses": all_courses.data,
        "tutorials": tutorials.data
    }
    return Response(context,status=200)



@api_view(['GET'])
def schools(request,*args,**kwargs):
    obj = Schools.objects.all()
    query = request.query_params.get("query")
    page = request.query_params.get("page")
    paginator = Paginator(obj,40)
    if query:
        obj = obj.filter(name__icontains=query)
        paginator = Paginator(obj,40)
    try:
        obj = paginator.page(page)
    except PageNotAnInteger:
        obj = paginator.page(1)
    except EmptyPage:
        obj = paginator.page(paginator.num_pages)
    
    if page == None:
        page = 1

    page = int(page)

    serializer = SchoolsSerializer(obj,many=True)
    
    return Response({'schools': serializer.data, 'page': page, 'pages': paginator.num_pages},status=200)



@api_view(['GET'])
def school_detail(request,pk,*args,**kwargs):
    pk=int(pk)
    obj = Schools.objects.get(id=pk)
    if not obj :
        return Response({'detail': 'There is no such school'},status=status.HTTP_400_BAD_REQUEST)
    try:
        most_sch = Schools.objects.all()[:4]
        sch_courses = Courses.objects.filter(schools=obj).all()[:30]
        all_courses= CoursesSerializer(sch_courses,many=True)
        obj2 = Materials.objects.filter(schools=obj).all()[:4]      
        serializer = SchoolsSerializer(obj)
        most_v= SchoolsSerializer(most_sch,many=True)
        main_obj = MaterialsSerializer(obj2,many=True)
        
        context={
            "school" :serializer.data,
            "most_schools" : most_v.data,
            "most_materials" : main_obj.data,
            "courses" : all_courses.data
        }
    except:
        context={
            "school" :serializer.data,
            "most_schools" : [],
            "most_materials" : [],
            "courses" : []
        }
    obj.most_viewed = obj.most_viewed + 1
    obj.save()
    return Response(context,status=200)


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def userPaid(request,pk,*args,**kwargs):
    pk=int(pk)
    user = request.user
    obj = Courses.objects.filter(students=user.id).first()
    serializer = CoursesSerializer(obj)
    if obj:
        return Response(serializer.data,status=200)
    else:
        return Response(None,status=200)
        
        
       
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def userPaidTutorial(request,pk,*args,**kwargs):
    pk=int(pk)
    user = request.user
    obj = Tutorial.objects.filter(students__id=user.id,id=pk).first()
    obj2 = Tutorial.objects.filter(id=pk).first()
    if obj or obj2:
        if obj2 and not obj2.price:
            serializer = TutorialSerializer(obj2)
            return Response(serializer.data,status=200)
        serializer = TutorialSerializer(obj)
        return Response(serializer.data,status=200)
    else:
        return Response(None,status=200)


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def verify_payment(request,*args,**kwargs):
    user = request.user
    if not user:
        return Response({'detail': 'There is no such user'},status=status.HTTP_400_BAD_REQUEST)
    data = request.data
    transaction = Transaction(authorization_key=config("PAY_STACK_SECRETE_KEY"))
    
    if "reference" in data :
        response  = transaction.verify(data["reference"])
        if data["action"] == "course":
            x_course = Courses.objects.get(pk=int(data["pk"]))
            tutoriaL = Tutorial.objects.get(pk= x_course.tutorial.id)
            if response[3]["status"] == "success" and (int(response[3]["amount"]) / (100)) == x_course.price:
                Payment_Information.objects.create(
                    user =request.user,
                    action = data["action"],
                    reference = response[3]["reference"],
                    transaction_id = response[3]["id"],
                    amount = int(response[3]["amount"]) / (100),
                    item_name = x_course.title,
                    item_title = x_course.name
                )
                Notification.objects.create(
                    owner =request.user,
                    topic= x_course.name,
                    image = x_course.image,
                    types = data["action"],
                    action = 'Successful Payment'
                )
                all_mat = x_course.materials.all()
                if all_mat:
                    for i in all_mat:
                        i.students.add(request.user)
                if tutoriaL:
                    tutoriaL.students.add(request.user)
                x_course.students.add(request.user)
        elif data["action"] == "material":
            x_course = Materials.objects.get(pk=int(data["pk"]))
            if response[3]["status"] == "success" and (int(response[3]["amount"]) / (100)) == x_course.price:
                Payment_Information.objects.create(
                    user =request.user,
                    action = data["action"],
                    reference = response[3]["reference"],
                    transaction_id = response[3]["id"],
                    amount = int(response[3]["amount"]) / (100),
                    item_name = x_course.course_name,
                    item_title = x_course.material_title
                )
                Notification.objects.create(
                    owner =request.user,
                    topic= x_course.material_title,
                    image = x_course.image,
                    types = data["action"],
                    action = 'Successful Payment'
                )
                x_course.students.add(request.user)
        elif data["action"] == "tutorial":
            x_course = Tutorial.objects.get(pk=int(data["pk"]))
            if response[3]["status"] == "success" and (int(response[3]["amount"]) / (100)) == x_course.price:
                Payment_Information.objects.create(
                    user =request.user,
                    action = data["action"],
                    reference = response[3]["reference"],
                    transaction_id = response[3]["id"],
                    amount = int(response[3]["amount"]) / (100),
                    item_name = x_course.course_name,
                    item_title = x_course.topic
                )
                Notification.objects.create(
                    owner =request.user,
                    topic= x_course.topic,
                    image = x_course.course_image,
                    types = data["action"],
                    action = 'Successful Payment'
                )
                x_course.students.add(request.user)
        elif data["action"] == "skill":
            x_course = Skills.objects.get(pk=int(data["pk"]))
            if response[3]["status"] == "success" and (int(response[3]["amount"]) / (100)) == x_course.price:
                Payment_Information.objects.create(
                    user =request.user,
                    action = data["action"],
                    reference = response[3]["reference"],
                    transaction_id = response[3]["id"],
                    amount = int(response[3]["amount"]) / (100),
                    item_name = x_course.title,
                    item_title = x_course.name
                )
                Notification.objects.create(
                    owner =request.user,
                    topic= x_course.name,
                    image = x_course.image,
                    types = data["action"],
                    action = 'Successful Payment'
                )
                x_course.students.add(request.user)
        else:
            return Response({"detail":"Unsuccessful Payment"},status=status.HTTP_400_BAD_REQUEST)
        return Response("success",status=200)
    return Response({"detail":"Unsuccessful Payment"},status=status.HTTP_400_BAD_REQUEST)
            
    
@api_view(['GET','POST'])
def course_detail(request,pk,*args,**kwargs):
    pk=int(pk)
    obj = Courses.objects.get(id=pk)
    user = request.user
    if not obj :
        return Response({'detail': 'There is no such course'},status=status.HTTP_400_BAD_REQUEST)
    sch = obj.schools
    top_course = Courses.objects.filter(schools=sch)
    top_courses = top_course.all()
    classes_on_course = obj.classes.all()
    
    paid = None
    try:
        if obj.students.get(id=user.id):
            paid = True
    except:
        if not obj.price:
            paid = True
    
    
    context={
        "paid" : paid,
        "top_courses" :CoursesSerializer(top_courses,many=True).data,
        "course" : CoursesSerializer(obj).data,
        "classes" : ClassesSerializer(classes_on_course,many=True).data,
        "tutorial" : obj.tutorial.id if obj.tutorial else None
    } 
    obj.most_viewed = obj.most_viewed + 1
    obj.save()   
    
    return Response(context,status=200)


@api_view(['GET'])
def skill_detail(request,pk,*args,**kwargs):
    pk=int(pk)
    obj = Skills.objects.get(id=pk)
    user = request.user
    if not obj :
        return Response({'detail': 'This skill is not available '},status=status.HTTP_400_BAD_REQUEST)
    skill_name = obj.name
    similar_skills = Skills.objects.filter(name__iexact=skill_name).all()[:10]
    soft_skill = obj.manual_skill
    if not similar_skills or len(similar_skills) < 2:
        similar_skills = Skills.objects.filter(manual_skill=soft_skill).all()
        if not similar_skills or len(similar_skills) < 2:
            similar_skills = Skills.objects.all()

    classes_on_skill = obj.classes.all()
    paid = None
    try:
        if obj.students.get(id=user.id):
            paid = True
    except:
        if not obj.price:
            paid = True
    
    context={
        "paid" : paid,
        "top_skills" :SkillsSerializer(similar_skills,many=True).data,
        "skill" : SkillsSerializer(obj).data,
        "classes" : ClassesSerializer(classes_on_skill,many=True).data
    } 
    obj.most_viewed = obj.most_viewed + 1
    obj.save()   
    return Response(context,status=200)




@api_view(['GET'])
def material_detail(request,pk,*args,**kwargs):
    pk=int(pk)
    obj = Materials.objects.get(id=pk)
    user = request.user
    if not obj :
        return Response({'detail': 'This material is not available '},status=status.HTTP_400_BAD_REQUEST)
    material_name = obj.course_name
    similar_material = Materials.objects.filter(course_name__iexact=material_name).all()[:10]
    if not similar_material or len(similar_material) < 2:
        similar_material = Materials.objects.filter(material_title__iexact =obj.material_title).all()
        if not similar_material or len(similar_material) < 2:
            similar_material = Materials.objects.all()

    paid = None
    check_paid = Courses.objects.filter(materials =obj).first()
    students = 0
    
    if check_paid:
        try:
            students =check_paid.students.count()
        except:
            students = 0
    try:
        if obj.students.get(id=user.id):
            paid = True
    except:
        if not obj.price :
            paid = True
        
    sch = obj.schools
    context={
        "school" : SchoolsSerializer(sch).data,
        "students" : students,
        "paid" : paid,
        "top_materials" :MaterialsSerializer(similar_material,many=True).data,
        "material" : MaterialsSerializer(obj).data
    } 
    obj.most_viewed = obj.most_viewed + 1
    obj.save()   
    return Response(context,status=200)


@api_view(['GET'])
def tutorial_detail(request,pk,*args,**kwargs):
    pk=int(pk)
    obj = Tutorial.objects.get(id=pk)
    user = request.user
    paid = None
    if not obj :
        return Response({'detail': 'There is no such tutorial'},status=status.HTTP_400_BAD_REQUEST)
    
    related_tutorial = Tutorial.objects.filter(course_name__iexact=obj.course_name,topic__iexact =obj.topic).all()
    if not related_tutorial or len(related_tutorial) <2:
        related_tutorial = Tutorial.objects.filter(course_name__iexact=obj.course_name).all()
    
    course = Courses.objects.filter(tutorials=obj.id).first()
    try:
        if obj.students.get(id=user.id):
            paid = True
        
    except:
        if not obj.price:
            paid = True
        
    context={
        "paid" : paid,
        "tutorial" :TutorialSerializer(obj).data,
        "similar_tutorials" :TutorialSerializer(related_tutorial,many=True).data,
        "course" : CoursesSerializer(course).data
    } 
    obj.most_viewed = obj.most_viewed + 1
    obj.save()   
    return Response(context,status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ongoing_course_detail(request,pk,*args,**kwargs):
    pk=int(pk)
    obj = Courses.objects.get(id=pk)
    user = request.user
    
    if not obj :
        return Response({'detail': 'There is no such course'},status=status.HTTP_400_BAD_REQUEST)
    
    classes_on_course = obj.classes.all()
    materials = obj.materials.all()
    announce = obj.announcement.all()
    
    paid = None
    try:
        if obj.students.get(id=user.id):
            paid = True
    except:
        if not obj.price:
            paid = True
    
    context={
        "paid" : paid,
        "course" : CoursesSerializer(obj).data,
        "classes" : ClassesSerializer(classes_on_course,many=True).data,
        "materials" : MaterialsSerializer(materials,many= True).data,
        "announcements": AnnouncementsSerializer(announce,many=True).data
    } 
    obj.most_viewed = obj.most_viewed + 1
    obj.save()   
    return Response(context,status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_courses_and_inventories(request,*args,**kwargs):
    user = request.user.id 
    if not user :
        return Response({'detail': 'Please login to view this page'},status=status.HTTP_400_BAD_REQUEST)
    
    courses = Courses.objects.filter(students__id =user).all()
    materials = Materials.objects.filter(students__id =user).all()
    skills = Skills.objects.filter(students__id =user).all()
    tutorials = Tutorial.objects.filter(students__id =user).all()
    
    context={
        "courses" : CoursesSerializer(courses,many=True).data,
        "skills" : SkillsSerializer(skills,many=True).data,
        "materials" : MaterialsSerializer(materials,many= True).data,
        "tutorials": TutorialSerializer(tutorials,many=True).data
    }  
    return Response(context,status=200)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ongoing_skill_detail(request,pk,*args,**kwargs):
    user = request.user
    pk=int(pk)
    obj = Skills.objects.get(id=pk)
    
    if not obj :
        return Response({'detail': 'There is no such skill'},status=status.HTTP_400_BAD_REQUEST)
    
    classes_on_course = obj.classes.all()
    materials = obj.materials.all()
    announce = obj.announcement.all()
    paid = None
    
    try:
        print(user.id)
        if obj.students.get(id=user.id):
            paid = True
            print(True)
    except:
        if not obj.price:
            paid = True
    
    context={
        "paid" : paid,
        "skill" : SkillsSerializer(obj).data,
        "classes" : ClassesSerializer(classes_on_course,many=True).data,
        "materials" : MaterialsSerializer(materials,many= True).data,
        "announcements": AnnouncementsSerializer(announce,many=True).data
    } 
    obj.most_viewed = obj.most_viewed + 1
    obj.save()   
    return Response(context,status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ongoing_tutorial_detail(request,pk,*args,**kwargs):
    pk=int(pk)
    obj = Tutorial.objects.get(id=pk)
    user = request.user
    if not obj :
        return Response({'detail': 'There is no such tutorial'},status=status.HTTP_400_BAD_REQUEST)
    
    materials = obj.materials.all()
    announce = obj.announcement.all()
    similar_tutorial = Tutorial.objects.filter(name_of_tutor=obj.name_of_tutor).all()
    paid = None
    tutor = False
    try:
        paidd = obj.students.get(pk=user.id)
        tuto = obj.which_tutor
        if paidd or tuto == user:
            paid= True
        if tuto == user :
            tutor = True
    except:
        tuto = obj.which_tutor
        if not obj.price:
            paid= True
        if tuto == user:
            tutor = True
    
    context={
        "tutor": tutor,
        "paid" : paid,
        "similar_tutorial" : TutorialSerializer(similar_tutorial,many=True).data,
        "tutorial" : TutorialSerializer(obj).data,
        "materials" : MaterialsSerializer(materials,many= True).data,
        "announcements": AnnouncementsSerializer(announce,many=True).data
    } 
    obj.most_viewed = obj.most_viewed + 1
    obj.save()   
    return Response(context,status=200)


@api_view(['GET','POST','PUT'])
@permission_classes([IsAuthenticated])
def tutors_actions(request,pk,*args,**kwargs):
    user = request.user
    data = request.data
    statuz = data.get("status")
    tutorial = Tutorial.objects.get(pk=int(pk))
    print(statuz)
    
    if not tutorial.which_tutor:
        return Response({'detail': 'You are not a tutor'},status=status.HTTP_400_BAD_REQUEST)
    elif user.id != tutorial.which_tutor.id:
        return Response({'detail': 'You are not a tutor'},status=status.HTTP_400_BAD_REQUEST)
    elif statuz == "start":
        tutorial1 = Tutorial.objects.get(pk=int(pk))
        tutorial1.started = True
        tutorial1.save()
        
        tutorial2 = Tutorial.objects.get(pk=int(pk))
        tutorial2.waiting_tutor = False
        tutorial2.save()
        return Response({"data": "Tutorial started"},status=200)
    elif statuz == "end" :
        tutorial1 = Tutorial.objects.get(pk=int(pk))
        tutorial1.started = False
        tutorial1.save()
        
        tutorial2 = Tutorial.objects.get(pk=int(pk))
        tutorial2.waiting_tutor = False
        tutorial2.save()
        
        return Response({"data": "Tutorial Ended"},status=200)
    elif statuz == "not":
        tutorial1 = Tutorial.objects.get(pk=int(pk))
        tutorial1.started = False
        tutorial1.save()
        
        tutorial2 = Tutorial.objects.get(pk=int(pk))
        tutorial2.waiting_tutor = True
        tutorial2.save()
        
        return Response({"data": "Waiting for tutor"},status=200)
    else:
        return Response({'detail': 'Invalid action'},status=status.HTTP_400_BAD_REQUEST)
    
    

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def tutors_date_actions(request,pk,*args,**kwargs):
    user = request.user
    date = request.data.get("date")
    reset = request.data.get("reset")
    tutorial = Tutorial.objects.get(pk=int(pk))
    if not tutorial.which_tutor:
        return Response({'detail': 'You are not a tutor'},status=status.HTTP_400_BAD_REQUEST)
    elif user.id != tutorial.which_tutor.id:
        return Response({'detail': 'You are not a tutor'},status=status.HTTP_400_BAD_REQUEST)
    elif date:
        tutorial.tutorial_time = date
        tutorial.save()
        return Response({"success": date},status=200)
    elif reset:
        tutorial.students.all().delete()
        tutorial.save()
        return Response({"success": "deleted"},status=200)
    else:
        return Response({'detail': 'Invalid action'},status=status.HTTP_400_BAD_REQUEST)
    
    
    


@api_view(['GET'])
def school_courses(request,pk,*args,**kwargs):
    pk=int(pk)
    obj = Schools.objects.get(id=pk)
    if not obj :
        return Response({'detail': 'There is no such school'},status=status.HTTP_400_BAD_REQUEST)
    try:
        sch_courses = Courses.objects.filter(schools=obj).all()
        classes_by_sch = Classes.objects.filter(schools=obj).all()[:4]
        
        course_serializer = CoursesSerializer(sch_courses,many=True)
        classes_serializer = ClassesSerializer(classes_by_sch,many=True)
        
        context={
            "top_classes" :classes_serializer.data,
            "courses" : course_serializer.data
        }
    except:
        context={
            "top_classes" :[],
            "courses" : []
        }  
    obj.most_viewed = obj.most_viewed + 1
    obj.save()   
    return Response(context,status=200)



@api_view(['GET'])
def school_courses_search(request,pk,*args,**kwargs):
    pk=int(pk)
    obj = Schools.objects.get(id=pk)
    page = request.query_params.get("page")
    query = request.query_params.get("query")
    topic = request.query_params.get("topic") #values are "old or newest"
    school = request.query_params.get("school")
    level = request.query_params.get("level")
    price = request.query_params.get("price")
    course = request.query_params.get("course")

    if not obj :
        return Response({'detail': 'There is no such school'},status=status.HTTP_400_BAD_REQUEST)
    try:
        sch_courses = Courses.objects.filter(schools=obj).all()
        if sch_courses:
            if query:
                sch_courses = sch_courses.filter(Q(title__icontains=query)| Q(name__icontains=query)| Q(price__icontains=query) | Q(levels__icontains=query)| Q(schools__name__icontains=query) | Q(teacher_name__icontains=query)| Q(level__icontains=query))
            if school:
                sch_courses = sch_courses.filter(schools__name = school)
            if topic:
                if topic == "newest":
                    sch_courses = sch_courses.filter(date__lte = datetime.now() + relativedelta(month =+12) )
                else:
                    sch_courses = sch_courses.filter(date__gt = datetime.now() + relativedelta(month =+12) )
            if level:
                sch_courses = sch_courses.filter(levels= level)
            if price:
                try:
                    sch_courses = sch_courses.filter(price__lt = int(price))
                except:
                    if price == "free":
                        sch_courses = sch_courses.filter(price = None)
                    else:
                        sch_courses = sch_courses.filter(price__gt = 9000)
            if course and course != "All":
                obj = obj.filter(title = course)
                
        classes_by_sch = Classes.objects.filter(schools=obj)[:4]
        
        paginator = Paginator(sch_courses,20)
        
        try:
            sch_courses = paginator.page(page)
        except PageNotAnInteger:
            sch_courses = paginator.page(1)
        except EmptyPage:
            page = paginator.num_pages
            sch_courses = paginator.page(paginator.num_pages)
        
    
        course_serializer = CoursesSerializer(sch_courses,many=True)
        classes_serializer = ClassesSerializer(classes_by_sch,many=True)
        
        if page == None:
            page = 1
            
        page = int(page) 
    
        context={
            "top_classes" :classes_serializer.data,
            "courses" : course_serializer.data,
            "page": page, 
            "pages": paginator.num_pages
        }
    except:
        sch_courses = Courses.objects.filter(schools=obj).all()
        classes_by_sch = Classes.objects.filter(schools=obj).all()[:4]
        paginator = Paginator(sch_courses,20)
            
        try:
            sch_courses = paginator.page(page)
        except PageNotAnInteger:
            sch_courses = paginator.page(1)
        except EmptyPage:
            page = paginator.num_pages
            sch_courses = paginator.page(paginator.num_pages)
    
        course_serializer = CoursesSerializer(sch_courses,many=True)
        classes_serializer = ClassesSerializer(classes_by_sch,many=True)
        
        if page == None:
            page = 1
            
        page = int(page) 
    
        context={
            "top_classes" :classes_serializer.data,
            "courses" : course_serializer.data,
            "page": page, 
            "pages": paginator.num_pages
        }
            
    
    obj.most_viewed = obj.most_viewed + 1
    obj.save()   
    return Response(context,status=200)


@api_view(['GET'])
def schools_page_test(request,*args,**kwargs):
    obj = Schools.objects.all()
    page = request.query_params.get("page")
    paginator = Paginator(obj,40)
    
    try:
        obj = paginator.page(page)
    except PageNotAnInteger:
        obj = paginator.page(1)
    except EmptyPage:
        obj = paginator.page(paginator.num_pages)
    
    if page == None:
        page = 1

    page = int(page)

    serializer = SchoolsSerializer(obj,many=True)
    
    return Response({'schools': serializer.data, 'page': page, 'pages': paginator.num_pages},status=200)

@api_view(['GET'])
def courses_all(request,*args,**kwargs):
    obj = Courses.objects.all()[:50]
    serializer = CoursesSerializer(obj,many=True)
    return Response(serializer.data,status=200)


@api_view(['GET'])
def courses(request,*args,**kwargs):
    obj = Courses.objects.all()
    
    page = request.query_params.get("page")
    query = request.query_params.get("query")
    topic = request.query_params.get("topic") #values are "old or newest"
    school = request.query_params.get("school")
    level = request.query_params.get("level")
    price = request.query_params.get("price")
    course = request.query_params.get("course")
    
    try:
        if obj:
            if query:
                
                obj = obj.filter(Q(title__icontains=query)| Q(name__icontains=query)| Q(price__icontains=query) | Q(levels__icontains=query)| Q(schools__name__icontains=query) | Q(teacher_name__icontains=query)| Q(level__icontains=query))
            
            if topic:
                if topic == "newest":
                    obj = obj.filter(date__lte = datetime.now() + relativedelta(month =+12) )
                else:
                    obj = obj.filter(date__gt = datetime.now() + relativedelta(month =+12) )
            if level:
                obj = obj.filter(levels= level)
            if price:
                try:
                    obj = obj.filter(price__lt = int(price))
                except:
                    if price == "free":
                        obj = obj.filter(price = None)
                    else:
                        obj = obj.filter(price__gt = 9000)
            if school:
                obj = obj.filter(schools__name = school)
            if course and course != "All":
                obj = obj.filter(title = course)
                
        obj2= Classes.objects.all()[:4]
        seri= ClassesSerializer(obj2,many=True)
        
        paginator = Paginator(obj,20)
        
        try:
            obj = paginator.page(page)
        except PageNotAnInteger:
            obj = paginator.page(1)
        except EmptyPage:
            page = paginator.num_pages
            obj = paginator.page(paginator.num_pages)
        
        serializer = CoursesSerializer(obj,many=True)
        
        if page == None:
            page = 1
            
        page = int(page)
        context={
            "top_classes" :seri.data,
            "courses" : serializer.data,
            "page": page, 
            "pages": paginator.num_pages
        }
    except:
        obj = Courses.objects.all()
        obj2= Classes.objects.all()[:4]

        paginator = Paginator(obj,20)
            
        try:
            obj = paginator.page(page)
        except PageNotAnInteger:
            obj = paginator.page(1)
        except EmptyPage:
            page = paginator.num_pages
            obj = paginator.page(paginator.num_pages)
    
        course_serializer = CoursesSerializer(obj,many=True)
        classes_serializer = ClassesSerializer(obj2,many=True)
        
        if page == None:
            page = 1
            
        page = int(page) 
    
        context={
            "top_classes" :classes_serializer.data,
            "courses" : course_serializer.data,
            "page": page, 
            "pages": paginator.num_pages
        } 
    return Response(context,status=200)



@api_view(['GET'])
def skills(request,skill="",*args,**kwargs):
    obj = Skills.objects.all()
    
    page = request.query_params.get("page")
    query = request.query_params.get("query")
    topic = request.query_params.get("topic") #values are "old or newest"
    school = request.query_params.get("school")
    level = request.query_params.get("level")
    price = request.query_params.get("price")
    course = request.query_params.get("course")
    owen = str(skill)
    if skill:
        obj = Skills.objects.filter(title=owen).all()
        
        if not obj:
            message = {'detail': 'Skill does not exist'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
    try:
        if obj:
            
            if query:
                obj = obj.filter(Q(title__icontains=query)| Q(name__icontains=query)| Q(price__icontains=query) | Q(levels__icontains=query) | Q(teacher_name__icontains=query)| Q(level__icontains=query))
            if topic:
                if topic == "newest":
                    obj = obj.filter(date__lte = datetime.now() + relativedelta(month =+12) )
                else:
                    obj = obj.filter(date__gt = datetime.now() + relativedelta(month =+12) )
            if level:
                obj = obj.filter(levels= level)
            if price:
                try:
                    obj = obj.filter(price__lt = int(price))
                except:
                    if price == "free":
                        obj = obj.filter(price = None)
                    else:
                        obj = obj.filter(price__gt = 9000)
            if course and course != "All":
                if course == "manual skills":
                    obj = obj.filter(manual_skill = True)
                elif course == "soft skills":
                    obj = obj.filter(manual_skill = False) 
            if school:
                obj = []
            paginator = Paginator(obj,20)
            
            try:
                obj = paginator.page(page)
            except PageNotAnInteger:
                obj = paginator.page(1)
            except EmptyPage:
                page = paginator.num_pages
                obj = paginator.page(paginator.num_pages)
            
            serializer = SkillsSerializer(obj,many=True)
            if page == None:
                page = 1
                
            page = int(page)
            context={
                "skills" :serializer.data,
                "page": page, 
                "pages": paginator.num_pages
            }
            return Response(context,status=200)
        return Response({},status=404)
    except:
        paginator = Paginator(obj,20)
            
        try:
            obj = paginator.page(page)
        except PageNotAnInteger:
            obj = paginator.page(1)
        except EmptyPage:
            page = paginator.num_pages
            obj = paginator.page(paginator.num_pages)
    
        serializer = SkillsSerializer(obj,many=True)
        
        if page == None:
            page = 1
            
        page = int(page) 
    
        context={
            "skills" :serializer.data,
            "page": page, 
            "pages": paginator.num_pages
        }
        return Response(context,status=200)
    return Response({},status=404)



@api_view(['GET'])
def materials(request,pk="",*args,**kwargs):
    page = request.query_params.get("page")
    query = request.query_params.get("query")
    topic = request.query_params.get("topic") #values are "old or newest"
    school = request.query_params.get("school")
    level = request.query_params.get("level")
    price = request.query_params.get("price")
    course = request.query_params.get("course")
    
    if pk:
        pk=int(pk)
        sch = Schools.objects.get(pk=pk)
        if sch:
            # course = Courses.objects.filter(schools=sch).all()
            obj = Materials.objects.filter(schools=sch).all()
            
            
            try:
                if obj:
                    if query:
                        obj = obj.filter(Q(course_name__icontains=query)| Q(material_title__icontains=query)| Q(price__icontains=query) | Q(levels__icontains=query)| Q(schools__name__icontains=query) | Q(author__icontains=query))
                    if topic:
                        if topic == "newest":
                            obj = obj.filter(date__lte = datetime.now() + relativedelta(month =+12) )
                        else:
                            obj = obj.filter(date__gt = datetime.now() + relativedelta(month =+12) )
                    
                    if price:
                        try:
                            obj = obj.filter(price__lt = int(price))
                        except:
                            if price == "free":
                                obj = obj.filter(price = None)
                            else:
                                obj = obj.filter(price__gt = 9000)
                    if school:
                        obj = obj.filter(schools__name = school)
                    if course and course != "All":
                        obj = obj.filter(course_name = course)
                        
                # seri= CoursesSerializer(course,many=True)
                
                paginator = Paginator(obj,20)
                
                try:
                    obj = paginator.page(page)
                except PageNotAnInteger:
                    obj = paginator.page(1)
                except EmptyPage:
                    page = paginator.num_pages
                    obj = paginator.page(paginator.num_pages)
                
                serializer = MaterialsSerializer(obj,many=True)
                
                if page == None:
                    page = 1
                    
                page = int(page)
                context={
                    # "courses" :seri.data,
                    "materials" : serializer.data,
                    "page": page, 
                    "pages": paginator.num_pages
                }
                return Response(context,status=200)
            except:
                # obj2 = Courses.objects.all()

                paginator = Paginator(obj,20)
                    
                try:
                    obj = paginator.page(page)
                except PageNotAnInteger:
                    obj = paginator.page(1)
                except EmptyPage:
                    page = paginator.num_pages
                    obj = paginator.page(paginator.num_pages)
            
                # course_serializer = CoursesSerializer(obj2,many=True)
                matz = MaterialsSerializer(obj,many=True)
                
                if page == None:
                    page = 1
                    
                page = int(page) 
            
                context={
                    "materials" :matz.data,
                    # "courses" : course_serializer.data,
                    "page": page, 
                    "pages": paginator.num_pages
                } 
                return Response(context,status=200)
            
        else:
            message = {'detail': 'School with such material does not exist'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
    else:
        # course = Courses.objects.all()
        obj = Materials.objects.all()
        
        try:
            if obj:
                if query:
                    obj = obj.filter(Q(course_name__icontains=query)| Q(material_title__icontains=query)| Q(price__icontains=query) | Q(levels__icontains=query)| Q(schools__name__icontains=query) | Q(author__icontains=query))
                if topic:
                    if topic == "newest":
                        obj = obj.filter(date__lte = datetime.now() + relativedelta(month =+12) )
                    else:
                        obj = obj.filter(date__gt = datetime.now() + relativedelta(month =+12) )
                
                if price:
                    try:
                        obj = obj.filter(price__lt = int(price))
                    except:
                        if price == "free":
                            obj = obj.filter(price = None)
                        else:
                            obj = obj.filter(price__gt = 9000)
                if school:
                    obj = obj.filter(schools__name = school)
                if course and course != "All":
                    obj = obj.filter(course_name = course)
                    
            # seri= CoursesSerializer(course,many=True)
            
            paginator = Paginator(obj,20)
            
            try:
                obj = paginator.page(page)
            except PageNotAnInteger:
                obj = paginator.page(1)
            except EmptyPage:
                page = paginator.num_pages
                obj = paginator.page(paginator.num_pages)
            
            serializer = MaterialsSerializer(obj,many=True)
            
            if page == None:
                page = 1
                
            page = int(page)
            context={
                # "courses" :seri.data,
                "materials" : serializer.data,
                "page": page, 
                "pages": paginator.num_pages
            }
            return Response(context,status=200)
        except:
            # obj2 = Courses.objects.all()

            paginator = Paginator(obj,20)
                
            try:
                obj = paginator.page(page)
            except PageNotAnInteger:
                obj = paginator.page(1)
            except EmptyPage:
                page = paginator.num_pages
                obj = paginator.page(paginator.num_pages)
        
            # course_serializer = CoursesSerializer(obj2,many=True)
            matz = MaterialsSerializer(obj,many=True)
            
            if page == None:
                page = 1
                
            page = int(page) 
        
            context={
                "materials" :matz.data,
                # "courses" : course_serializer.data,
                "page": page, 
                "pages": paginator.num_pages
            } 
            return Response(context,status=200)
        
    message = {'detail': 'Material does not exist'}
    return Response(message, status=status.HTTP_400_BAD_REQUEST)
        


@api_view(['GET'])
def classes(request,*args,**kwargs):
    obj = Classes.objects.all()
    serializer = ClassesSerializer(obj,many=True)
    return Response(serializer.data,status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notifications(request,*args,**kwargs):
    user = request.user
    obj = Notification.objects.filter(owner__id = user.id).all()
    serializer = NotificationSerializer(obj,many=True)
    return Response(serializer.data,status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile (request,*args,**kwargs):
    user = request.user
    obj = Profile.objects.filter(user__id = user.id).first()
    serializer = ProfileSerializer(obj)
    return Response(serializer.data,status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_comments (request,pk,*args,**kwargs):
    user = request.user
    obj2 = Comments.objects.filter(tutorial__id = int(pk)).first()
    if not obj2:
        return Response({},status=404)
    obj = obj2.chats.all()
    serializer = CommentSerializer(obj,many=True)
    return Response(serializer.data,status=200)


@api_view(['GET'])
def tutorials(request,*args,**kwargs):
    obj = Tutorial.objects.all()
    
    page = request.query_params.get("page")
    query = request.query_params.get("query")
    topic = request.query_params.get("topic") #values are "old or newest"
    school = request.query_params.get("school")
    level = request.query_params.get("level")
    price = request.query_params.get("price")
    course = request.query_params.get("course")
    
    try:
        if obj:
            if query:
                obj = obj.filter(Q(course_name__icontains=query) | Q(topic__icontains=query)| Q(price__icontains=query) | Q(levels__icontains=query) | Q(which_tutor__first_name__icontains=query)| Q(level__icontains=query))
            
            if topic:
                if topic == "newest":
                    obj = obj.filter(date__lte = datetime.now() + relativedelta(month =+12) )
                else:
                    obj = obj.filter(date__gt = datetime.now() + relativedelta(month =+12) )
            if level:
                obj = obj.filter(levels= level)
            if price:
                try:
                    obj = obj.filter(price__lt = int(price))
                except:
                    if price == "free":
                        obj = obj.filter(price = None)
                    else:
                        obj = obj.filter(price__gt = 9000)
            
            if course and course != "All":
                obj = obj.filter(course_name = course)
        
        paginator = Paginator(obj,20)
        
        try:
            obj = paginator.page(page)
        except PageNotAnInteger:
            obj = paginator.page(1)
        except EmptyPage:
            page = paginator.num_pages
            obj = paginator.page(paginator.num_pages)
        
        seri = TutorialSerializer(obj,many=True)
        
        if page == None:
            page = 1
            
        page = int(page)
        context={
            "tutorials" :seri.data,
            "page": page, 
            "pages": paginator.num_pages
        }
    except:
        paginator = Paginator(obj,20)
        try:
            obj = paginator.page(page)
        except PageNotAnInteger:
            obj = paginator.page(1)
        except EmptyPage:
            page = paginator.num_pages
            obj = paginator.page(paginator.num_pages)
    
        seri = TutorialSerializer(obj,many=True)
        
        if page == None:
            page = 1
            
        page = int(page) 
    
        context={
            "tutorials" :seri.data,
            "page": page, 
            "pages": paginator.num_pages
        }
    
    return Response(context,status=200)


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def testing(request,*args,**kwargs):
    print("xup")
    return Response("context",status=200)

@api_view(['GET','POST','PUT'])
@permission_classes([IsAuthenticated])
def continue_reg(request):
    data = request.data
    user = request.user.id
    profile = Profile.objects.get(pk=user)
    if not user:
        message = {'detail': 'User with this profile does not exist'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    elif data and profile:
        if 'option1' in data:
            profile.cat1 = data['option1']
            profile.save()
        if "option2" in data:
            profile.cat2 = data['option2']
            profile.save()
        if "option3" in data:
            profile.cat3 = data['option3']
            profile.save()
        if "option4" in data:
            profile.cat4 = data['option4']
            profile.save()
        profile.done = True
        profile.save()
        serializer = ProfileSerializer(profile)
        return Response(serializer.data,status=201)
    elif not data and profile:
        profile.done = True
        profile.save()
        serializer = ProfileSerializer(profile)
        return Response(serializer.data,status=201)
    else:
        message = {'detail': 'An Error occurred'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def comments(request):
    data = request.data
    user=request.user
    the_comment = Comments_Holder.objects.create(
        user=user,
        name=user.first_name,
        text=data['message']
    )
    pro_comment = Comments.objects.get(pk = int(data["id"]))
    pro_comment.chats.add(the_comment)
    return Response("success",status=201)


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def announcement_update(request):
    data = request.data
    user=request.user
    announcement = Announcements.objects.create(
        user=user,
        title=data['hed'],
        notification=data['message']
    )
    tutorial = Tutorial.objects.get(pk = int(data["id"]))
    tutorial.announcement.add(announcement)
    return Response("success",status=201)



@api_view(['GET','POST'])
def registerUser(request):
    data = request.data
    try:
        user = User.objects.create(
            first_name=data['first_name'],
            username=data['email'],
            email=data['email'],
            password=make_password(data['password'])
        )
        ip = None
        try:
            ip = request.META.get('REMOTE_ADDR')
        except:
            try:
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[-1].strip()
            except:
                ip= None
            
        Logged_In_User_Jwt_Rec.objects.create(
            user = user,
            ip_address= ip,
            date= datetime.now() + timedelta(hours=12)
        )
        # I wanted to add conversion rate to the admin
        # user_xchng =
        # serializer = UserSerializerWithToken(user,context={"amount":})
        serializer = UserSerializerWithToken(user)
        return Response(serializer.data,status=201)
    except:
        message = {'detail': 'User with this email already exist'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','POST'])
def logout(request):
    data = request.data
    print(data)
    user = User.objects.filter(email = data["email"]).first()
    delUser= Logged_In_User_Jwt_Rec.objects.filter(user=user).first()
    print(delUser)
    
    if delUser:
        delUser.delete()
        print("Deleted")
        
    return Response({"success":"success"},status=201)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # ip = None
        # try:
        #     ip = request.META.get('REMOTE_ADDR')
        #     print(ip,"one")
        # except:
        #     try:
        #         x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        #         if x_forwarded_for:
        #             ip = x_forwarded_for.split(',')[-1].strip()
        #             print(ip,"two")
        #     except:
        #         ip= None
    
        serializer = UserSerializerWithToken(self.user).data

        check_multi_auth = Logged_In_User_Jwt_Rec.objects.filter(user=self.user).all()
        if not check_multi_auth:
            Logged_In_User_Jwt_Rec.objects.create(
                user = self.user,
                date= datetime.now() + timedelta(hours=12)
            )
        elif check_multi_auth and check_multi_auth.count() < 4:
            Logged_In_User_Jwt_Rec.objects.create(
                user = self.user,
                date= datetime.now(tz=timezone.utc) + timedelta(hours=12)
            )
        elif check_multi_auth and check_multi_auth.count() > 2 and check_multi_auth.count() < 4:
            gg = True
            for i in check_multi_auth:
                if i.date > timezone.now():
                    pass
                else:
                    i.delete()
                    Logged_In_User_Jwt_Rec.objects.create(
                        user = self.user,
                        date= datetime.now() + timedelta(hours=12)
                    )
                    gg = False
            if gg == True:
                for k, v in serializer.items():
                    data[k] = v
                data["error"] = "Please logout from previously used device"
                return data
        elif check_multi_auth and check_multi_auth.count() > 3:
            for k, v in serializer.items():
                    data[k] = v
            data["error"] = "Please logout from previously used device"
            # message = json.dumps({'detail': 'Please logout from previously used device'})
            return data
            
            # Logout should contain email from frontend and we del
            # this user
        for k, v in serializer.items():
            data[k] = v

        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    

class GoogleAuthApiView(APIView):
    def post(self, request):
        token = request.data.get("token")["access_token"]
        payload = {'access_token': token}  # validate the token
        r = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', params=payload)
        data = json.loads(r.text)
        
        if 'error' in data:
            raise exceptions.AuthenticationFailed("unauthenticated")
            

        # create user if not exist
        try:
            user = User.objects.get(email=data['email'])
            serializer = UserSerializerWithToken(user)
            return Response(serializer.data,status=201)
        except User.DoesNotExist:
            user = User.objects.create(
                first_name= data["name"],
                username = data["email"],
                email = data["email"]
            )
            user.set_password(token)
            user.save()
            serializer = UserSerializerWithToken(user)
            return Response(serializer.data,status=201)
        






def send_reset_email2(user):
    token = user.get_reset_token()
    user= user.user
    html_massage= f"""
        <div style="display:flex;margin-top:15px;">
            <div style="margin:auto">
                <div style="max-width: 667px; text-align:initial;">
                    <div style=" padding: 5px 10px;background-color: white; ">
                        <div style="background:#040D36;padding:0 10px">
                            <svg style="max-height: 60px;" viewBox="0 0 84 54" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M42.3449 32.8517C41.0218 32.8517 40.018 32.5233 39.3335 31.8663C38.649 31.2048 38.3068 30.2745 38.3068 29.0755V22.6117H40.1811V28.917C40.1811 29.7577 40.3511 30.371 40.691 30.7569C41.0356 31.1428 41.5984 31.3357 42.3793 31.3357C43.1465 31.3357 43.7024 31.1428 44.047 30.7569C44.3915 30.3664 44.5638 29.7508 44.5638 28.9101V22.6117H46.4312V29.0893C46.4312 30.2791 46.0821 31.2048 45.3838 31.8663C44.6855 32.5233 43.6726 32.8517 42.3449 32.8517ZM50.2012 32.8449C49.0848 32.8449 48.1913 32.6542 47.5206 32.2729L47.7066 30.9154C48.0098 31.0808 48.3957 31.2301 48.8643 31.3633C49.3329 31.4919 49.7602 31.5562 50.146 31.5562C50.5457 31.5562 50.8558 31.4827 51.0763 31.3357C51.3014 31.1841 51.4163 30.9636 51.4209 30.6742C51.4209 30.4123 51.3152 30.2056 51.1039 30.054C50.8972 29.9024 50.4998 29.714 49.9118 29.4889C49.7096 29.4154 49.5787 29.3672 49.519 29.3442C48.8207 29.0732 48.3176 28.7723 48.0098 28.4415C47.702 28.1061 47.5481 27.6536 47.5481 27.084C47.5481 26.3949 47.7962 25.8666 48.2924 25.499C48.7931 25.1315 49.4891 24.9478 50.3803 24.9478C51.3451 24.9478 52.1927 25.1292 52.9231 25.4922L52.4752 26.7394C51.7539 26.4041 51.0671 26.2364 50.4148 26.2364C50.0519 26.2364 49.767 26.2984 49.5603 26.4224C49.3582 26.5419 49.2571 26.7256 49.2571 26.9737C49.2571 27.208 49.3559 27.3918 49.5534 27.525C49.751 27.6536 50.1369 27.8236 50.7111 28.0349C50.7295 28.0395 50.7892 28.0602 50.8903 28.097C50.9913 28.1337 51.0694 28.1636 51.1246 28.1865C51.8183 28.4392 52.3282 28.7424 52.6544 29.0961C52.9805 29.4453 53.1436 29.9024 53.1436 30.4675C53.139 31.2255 52.8818 31.8112 52.3718 32.2247C51.8619 32.6381 51.1384 32.8449 50.2012 32.8449ZM57.0376 32.8104C56.5231 32.8104 56.0935 32.7507 55.749 32.6312C55.409 32.5072 55.1426 32.3142 54.9496 32.0524C54.7567 31.7905 54.6189 31.4827 54.5362 31.129C54.4581 30.7707 54.419 30.3296 54.419 29.8059V26.2295H53.1786L53.2476 25.251L54.5431 25.1338L55.1219 23.0803L56.2245 23.0734V25.1338H58.1057V26.2295H56.2245V29.8404C56.2245 30.4146 56.3072 30.8235 56.4725 31.067C56.6379 31.3105 56.9434 31.4322 57.389 31.4322C57.6509 31.4322 57.9311 31.4092 58.2297 31.3633L58.278 32.6588C58.2688 32.6588 58.2114 32.6703 58.1057 32.6932C58.0046 32.7116 57.9059 32.7277 57.8094 32.7415C57.7175 32.7599 57.5981 32.7759 57.4511 32.7897C57.3041 32.8035 57.1662 32.8104 57.0376 32.8104ZM64.4529 32.1144C63.8511 32.606 63.0586 32.8517 62.0755 32.8517C61.0924 32.8517 60.2999 32.606 59.6981 32.1144C59.1009 31.6228 58.8022 30.9016 58.8022 29.9506V25.1338H60.6146V29.8817C60.6146 30.4468 60.7317 30.8556 60.966 31.1083C61.2049 31.361 61.5816 31.4873 62.0961 31.4873C62.6015 31.4873 62.969 31.3633 63.1987 31.1152C63.433 30.8625 63.5501 30.4514 63.5501 29.8817V25.1338H65.3556V29.9506C65.3556 30.897 65.0547 31.6183 64.4529 32.1144ZM69.2633 32.8517C68.2756 32.8517 67.4992 32.4888 66.9342 31.763C66.3691 31.0371 66.0866 30.0678 66.0866 28.855C66.0866 27.6789 66.3668 26.7348 66.9273 26.0228C67.4924 25.3061 68.2687 24.9478 69.2564 24.9478C70.3314 24.9478 71.0918 25.3291 71.5374 26.0917C71.4914 25.6415 71.4685 25.2073 71.4685 24.7893V22.343L73.2739 22.2258V32.707H71.7096L71.5098 31.6734C71.4317 31.7974 71.3582 31.9054 71.2893 31.9973C71.225 32.0845 71.1285 32.1879 70.9999 32.3074C70.8712 32.4222 70.7311 32.5164 70.5795 32.5899C70.4325 32.6588 70.2442 32.7185 70.0145 32.7691C69.7894 32.8242 69.539 32.8517 69.2633 32.8517ZM69.6906 31.4804C70.9034 31.4804 71.519 30.6558 71.5374 29.0066C71.5374 28.074 71.3812 27.3941 71.0688 26.9668C70.7564 26.5396 70.2901 26.326 69.6699 26.326C69.1278 26.326 68.6937 26.5442 68.3675 26.9806C68.0459 27.4124 67.8851 28.051 67.8851 28.8963C67.8851 29.737 68.0459 30.3779 68.3675 30.8189C68.6937 31.2599 69.1347 31.4804 69.6906 31.4804ZM76.5615 32.8517C75.8586 32.8517 75.2889 32.6588 74.8525 32.2729C74.4207 31.8824 74.2047 31.3219 74.2047 30.5915C74.2047 29.8059 74.462 29.2248 74.9765 28.8481C75.4911 28.4668 76.2674 28.2256 77.3057 28.1245C77.4481 28.1061 77.602 28.0878 77.7674 28.0694C77.9328 28.051 78.1188 28.0326 78.3256 28.0143C78.5323 27.9959 78.6954 27.9798 78.8148 27.966V27.5663C78.8148 27.1069 78.7092 26.7739 78.4978 26.5671C78.2865 26.3558 77.9649 26.2502 77.5331 26.2502C76.9175 26.2502 76.1572 26.4224 75.2522 26.767C75.2476 26.7532 75.1718 26.5442 75.0248 26.1399C74.8778 25.7356 74.802 25.5289 74.7974 25.5197C75.6886 25.1384 76.6533 24.9478 77.6916 24.9478C78.7115 24.9478 79.4534 25.1706 79.9174 25.6162C80.3814 26.0572 80.6134 26.7739 80.6134 27.7662V32.707H79.2765C79.2719 32.6887 79.2214 32.5348 79.1249 32.2453C79.0284 31.9559 78.9802 31.802 78.9802 31.7836C78.6035 32.1512 78.2337 32.4222 77.8708 32.5968C77.5124 32.7668 77.076 32.8517 76.5615 32.8517ZM77.0507 31.57C77.4688 31.57 77.8317 31.4712 78.1395 31.2737C78.4519 31.0716 78.6747 30.8281 78.8079 30.5433V29.0824C78.7941 29.0824 78.6724 29.0916 78.4427 29.1099C78.2176 29.1283 78.0959 29.1375 78.0775 29.1375C77.347 29.2018 76.8118 29.3396 76.4719 29.551C76.1319 29.7623 75.9619 30.1022 75.9619 30.5708C75.9619 30.8924 76.0561 31.1405 76.2445 31.315C76.4328 31.485 76.7016 31.57 77.0507 31.57Z" fill="white"/>
                                <path d="M-7.55457e-07 18.3597L22.7993 18.3597C25.0912 18.3597 27.2892 19.2702 28.9097 20.8907C30.5303 22.5113 31.4408 24.7093 31.4408 27.0012C31.4408 29.293 30.5303 31.491 28.9097 33.1116C27.2892 34.7321 25.0912 35.6426 22.7993 35.6426L0 35.6426L-2.22713e-07 30.5475L22.7993 30.5475C23.27 30.5559 23.7376 30.4704 24.1748 30.2961C24.6121 30.1218 25.0103 29.8621 25.3461 29.5322C25.6819 29.2023 25.9486 28.8089 26.1307 28.3748C26.3127 27.9407 26.4065 27.4747 26.4065 27.004C26.4065 26.5332 26.3127 26.0672 26.1307 25.6331C25.9486 25.199 25.6819 24.8056 25.3461 24.4757C25.0103 24.1458 24.6121 23.8861 24.1748 23.7118C23.7376 23.5375 23.27 23.452 22.7993 23.4604L-5.32499e-07 23.4604L-7.55457e-07 18.3597Z" fill="#2E54FF"/>
                                <path d="M0 28.3906L-1.21496e-07 25.6111L22.6994 25.6111C23.4669 25.6111 24.0891 26.2333 24.0891 27.0009V27.0009C24.0891 27.7684 23.4669 28.3906 22.6994 28.3906L0 28.3906Z" fill="#2E54FF"/>
                            </svg>
                        </div>
                        <div style="padding-top: 25px; font-size:18px;">
                            To reset your password click on the button bellow:
                        </div>
                        <div style="padding-top: 25px; font-size:18px;">
                            <a href="{settings.FRONTEND_URL}/reset-password/reset/{token}" style="padding:8px 20px; background-color: #2E54FF;text-decoration:none;color:#fff">Reset password</a>
                        </div>
                        <div style="padding-top: 30px; font-size:18px;">
                            Or copy and paste the following link into your browser url {settings.FRONTEND_URL}/reset-password/reset/{token}
                        </div>
                        <div style="padding-top: 25px; font-size:18px;">
                            Please note that this link is only valid for 10 minutes.
                        </div>
                        <div style="padding-top: 30px; font-size:18px;">
                            If you are unaware of this request, simply ignore this email and no changes will be made to your account.
                        </div>
                    </div>
                </div>
            </div>
        </div>
    """
    subject, to = 'Reset password', user.email
    text_content = ''
    form_email = "ctdigitaltech@gmail.com"
    msg = EmailMultiAlternatives(subject, text_content,form_email, [to])
    msg.attach_alternative(html_massage, "text/html")
    msg.send(fail_silently=False)
    
    
    
    

@api_view(['GET','POST'])
def reset_request(request,*args,**kwargs):
    
    data = request.data
    user = User.objects.filter(email=data["email"]).first()
    if not user:
        message = {'detail': 'An Error occurred'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    profile= Profile.objects.filter(user=user).first()
    send_reset_email2(profile)
    return Response({"success":"success"},status=200)
    
    


@api_view(['GET','POST'])
def reset_token(request,*args,**kwargs):
    # if request.user:
    #     message = {'detail': 'An Error occurred'}
    #     return Response(message, status=status.HTTP_400_BAD_REQUEST)
    
    data = request.data
    user = Profile.verify_reset_token(data["token"])
    if user is None:
        message = {'detail': 'That is invalid or expired token. Please request reset password again'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    if not data:
        message = {'detail': 'An Error occurred'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    user.password=make_password(data['password'])
    user.save()
    # redirect to login
    return Response({"success":"success"},status=201)






# class GoogleView(APIView):
#     def post(self, request):
#         payload = {'access_token': request.data.get("token")}  # validate the token
#         r = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', params=payload)
#         data = json.loads(r.text)

#         if 'error' in data:
#             content = {'message': 'wrong google token / this google token is already expired.'}
#             return Response(content)

#         # create user if not exist
#         try:
#             user = User.objects.get(email=data['email'])
#         except User.DoesNotExist:
#             user = User()
#             user.username = data['email']
#             # provider random default password
#             user.password = make_password(BaseUserManager().make_random_password())
#             user.email = data['email']
#             user.save()

#         token = RefreshToken.for_user(user)  # generate token without username & password
#         response = {}
#         response['username'] = user.username
#         response['access_token'] = str(token.access_token)
#         response['refresh_token'] = str(token)
#         return Response(response)



# class GoogleAuthApiView(APIView):
#     def post(self, request):
#         token = request.data.get("token")
        
#         googleUser = id_token.verify_token(token, GoogleRequest())
        
#         if not googleUser:
#             raise exceptions.AuthenticationFailed("unauthenticated")
#         user = User.objects.filter(email=googleUser["email"]).first()
        
#         if not user:
#             user = User.objects.create(
#                 first_name= f"{googleUser['given_name']} {googleUser['family_name']}",
#                 username = googleUser["email"],
#                 email = googleUser["email"]
#             )
#             user.set_password(BaseUserManager().make_random_password())
#             user.save()
#             serializer = UserSerializerWithToken(user)
#             return Response(serializer.data,status=201)
#         elif user :
#             serializer = UserSerializerWithToken(user)
#             return Response(serializer.data,status=201)
