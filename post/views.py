from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Image
from .forms import PostForm
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q

def home(request):
    query = request.GET.get('q', '').strip()
    option = request.GET.get('option', 'all')

    if query:
        words = [word for word in query.replace(',', ' ').split() if word]

        q_object = Q()
        for word in words:
            if option == 'title':
                q_object |= Q(title__icontains=word)
            elif option == 'content':
                q_object |= Q(body__icontains=word)
            else:
                q_object |= Q(title__icontains=word) | Q(body__icontains=word)

        posts = Post.objects.filter(q_object).order_by('-created_at')
    else:
        posts = Post.objects.all().order_by('-created_at')

    return render(request, 'list.html', {
        'posts': posts,
        'query': query,
        'option': option
    })

def detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post:detail', post_id=post.id)
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

            return redirect('post:home')
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
            return redirect('post:detail', post_id=post.id)
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

    return redirect('post:detail', post_id=post.id)

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
                try:
                    image = Image.objects.get(id=img_id)
                    image.delete()
                except Image.DoesNotExist:
                    pass

            images = request.FILES.getlist('new_image')

            for image in images:
                Image.objects.create(post=post, image=image)

            return redirect('post:detail', post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, 'edit.html', {'form': form, 'post': post, 'images': images})
