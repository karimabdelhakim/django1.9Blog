from django.shortcuts import render , get_object_or_404, redirect
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.contrib import messages
from urllib import quote_plus
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.db.models import Q
from .forms import PostForm
from .models import Post
def post_create(request):
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404	
	form = PostForm(request.POST or None,request.FILES or None)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.user = request.user
		instance.save()
		messages.success(request, "Successfuly Created")
		return HttpResponseRedirect(instance.get_absolute_url())
	#messages.error(request, "Not Successfuly Created")
	
	context ={"form": form,}
	return render(request,"post_form.html",context)

def post_detail(request,slug):
	instance = get_object_or_404(Post,slug=slug)
	if instance.draft or instance.publish > timezone.now().date():
		if not request.user.is_staff or not request.user.is_superuser:#if not admin
			raise Http404
	#you can use this to url-encode the post content
	#or use a custome filter(named urlify)in posts/templatetags 
	share_string = quote_plus(instance.content)
	context = {
	"title":instance.title,
	"instance":instance,
	"share_string":share_string
	}
	return render(request,"post_detail.html",context)

def post_list(request):
	today = timezone.now().date()
	queryset_list = Post.objects.active()#it is modified in models.py,so it doesn't get all posts
	if request.user.is_staff or request.user.is_superuser:#if admin
		queryset_list = Post.objects.all()
	query = request.GET.get('q')
	if query:
		queryset_list= queryset_list.filter(
			Q(title__icontains=query) |
			Q(content__icontains=query) |
			Q(user__first_name__icontains=query) |
			Q(user__last_name__icontains=query)
			).distinct()
	paginator = Paginator(queryset_list, 3) # Show 3 posts per page
	page_request_var = 'page'
	page = request.GET.get(page_request_var)
	try:
		queryset = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		queryset = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		queryset = paginator.page(paginator.num_pages)

	context = {
		"title":"list",
		"object_list" :queryset,
		"page_request_var":page_request_var,
		"today":today
	}
	return render(request,"post_list.html",context)


def post_update(request,slug):
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404
	instance = get_object_or_404(Post,slug=slug)
	form = PostForm(request.POST or None,request.FILES or None,instance=instance)
	if form.is_valid():#works while post method is applied on the form#not valid while get method
		instance = form.save(commit=False)
		instance.save()
		messages.success(request, "Successfuly Updated")
		return HttpResponseRedirect(instance.get_absolute_url())
	
	#messages.error(request, "Not Successfuly Updated")
	context = {
	"title":instance.title,
	"instance":instance,
	"form":form
	}
	return render(request,"post_form.html",context)
def post_delete(request,slug):
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404
	instance = get_object_or_404(Post,slug=slug)
	instance.delete()
	messages.success(request, "Post Deleted")
	return redirect('posts:list')