from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest, JsonResponse
from .models import UserField, PostField, ReplyField
from django.contrib.auth.models import User
from django.contrib import auth
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import *
import json


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
        try:
            user_field = UserField.objects.get(user=request.user)
        except UserField.DoesNotExist:

            user_field = UserField.objects.create(
                user=request.user, usrname=request.user.username)

        context['user_field'] = user_field
        context['profile_pic'] = user_field.profile_pic.url if user_field.profile_pic else None
        context['posts'] = posts

    return render(request, 'index.html', context)


def login(request: HttpRequest):

    posts = PostField.objects.all().order_by('-created_at')
    context = {'posts': posts,
               'login_error': 'Username or password field is missing'}
    if request.method == 'POST':
        try:
            username = request.POST['username']
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

            else:
                return render(request, 'index.html', context)

    return render(request, 'index.html', context)


def register(request):
    posts = PostField.objects.all().order_by('-created_at')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        isAgreed = request.POST.get('acceptTerms') == 'on'

        if User.objects.filter(email=email).exists() or User.objects.filter(username=username).exists():
            return render(request, 'index.html', {'signup_error': 'Username or Email already exists', 'posts': posts})

        if not isAgreed:
            return render(request, 'index.html', {'signup_error': 'Please agree to the terms and conditions', 'posts': posts})

        user = User.objects.create_user(
            username=username, password=password, email=email)

        user_field = UserField.objects.create(
            user=user, usrname=username, has_agreed=isAgreed)
        user_field.save()

        user = authenticate(username=username, password=password)

        if user is not None:

            auth.login(request, user)
            return redirect('/')
        else:
            return render(request, 'index.html', {'login_error': 'Username or password is incorrect', 'posts': posts})

    return render(request, 'index.html', {'posts': posts})


def logout(request: HttpResponse):
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

            user_field = UserField.objects.filter(user=request.user).first()

            new_post = PostField.objects.create(
                user=user_field, post_title=title, description=description)
            new_post.save()

            return redirect('post', post_id=new_post.post_id)
        else:
            print(form.errors)
    else:
        form = PostForm()
    return render(request, 'Create_Post.html', {'form': form})


def post(request: HttpRequest, post_id):
    post = get_object_or_404(PostField, post_id=post_id)
    replies = post.replies.all().order_by('-created_at')

    paginator = Paginator(replies, 2)
    page = request.GET.get('page', 1)
    try:
        paginated_replies = paginator.page(page)
    except PageNotAnInteger:

        paginated_replies = paginator.page(1)
    except EmptyPage:

        paginated_replies = paginator.page(paginator.num_pages)
    context = {}
    if request.method == 'POST':
        reply_form = ReplyForm(request.POST)
        if reply_form.is_valid():
            reply_text = reply_form.cleaned_data['reply_text']
            user_field = UserField.objects.get(user=request.user)
            context['profile_pic'] = user_field.profile_pic.url if user_field.profile_pic else None
            ReplyField.objects.create(
                post=post, user=user_field, reply_text=reply_text).save()
            return redirect('post', post_id=post_id)
    else:
        reply_form = ReplyForm()
    context['post'] = post
    context['replies'] = paginated_replies
    context['reply_form'] = reply_form
    return render(request, 'Post.html', context)


@login_required
def dashboard_view(request: HttpRequest, username: str):

    user_field = get_object_or_404(UserField, user=request.user)
    if request.method == 'POST':

        profile_pic = request.FILES.get('profile_pic')
        if profile_pic:
            user_field.profile_pic = profile_pic
            user_field.save()

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

            get_usr.set_password(dashboard_passwd)
            get_usr.save()

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
    return render(request, 'Dashboard.html', context)

    ...


@login_required
@require_POST
def post_reply(request: HttpRequest):

    try:
        data = json.loads(request.body)

        post_id = data.get('post_id')
        reply_text = data.get('replyarea')

        post = PostField.objects.get(id=post_id)

        user_field = UserField.objects.get(user=request.user)
        reply = ReplyField.objects.create(
            post=post, user=user_field, reply_text=reply_text)

        return JsonResponse({'success': True, 'reply_text': reply_text, 'user': request.user.username, 'created_at': reply.created_at.strftime("%Y-%m-%d %H:%M:%S")})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_POST
def views_delete_reply(request: HttpRequest, post_id, reply_id):
    """View to delete a specific reply"""
    if request.user.is_authenticated:
        try:
            reply = get_object_or_404(

                ReplyField, id=reply_id, post__post_id=post_id)

            if request.user.has_perm('backend.can_delete_reply') and request.user.username == reply.user.usrname or request.user.has_perm('backend.can_delete_any_reply'):
                reply.delete()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'Not authorized to delete this reply', 'reply_user': reply.user.usrname, 'current_usr': request.user.username})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'User not authenticated'})


@require_POST
@login_required
def views_delete_post(request: HttpRequest, post_id):
    try:
        post = get_object_or_404(PostField, post_id=post_id)
        if request.user.has_perm('backend.can_delete_post') and request.user.username == post.user.usrname or request.user.has_perm('backend.can_delete_any_post'):
            post.delete()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Not authorized to delete this post'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


def _search_post(request: HttpRequest):
    query = request.GET.get('query', '')
    if query:

        retrieved_post = PostField.objects.filter(post_title__icontains=query)
    else:
        retrieved_post = PostField.objects.none()

    results = [{'id': post.id, 'title': post.title} for post in retrieved_post]
    return JsonResponse(results, safe=False)
