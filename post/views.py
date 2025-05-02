from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Image
from .forms import PostForm, ImageForm
from django.forms import modelformset_factory
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
def home(request):
    posts = Post.objects.all()
    return render(request, 'list.html', {'posts': posts})

def detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'detail.html', {'post': post})

@login_required
def write(request):
    ImageFormSet = modelformset_factory(Image, form=ImageForm, extra=3)  # 3개 파일 기본 제공

    if request.method == 'POST':
        post_form = PostForm(request.POST)
        formset = ImageFormSet(request.POST, request.FILES, queryset=Image.objects.none())

        if post_form.is_valid() and formset.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            post = post_form.save()

            for form in formset.cleaned_data:
                if form:
                    image = form['image']
                    Image.objects.create(post=post, image=image)

            return redirect('home')
    else:
        post_form = PostForm()
        formset = ImageFormSet(queryset=Image.objects.none())

    return render(request, 'write.html', {
        'post_form': post_form,
        'formset': formset,
    })

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
