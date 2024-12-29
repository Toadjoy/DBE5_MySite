from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import Post
from django.views.generic import ListView
from django.core.paginator import Paginator,PageNotAnInteger, EmptyPage
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
# Create your views here.

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name='posts'
    paginate_by= 3
    template_name="blog/post/list.html"

def post_list(request):
    post_list = Post.published.all()
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        # Requested page is GT num pages, return last page
        posts = paginator.page(paginator.num_pages)
    return render(
        request,
        'blog/post/list.html',
        { 'posts':posts }
    )

def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )

    # Current list of active comments
    comments = post.comments.filter(active=True)
    # Form for users to comment
    form = CommentForm()


    return render(request,
                  'blog/post/detail.html',
                  {'post' : post,
                   'form': form,
                   'comments': comments,}
                )

def post_share(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )
    sent = False

    if (request.method == 'POST'):
        form = EmailPostForm(request.POST)
        if(form.is_valid()):
            #Form is valid
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = (f"{cd['name']} ({cd['email']}) "
                       f"recommends you read {post.title}"
                       )
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}\'s comments: {cd['comments']}"
            )
            send_mail(subject=subject,
                      message=message,
                      from_email=None,
                      recipient_list=[cd['to']]
                      )
            sent = True
    else:
        form = EmailPostForm()
    return render(request,
                  'blog/post/share.html', 
                  {
                    'post' : post,
                    'form': form,
                    'sent': sent
                    }
                )

@require_POST #Restricts this view to only be accessable by POST method
def post_comment(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )
    comment = None
    #A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        #Create a new comment object without saving it
        comment = form.save(commit=False)
        #Assign post to comment
        comment.post = post
        # Save the comment to the databse
        comment.save()
    return render(
        request,
        'blog/post/comment.html',
        {
            'post': post,
            'form': form,
            'comment':comment
        }
    )