from rest_framework import serializers
from .models import Comments_Holder, Courses,Profile, Skills, Tutorial,Schools,Materials,Classes,Notification,Announcements
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class SkillsSerializer(serializers.ModelSerializer):
    classes= serializers.SerializerMethodField(read_only= True)
    students= serializers.SerializerMethodField(read_only= True)
    materials= serializers.SerializerMethodField(read_only= True)
    class Meta:
        model = Skills
        fields = [
                "id","title","name","details","detailed_summary_of_course","materials","image",
                "classes","total_hour","levels","level","manual_skill",
                "price","students","teacher_name","teacher_image_or_logo",
                "brief_about_teacher","last_modified","most_viewed","date"
            ]
    
    def get_classes(self,obj):
        return obj.classes.count()
    def get_materials(self,obj):
        return obj.materials.count()
    def get_students(self,obj):
        return obj.students.count()

class TutorialSerializer(serializers.ModelSerializer):
    students= serializers.SerializerMethodField(read_only= True)
    materials= serializers.SerializerMethodField(read_only= True)
    tutor= serializers.SerializerMethodField(read_only= True)
    class Meta:
        model = Tutorial
        fields = [
            "id","course_name","topic","level","detail","started","tutorial_time",
            "price","link","course_image","students","name_of_tutor","tutors_image","expire_time",
            "last_seen","date","levels","about_teacher","materials","waiting_tutor","tutor"
        ]
    def get_students(self,obj):
        return obj.students.count()
    def get_tutor(self,obj):
        ids = None
        if obj.which_tutor:
            ids = obj.which_tutor.id
        return ids
    def get_materials(self,obj):
        return obj.materials.count()
    
    
class SchoolsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schools
        fields = [
            "id","name","state","address","info","logo","date"
        ]

class MaterialsSerializer(serializers.ModelSerializer):
    schools = serializers.SerializerMethodField(read_only= True)
    class Meta:
        model = Materials
        fields = ["id","author","material","detailed_summary_of_material","course_name","levels","schools","material_title","price","date","image","last_modified","pages"]
    
    def get_schools(self,obj):
        return obj.schools.name
    

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments_Holder
        fields = ["id","name","text"]
    


class ClassesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classes
        fields = ["id","class_time","course_name","topic","link","level","price","date","last_modified","image"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id","topic","types","user","action","image","date"]

class AnnouncementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcements
        fields = ["id","title","notification","date"]

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Profile
        fields = ["id","user","email","school","image","done"]
    
    def get_user(self,obj):
        return f"{obj.user.first_name}"
    def get_email(self,obj):
        return obj.user.email


class CoursesSerializer(serializers.ModelSerializer):
    classes= serializers.SerializerMethodField(read_only= True)
    students= serializers.SerializerMethodField(read_only= True)
    school= serializers.SerializerMethodField(read_only= True)
    school_id= serializers.SerializerMethodField(read_only= True)
    materials= serializers.SerializerMethodField(read_only= True)
    class Meta:
        model = Courses
        fields = [
            "id","title","name","details","materials","classes","total_hour",
            "level","tutorials","image","school_logo","is_featured",
            "price","students","last_modified","date","levels","school","detailed_summary_of_course",
            "school_id","teacher_name","teacher_image","brief_about_teacher"
        ]
    def get_classes(self,obj):
        return obj.classes.count()
    def get_materials(self,obj):
        return obj.materials.count()
    def get_students(self,obj):
        return obj.students.count()
    def get_school(self,obj):
        return obj.schools.name
    def get_school_id(self,obj):
        return obj.schools.id
    

class GeneralSerializer(serializers.ModelSerializer):
    schools = serializers.SerializerMethodField(read_only=True)
    classes = serializers.SerializerMethodField(read_only=True)
    tutorials = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Courses
        fields = [
            "id","title","schools","classes","tutorials",
            "price","students","last_modified","date","image"
        ]
    def get_schools(self,obj):
        context = self.context
        schools = context.get("schools")
        return schools
    def get_classes(self,obj):
        context = self.context
        classes = context.get("classes")
        return classes
    def get_tutorials(self,obj):
        context = self.context
        tutorials = context.get("tutorials")
        return tutorials



class UserSerializerWithToken(serializers.ModelSerializer):
    token = serializers.SerializerMethodField(read_only=True)
    # rate = serializers.SerializerMethodField(read_only=True)
    # is_admin = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username','email','first_name', 'token']

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)
    # def get_rate(self,obj):
    #     return obj.last_name
    # def get_is_admin(self, obj):
    #     is_admin = obj.is_admin
    #     return is_admin


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username','email','first_name']













