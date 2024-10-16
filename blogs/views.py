from django.shortcuts import render,redirect
from .forms import BlogForm,PostForm

# Create your views here.
from .models import blog_name,blog_post
from django.contrib.auth.decorators import login_required
from django.http import Http404

def home(request):
    return render(request,"blogs/home.html")

@login_required # TO make it work add login_url in settings
# @ can help only authentic users to browse data. but authentic users can browse other users data too.
def all_blogs(request):
    """Show all blogs."""
    name=blog_name.objects.filter(user=request.user) # left user is a foreign key.
    #tells Django to retrieve only the blog objects from the database whose user attribute matches the current user. We just add the ownership of data to each user. Protecting it is still left.
    context={'blog_names':name}
    return render(request,'blogs/blogs.html',context)

@login_required
def blog(request,blog_id):
    """Show posts of clicked blog"""
    name=blog_name.objects.get(id=blog_id)
    
    #Make sure the blogs belongs to current user.
    # if name.user != request.user: # Means if blog_name is not owned by current user.
    #     raise Http404
    check_blog_owner(request,name)
    
    
    post=blog_post.objects.filter(f_key=name)
    context={'blog_name':name,'post_name':post}
    return render(request,'blogs/blog.html',context)

@login_required
def posts(request):
    name=blog_name.objects.all()
    p_name=blog_post.objects.filter(f_key__in=name)
    #The __in lookup allows you to filter against multiple values. So, when you write f_key__in=name, you're telling Django: "Find all blog_post objects where f_key (the foreign key to blog_name) matches any of the blog_name objects in the QuerySet name."Essentially, it retrieves all blog posts that belong to any of the blog names in the database.
    context={'blog_name':name,'post_name':p_name}
    return render(request,'blogs/posts.html',context)

@login_required
def new_blogs(request):
    """New blogs add"""
    #After the creation of forms under forms.py
    if request.method != 'POST':
        form=BlogForm()
    else:
        form=BlogForm(data=request.POST)
    if form.is_valid():
        
        new_blog=form.save(commit=False)
        new_blog.user=request.user #We set the new blog's user attribute to the current user. 
        new_blog.save()
        
        
        
        # form.save()
        return redirect('blogs:all_blogs')
    context={'form':form}
    return render(request,'blogs/new_blogs.html',context)

@login_required
def new_posts(request,blog_id):
    """New post(s) add"""
    #After the creation of forms under forms.py
    
    blog = blog_name.objects.get(id=blog_id)
    if request.method != 'POST':
        form=PostForm()
    else:
        form=PostForm(data=request.POST)
    if form.is_valid():
        post = form.save(commit=False)  # Create post instance without saving to the database
        post.f_key = blog  # Set the foreign key to the blog instance
        post.save()  # Now save the post to the database
        return redirect('blogs:blogs',blog_id) 
    # or you can "return redirect('blogs:new_posts',blog_id)"
    context={'form':form,'blog_name': blog}
    return render(request,'blogs/new_posts.html',context)

@login_required
def edit_posts(request, post_id):
    
    """Edit an existing entry."""
    post = blog_post.objects.get(id=post_id)
    f_key = post.f_key #it gives the 'blog_name' instance that the post is linked to.
    # the left f_key is now a blog object instance. We could name it anything. 
    
    
    # if f_key.user != request.user: #f_key.user literally means blog.user. We check whether the user/owner of the blog matches the currently logged-in user.
    #     raise Http404
    
    check_blog_owner(request,f_key)
    
    
    if request.method != 'POST':
        # Initial request; pre-fill form with the current entry.
        form = PostForm(instance=post)
    else:
        # POST data submitted; process data.
        form = PostForm(instance=post, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('blogs:blogs', f_key.id)
    context = {'post': post, 'blog': f_key, 'form': form}
    return render(request, 'blogs/edit_posts.html', context)

def check_blog_owner(request,article):
    if article.user != request.user:
        raise Http404
    