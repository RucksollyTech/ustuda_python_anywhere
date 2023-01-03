from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

User = settings.AUTH_USER_MODEL

from django.contrib.auth.models import User as User2


class Tokens(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True) 
    token = models.CharField(max_length=10000)
    date= models.DateTimeField(auto_now_add = True)


class Announcements(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True) 
    title = models.CharField(max_length=10000)
    notification= models.TextField()
    date= models.DateTimeField(auto_now_add = True)
    
    class Meta:
        ordering= ["-id"]
        
    def __str__(self):
        return self.title

class Payment_Information(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True) 
    action = models.CharField(max_length=10)
    reference = models.CharField(max_length=100)
    transaction_id = models.IntegerField(default =1)
    amount = models.IntegerField(default =1)
    item_name = models.TextField(default =1)
    item_title = models.TextField(default =1)
    date= models.DateTimeField(auto_now_add = True)
    
    class Meta:
        ordering= ["-id"]
        
    def __str__(self):
        return f"{self.action} {self.user.email}"


class Schools(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True) 
    name= models.TextField()
    state= models.TextField()
    most_viewed = models.IntegerField(default=1)
    logo = models.ImageField(upload_to ="media/", null=True,blank=True)
    address= models.TextField(default="School information")
    info= models.TextField(default="School information")
    date= models.DateTimeField(auto_now_add = True)
    
    class Meta:
        ordering= ["-most_viewed"]
        
    def __str__(self):
        return self.name


class Materials(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True) 
    course_name = models.CharField(max_length=10000,default="Chemistry")
    author = models.CharField(max_length=10000,null=True,blank=True)
    material_title = models.CharField(max_length=10000,default="Fundamental")
    material = models.FileField(upload_to="media/bkk")
    schools = models.ForeignKey(Schools,on_delete=models.SET_NULL,null=True,blank=True )
    pages = models.IntegerField(default=1)
    detailed_summary_of_material = models.TextField(null=True,blank=True,default="Materials Details")
    price = models.DecimalField(max_digits=10,decimal_places = 1,null = True,blank=True)
    date= models.DateTimeField(auto_now_add = True)
    levels = models.IntegerField(null=True,blank=True,default=100)
    students = models.ManyToManyField(User,blank=True, related_name="material_students" )
    image = models.ImageField(upload_to ="media/", null=True,blank=True)
    most_viewed = models.IntegerField(default=1)
    last_modified =models.DateTimeField(auto_now_add = False,blank=True,null = True)
    
    class Meta:
        ordering= ["-most_viewed"]
    
    def __str__(self):
        return self.course_name

class Classes(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True) 
    course_name = models.CharField(max_length=10000)
    topic = models.CharField(max_length=10000)
    link = models.CharField(max_length=10000)
    class_time = models.CharField(max_length=10000,null=True,blank=True,default="2:20")
    level = models.CharField(max_length=20,default="BEGINNER - ADVANCED")
    schools = models.ForeignKey(Schools,on_delete=models.SET_NULL,null=True,blank=True )
    # schools = models.OneToOneField(Schools,on_delete=models.SET_NULL,null=True,blank=True, related_name="classes_school" )
    image = models.ImageField(upload_to ="media/", null=True,blank=True)
    price = models.DecimalField(max_digits=10,decimal_places = 1,null = True,blank=True)
    last_modified =models.DateTimeField(auto_now_add = False,blank=True,null = True)
    most_viewed = models.IntegerField(default=1)
    date= models.DateTimeField(auto_now_add = True)
    
    class Meta:
        ordering= ["-most_viewed"]
    
    
    def __str__(self):
        return self.course_name

# add name and pix of tutor and can create same tutorial but another tutor
class Tutorial(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True) 
    course_name = models.CharField(max_length=10000,default="Chemistry")
    topic = models.CharField(max_length=10000,default="Molecular Structure Of Mass")
    level = models.CharField(max_length=20,default="BEGINNER - ADVANCED")
    detail = models.TextField()
    started = models.BooleanField(default=False)
    about_teacher = models.TextField(null=True,blank=True,default="Briefly about tutor")
    tutorial_time = models.TextField(null =True, blank=True)
    price = models.DecimalField(max_digits=10,decimal_places = 1,null = True,blank=True)
    link = models.TextField()
    course_image = models.ImageField(upload_to ="media/", null=True,blank=True)
    students = models.ManyToManyField(User,blank=True, related_name="tutorial_students" )
    which_tutor = models.ForeignKey(User,blank=True,on_delete=models.SET_NULL,null=True, related_name="tutorial_tutor")
    waiting_tutor = models.BooleanField(default=False)
    levels = models.IntegerField(null=True,blank=True,default=100)
    name_of_tutor = models.CharField(max_length=10000,default="Mr Ben")
    tutors_image = models.ImageField(upload_to ="media/", null=True,blank=True)
    expire_time =models.DateTimeField(auto_now_add = False)
    last_seen =models.DateTimeField(auto_now_add = False,blank=True,null = True)
    most_viewed = models.IntegerField(default=1)
    date= models.DateTimeField(auto_now_add = True)
    materials = models.ManyToManyField(Materials,blank=True, related_name="tutorial_material")
    announcement = models.ManyToManyField(Announcements,blank=True, related_name="tutorial_announcement")
    
    class Meta:
        ordering= ["-most_viewed"]
    
    def __str__(self):
        return self.course_name
    

class Courses(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True) 
    title = models.CharField(max_length=10000,null=True,blank=True)
    name = models.CharField(max_length=10000,null=True,blank=True)
    details = models.TextField(null=True,blank=True)
    detailed_summary_of_course = models.TextField(null=True,blank=True,default="Lorem ipsum dolor sit amet consectetur adipisicing elit. Autem quibusdam eum explicabo velit cum mollitia vel numquam repellat")
    schools = models.ForeignKey(Schools,on_delete=models.SET_NULL,null=True,blank=True)
    materials = models.ManyToManyField(Materials,blank=True)
    classes = models.ManyToManyField(Classes,blank=True)
    announcement = models.ManyToManyField(Announcements,blank=True)
    total_hour = models.CharField(max_length=10000,null=True,blank=True,default="240 hours")
    levels = models.IntegerField(null=True,blank=True,default=100)
    level = models.CharField(null=True,blank=True,default="BEGINNER - ADVANCED",max_length=20)
    tutorials = models.ManyToManyField(Tutorial,blank=True)
    image = models.ImageField(upload_to ="media/", null=True,blank=True)
    school_logo = models.ImageField(upload_to ="media/", null=True,blank=True)
    price = models.DecimalField(max_digits=10,decimal_places = 1,null = True,blank=True)
    students = models.ManyToManyField(User,blank=True, related_name="course_students")
    teacher_name = models.CharField(max_length=10000,null=True,blank=True)
    teacher_image = models.ImageField(upload_to ="media/", null=True,blank=True)
    brief_about_teacher = models.TextField(null=True,blank=True)
    last_modified =models.DateTimeField(auto_now_add = False,blank=True,null = True)
    most_viewed = models.IntegerField(default=1)
    is_featured= models.BooleanField(default=False)
    date= models.DateTimeField(auto_now_add = True)
    
    class Meta:
        ordering= ["-most_viewed"]
        
    # def my_date(self):
    #     return self.date -
    
    def __str__(self):
        return self.title


# owner here is for people that a particular thing concerns so when we save that sth
# we notify the users on that model
class Notification(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True) 
    owner = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name="not_owner") 
    # owner = models.OneToOneField(User,on_delete=models.SET_NULL,null=True,blank=True, related_name="not_owner") 
    topic = models.TextField(default= "Molecular Structure of Matter")
    image = models.ImageField(upload_to ="media/", null=True,blank=True)
    types = models.CharField(max_length=100,null=True,blank=True, default="Leave this field empty if briefing is needed")
    action = models.TextField(default= "Live tutorial have started")
    date= models.DateTimeField(auto_now_add = True)
    
    def __str__(self):
        return (f"{self.action}")


class Skills(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True) 
    title = models.CharField(max_length=10000,null=True,blank=True)
    name = models.CharField(max_length=10000,null=True,blank=True)
    details = models.TextField(null=True,blank=True)
    detailed_summary_of_course = models.TextField(null=True,blank=True,default="Lorem ipsum dolor sit amet consectetur adipisicing elit. Autem quibusdam eum explicabo velit cum mollitia vel numquam repellat")
    materials = models.ManyToManyField(Materials,blank=True)
    image = models.ImageField(upload_to ="media/", null=True,blank=True)
    classes = models.ManyToManyField(Classes,blank=True)
    announcement = models.ManyToManyField(Announcements,blank=True)
    total_hour = models.CharField(max_length=10000,null=True,blank=True,default="240 hours")
    levels = models.IntegerField(null=True,blank=True,default=100)
    level = models.CharField(null=True,blank=True,default="BEGINNER,INTERMEDIATE,ADVANCE,BEGINNER - ADVANCE",max_length=20)
    price = models.DecimalField(max_digits=10,decimal_places = 1,null = True,blank=True)
    students = models.ManyToManyField(User,blank=True, related_name="skill_students")
    teacher_name = models.CharField(max_length=10000,null=True,blank=True)
    teacher_image_or_logo = models.ImageField(upload_to ="media/", null=True,blank=True)
    brief_about_teacher = models.TextField(null=True,blank=True)
    last_modified =models.DateTimeField(auto_now_add = False,blank=True,null = True)
    most_viewed = models.IntegerField(default=1)
    manual_skill = models.BooleanField(default=False)
    date= models.DateTimeField(auto_now_add = True)
    
    class Meta:
        ordering= ["-most_viewed"]
    
    def __str__(self):
        return self.title


class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    cat1 = models.CharField(max_length=200,null=True,blank=True)
    cat2 = models.CharField(max_length=200,null=True,blank=True)
    cat3 = models.CharField(max_length=200,null=True,blank=True)
    cat4 = models.CharField(max_length=200,null=True,blank=True)
    school= models.TextField(null=True,blank= True)
    done =models.BooleanField(default=False)
    image = models.ImageField(upload_to ="media/", null=True,blank=True)
    date= models.DateTimeField(auto_now_add = True)
    
    
    def get_reset_token(self, expires_sec=600):
        s = Serializer(settings.SECRET_KEY, expires_sec)
        return s.dumps({'user_id': self.user.id}).decode('utf-8')


    @staticmethod
    def verify_reset_token(token):
        s = Serializer(settings.SECRET_KEY)
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User2.objects.get(pk=user_id)
    
    def __str__(self):
        return self.user.email



class Comments_Holder(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True) 
    name= models.CharField(max_length=200,null=True,blank=True)
    text= models.TextField(null=True,blank=True)
    date= models.DateTimeField(auto_now_add = True)
    
    
    def __str__(self):
        return self.name



class Comments(models.Model):
    tutorial = models.ForeignKey(Tutorial,on_delete=models.SET_NULL,null=True,blank=True) 
    chats= models.ManyToManyField(Comments_Holder,blank=True)
    date= models.DateTimeField(auto_now_add = True)
    
    class Meta:
        ordering= ["-date"]
        
    def __str__(self):
        return self.tutorial.course_name


def user_did_save(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
post_save.connect(user_did_save, sender=User)


def comment_did_save(sender, instance, created, *args, **kwargs):
    if created:
        Comments.objects.get_or_create(tutorial=instance)
post_save.connect(comment_did_save, sender=Tutorial)
















