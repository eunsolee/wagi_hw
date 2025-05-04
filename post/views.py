from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Image
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def home(request):
    posts = Post.objects.all()
    return render(request, 'list.html', {'posts': posts})

def detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'detail.html', {'post': post})

@login_required
def write(request):
    if request.method == 'POST':
        post_form = PostForm(request.POST)
        images = request.FILES.getlist('images')

        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            post.save()

            for image in images:
                Image.objects.create(post=post, image=image)

            return redirect('home')
    else:
        post_form = PostForm()

    return render(request, 'write.html', {'post_form': post_form})

@login_required
def edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, 'edit.html', {'form': form})
