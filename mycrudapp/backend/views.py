from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest, JsonResponse
from .models import UserField, PostField, ReplyField
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import * # for form validation
import json

"""
To add to group programatically

admin_group, _ = Group.objects.get_or_create(name='Admin')
moderator_group, _ = Group.objects.get_or_create(name='Moderator')
user_group, _ = Group.objects.get_or_create(name='User')

this will create group



admin_permissions = Permission.objects.all()  # Admin gets all permissions
moderator_permissions = [
    Permission.objects.get(codename='can_delete_any_post'),
    Permission.objects.get(codename='can_delete_any_reply'),
]

this will assign permissions to group

# Add permissions to groups
admin_group.permissions.set(admin_permissions)
moderator_group.permissions.set(moderator_permissions)

this will add permission to group


to assign users to the group you want
    def assign_user_to_group(user, group_name):
        group = Group.objects.get(name=group_name)
        user.groups.add(group)

check for permission

 if request.user.has_perm('myapp.can_delete_any_post')


"""


# -------------------------------COME BACK AFTER WATCHING SYSTEM DESIGN ALL VIDEOS.-----------------------------

# Handle AJAX query
# https://www.geeksforgeeks.org/how-to-make-ajax-call-from-javascript/
"""

AJAX (Asynchronous JavaScript and XML) is a technique used to create dynamic and interactive web applications. It allows web pages to be updated asynchronously by exchanging small amounts of data with the server behind the scenes. This means that parts of a web page can be updated without reloading the entire page.
"""

def index(request: HttpRequest):
    usr_feat = UserField.objects.all()
    post_feat = PostField.objects.all()
    posts = PostField.objects.all().order_by('-created_at')
    context = {
        'user_field': usr_feat,
        'post_field': post_feat,
        'posts': posts
    }
     
    if request.user.is_authenticated:
        print("I'm authenticated")
        try:
            user_field = UserField.objects.get(user=request.user)
        except UserField.DoesNotExist:
            # If UserField doesn't exist, create one
            user_field = UserField.objects.create(user=request.user, usrname=request.user.username)
        
        context['user_field'] = user_field
        context['profile_pic'] = user_field.profile_pic.url if user_field.profile_pic else None
        context['posts'] = posts
        # Debug
        print(f"Profile pic -> {context['profile_pic']}")
        print(f"The user field is -> {context['user_field']}")
        print(f"The post field is -> {context['posts']}")

    return render(request, 'index.html', context)

def login(request:HttpRequest):
    posts = PostField.objects.all().order_by('-created_at')
    context = {'posts' : posts, 'login_error': 'Username or password field is missing'}
    if request.method == 'POST':
        try:
            username = request.POST['username'] #name='username' in html
            password = request.POST['password']
            rememberMe = request.POST.get('rememberMe') == 'on'
        except KeyError:
            return render(request, 'index.html', context)

        user = authenticate(username=username, password=password)
        
        if not rememberMe:
            if user is not None:
                request.session.set_expiry(0)
                auth.login(request, user)
                return redirect('/')
            else:
                return render(request, 'index.html', context)
                
        else:
            if user is not None:
                request.session.set_expiry(1209600)
                auth.login(request, user)
                return redirect('/')
            # return redirect('index')
            else:
                return render(request, 'index.html', context)
            
    
    return render(request, 'index.html', context)
    # return redirect('index') #'index' defined in urls

# More info - https://docs.djangoproject.com/en/5.0/topics/auth/default/
# User (model) - https://docs.djangoproject.com/en/5.0/ref/contrib/auth/#django.contrib.auth.models.User

def register(request):
    posts = PostField.objects.all().order_by('-created_at')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        isAgreed = request.POST.get('acceptTerms') == 'on'
        
        
        # Check if the username or email already exists and if terms are agreed
        if User.objects.filter(email=email).exists() or User.objects.filter(username=username).exists():
            return render(request, 'index.html', {'signup_error': 'Username or Email already exists', 'posts' : posts})
    
        if not isAgreed:
            return render(request, 'index.html', {'signup_error': 'Please agree to the terms and conditions', 'posts':posts})

        # Create the User instance
        user = User.objects.create_user(username=username, password=password, email=email)

        # Create the UserField instance
        user_field = UserField.objects.create(user=user, usrname=username, has_agreed=isAgreed)
        user_field.save()
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # Log the user in immediately after registration
            auth.login(request, user)
            return redirect('/')
        else:
            return render(request, 'index.html', {'login_error': 'Username or password is incorrect', 'posts':posts})
    
    return render(request, 'index.html', {'posts':posts})

def logout(request:HttpResponse):
    auth.logout(request)
    return redirect('/')

def check_login(request):
    if request.user.is_authenticated:
        return JsonResponse({'authenticated': True, 'username': request.user.username})
    else:
        return JsonResponse({'authenticated': False})
    
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['post_title']
            description = form.cleaned_data['description']
            
            # Get or create the UserField instance
            user_field = UserField.objects.filter(user=request.user).first()
            # user_field, created = UserField.objects.get_or_create(user=request.user)
            
            # Create a new PostField instance
            new_post = PostField.objects.create(user=user_field, post_title=title, description=description)
            new_post.save()
            
            return redirect('post', post_id=new_post.post_id)
        else:
            print(form.errors)
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})

def post(request:HttpRequest, post_id):
    post = get_object_or_404(PostField, post_id=post_id)
    replies = post.replies.all().order_by('-created_at')
    context = {}
    if request.method == 'POST':
        reply_form = ReplyForm(request.POST)
        if reply_form.is_valid():
            reply_text = reply_form.cleaned_data['reply_text']
            user_field = UserField.objects.get(user=request.user)
            context['profile_pic'] = user_field.profile_pic.url if user_field.profile_pic else None
            ReplyField.objects.create(post=post, user=user_field, reply_text=reply_text).save()
            return redirect('post', post_id=post_id)
    else:
        reply_form = ReplyForm()
    context['post'] = post
    context['replies'] = replies
    context['reply_form'] = reply_form
    return render(request, 'post_bp.html', context)

# https://docs.djangoproject.com/en/5.0/ref/templates/api/#built-in-template-context-processors
@login_required
def dashboard_view(request:HttpRequest, username:str):
    # <a href="{% url 'dashboard_view' user.username %}">Dashboard</a>
    # here The user object is available in both the view and the template without you having to pass it explicitly.
    # Django's authentication middleware adds it to the request object and makes it available in templates.
    #context = {'username': username} # 'username' = inhtml, username = the above paramter
    
    user_field = get_object_or_404(UserField, user=request.user) # better to raise 404 instead of DNE
    if request.method == 'POST':
        
        # Handle profile 
        profile_pic = request.FILES.get('profile_pic')
        print(f"I get profilepic {profile_pic}")
        if profile_pic:
            user_field.profile_pic = profile_pic
            user_field.save()
        
        #Handle email
        
        # Find corresp. user's email first
        get_usr = get_object_or_404(User, username=request.user.username)
       
        dashboard_email = request.POST.get('dashboard_email')
                
        if dashboard_email and dashboard_email != get_usr.email:
            current_mail = User.objects.update(email=dashboard_email)
            if current_mail != dashboard_email:
                print("Updated")
            else:
                print("Not updated")
        else:
            print("No change")
            
        dashboard_passwd = request.POST.get('dashboard_password')
        if dashboard_passwd:
            
            # Hash the new password-- Use User.set_password() instead
            #hashed_password = make_password(dashboard_passwd)
            
            # Update the password
            # updated = User.objects.filter(username=request.user.username).update(password=hashed_password)
            get_usr.set_password(dashboard_passwd)
            get_usr.save()     
            
            #Update session to prevent logout
            update_session_auth_hash(request, get_usr)
            
            print("Password changed")
        else:
            print("No password was provided")
                  
            
        
            
        
        return redirect('dashboard_view', username=request.user.username)

    context = {
        'username': username,
        'account_data': user_field.usr_created_at,
        'profile_pic': user_field.profile_pic,
    }
    return render(request, 'dashboard.html', context)

    

    ...
@login_required
@require_POST
def post_reply(request:HttpRequest):
    
    try:
        data = json.loads(request.body) # get a dict from jsavasript
        post_id = data.get('post_id') # Get the key from frontend that is javascript. script.js will send
        reply_text = data.get('replyarea') # after that you'll do your logic
        
        # this will be used, change to post_id at <form > in html
        post = PostField.objects.get(id=post_id) # if u dont set primary_key=true in model djnaog automatically creates a id...so u use
       # post = PostField.objects.get(post_id=post_id)
        user_field = UserField.objects.get(user=request.user)
        reply = ReplyField.objects.create(post=post, user=user_field, reply_text=reply_text)

        
        # Use console log to check in javascript
        # opn console log in broweser to check 
        
        # Return to javscipt
        print(reply_text)
        print(request.user.username)
        return JsonResponse({'success': True, 'reply_text': reply_text, 'user': request.user.username, 'created_at': reply.created_at.strftime("%Y-%m-%d %H:%M:%S")})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
        
    # if request.method == 'POST' and request.user.is_authenticated and request.is_ajax:
    #     post_id = request.POST.get('post_id')
    #     reply_text = request.POST.get('reply_text')
        
    #     post = PostField.objects.get(id=post_id)
    #     reply = ReplyField.objects.create(post=post, user=request.user, reply_text=reply_text)
        
    #     return JsonResponse({'status':'sucess', 'reply_text':reply_text, 'username':request.user.username})
    # return JsonResponse({'status':'fail'})
    
@require_POST  # Enforce POST method for this view
def views_delete_reply(request: HttpRequest, post_id, reply_id):
    """View to delete a specific reply"""
    if request.user.is_authenticated:
        try:
            # Lookup API ref in django docs
            # syntax to perform lookups across foreign key relationships. It allows you to traverse models in relationships, such as many-to-one, one-to-one, or many-to-many relationships.
            # post is a ForeignKey pointing to the PostField model.
            """
            class ReplyField(models.Model):
            post = models.ForeignKey(PostField, on_delete=models.CASCADE)
            """
            """
            
            Hereee, this wont Work
                        reply = get_object_or_404(ReplyField, reply_id=reply_id, post__post_id=post_id) #This looks into the related PostField model, specifically at the post_id field of PostField. So, post__post_id=post_id means, "Get replies where the related PostField has the post_id field equal to post_id."
                beause reply_id is not primary key
                in models.py define it as 
                    reply_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
                    that is include primary_key=true
                    otherwise you ahve to use 
                    id=reply_id
                    where id is default primary key
            
            """
            reply = get_object_or_404(ReplyField, id=reply_id, post__post_id=post_id) #This looks into the related PostField model, specifically at the post_id field of PostField. So, post__post_id=post_id means, "Get replies where the related PostField has the post_id field equal to post_id."
            # Currently being managed from Django Admin interface
            if request.user.has_perm('backend.can_delete_reply') and request.user.username == reply.user.usrname or request.user.has_perm('backend.can_delete_any_reply'):
                reply.delete()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'Not authorized to delete this reply', 'reply_user': reply.user.usrname, 'current_usr':request.user.username})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'User not authenticated'})
    
@require_POST
@login_required
def views_delete_post(request: HttpRequest, post_id):
    try:
        post = get_object_or_404(PostField, post_id=post_id)
        # user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_field')
        """
        ---------------------------
        class UserField(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_field')
    .... other stuffs skiped
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
        
        
        
        
        
        
        The related_name allows you to access the UserField instance associated with a User instance. So, when you call request.user.user_field,
        you're accessing the UserField object that corresponds to the currently authenticated user.
        
        role:

        This is the field you've added to the UserField model that indicates the role of the user (e.g., 'user', 'moderator', 'admin').
        When you call request.user.user_field.role, you get the value of the role field for that specific user's UserField instance.
        
        user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_field')
        
        role checking - if request.user.user_field.role == 'admin'...
        
        assigning role

        def assign_permissions(user_field):
            if user_field.role == 'admin':
            # Assign all permissions
            user_field.user.user_permissions.set(Permission.objects.all())
            
            if user_field.role == 'moderator':
            # Assign specific permissions for moderators
            delete_any_post_permission = Permission.objects.get(codename='can_delete_any_post')
            user_field.user.user_permissions.add(delete_any_post_permission)
            
            
        when you create new user you can assign role to them
        def create_user(username, password, role):
        user = User.objects.create_user(username=username, password=password)
        user_field = UserField.objects.create(user=user, usrname=username, role=role)
        assign_permissions(user_field)  # Call to assign permissions based on role
        
        """
        if request.user.has_perm('backend.can_delete_post') and request.user.username == post.user.usrname or request.user.has_perm('backend.can_delete_any_post'):
            post.delete()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Not authorized to delete this post'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
            
        




