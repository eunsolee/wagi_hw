from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Image
from .forms import PostForm
from .forms import PostForm, CommentForm
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
    comments = post.comments.all().order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('detail', post_id=post.id)
    else:
        form = CommentForm()

    return render(request, 'detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })

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

@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
    else:
        post.likes.add(user)

    return redirect('detail', post_id=post.id)

def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    images = post.images.all()

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        files = request.FILES.getlist('image')

        # 삭제할 이미지 ID 리스트 받기
        delete_ids = request.POST.getlist('delete_images')

        if form.is_valid():
            form.save()

            # 기존 이미지 삭제
            for img_id in delete_ids:
                image = Image.objects.get(id=img_id)
                image.delete()

            # 새 이미지 추가
            for file in files:
                ext = file.name.split('.')[-1]
                filename = f"{uuid4().hex}.{ext}"
                save_path = os.path.join(settings.MEDIA_ROOT, 'post_images', filename)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)

                with open(save_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                Image.objects.create(post=post, image_path=f'post_images/{filename}')

            return redirect('detail', post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, 'edit.html', {'form': form, 'post': post, 'images': images})
