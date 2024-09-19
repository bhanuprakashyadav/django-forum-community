from django.db import models
from django.contrib.auth.models import User
import uuid 
"""
UUID Generation: uuid.uuid4() generates a random UUID. If you need a different type of UUID (like uuid1 for time-based UUIDs), you can specify it as default=uuid.uuid1.

"""




# -------------------------------COME BACK AFTER WATCHING SYSTEM DESIGN ALL VIDEOS.-----------------------------



class UserField(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_field')
    usrname = models.CharField(max_length=100, unique=True, blank=False)
    usr_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    usr_created_at = models.DateTimeField(auto_now_add=True)
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    has_agreed = models.BooleanField(default=False,blank=False)

    def __str__(self):
        return self.usrname

class PostField(models.Model):    
    # a user can have many Post so, estable a foreign key
    user = models.ForeignKey(UserField, on_delete=models.CASCADE, related_name='posts')
    post_title = models.CharField(max_length=500, blank=False, null=False)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    post_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) #you can do (primary_key=True) if you dont want to use "id" # instead u post_id see 191 on views.py
    
    class Meta:
         permissions = [
            ("can_delete_post", "Can delete post"),
            ("can_delete_any_post", "Can delete any post"),
        ]
                                                                        
                                                            
    
    def __str__(self):
        return self.post_title  # You can customize this as needed


class ReplyField(models.Model):
    post = models.ForeignKey(PostField, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(UserField, on_delete=models.CASCADE)
    reply_text = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reply_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    class Meta:
        
         permissions = [
            ("can_delete_reply", "Can delete reply"),
            ("can_delete_any_reply", "Can delete any reply"),
        ]

    def __str__(self):
        return self.reply_text[:50]

    
    

    
    
    
