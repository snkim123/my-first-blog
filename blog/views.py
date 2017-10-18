from django.shortcuts import render, render_to_response, get_object_or_404
from django.utils import timezone
from .models import Post, Comment

from django.contrib.auth.decorators import login_required

from .pagingHelper import pagingHelper



# Create your views here.

rows_per_page = 3

def post_list(request):
    #posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    #posts = Post.objects.all()
    posts = Post.objects.order_by('-id')[0:rows_per_page]


    current_page = 1
    total_cnt = Post.objects.all().count()

    #helper class for paging
    pagingHelperIns = pagingHelper()
    total_page_list = pagingHelperIns.getTotalPageList(total_cnt, rows_per_page)
    print('total page list : ', total_page_list)


    return render(request, 'blog/post_list.html',
                  {'posts':posts, 'total_cnt': total_cnt, 'current_page':current_page, 'total_page_list': total_page_list})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    print(pk)
    return render(request, 'blog/post_detail.html', {'post': post})


from .forms import PostForm, CommentForm
from django.shortcuts import redirect

@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            #post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
        return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            #post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)

    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})


@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts':posts})

@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)

@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('post_list')



#===========================================================================================
def post_list_specific_page(request):
    current_page = request.GET['current_page']
    total_cnt = Post.objects.all().count()

    print ('specific current_page=', current_page)

    # 페이지를 가지고 범위 데이터를 조회한다 => raw SQL 사용함
    #posts = Post.objects.raw('SELECT Z.* FROM(SELECT X.*, ceil( rownum / %s ) as page FROM ( SELECT ID,SUBJECT,NAME, CREATED_DATE, MAIL,MEMO,HITS \
    #                                    FROM POST  ORDER BY ID DESC ) X ) Z WHERE page = %s', [rows_per_page, current_page])

    #"UPDATE Cars SET Price=? WHERE Id=?", (uPrice, uId)
    start = (int(current_page)-1) * int(rows_per_page)
    qry = 'SELECT * FROM BLOG_POST  ORDER BY ID DESC  LIMIT ' + str(start) + ', ' + str(rows_per_page)
    print(qry)
    #posts = Post.objects.raw('SELECT * FROM BLOG_POST  ORDER BY ID DESC  LIMIT ? , ?', (current_page * rows_per_page, rows_per_page) )
    posts = Post.objects.raw(qry )

    print('boardList=',posts, 'count()=', total_cnt)

    # 전체 페이지를 구해서 전달...
    pagingHelperIns = pagingHelper();

    total_page_list = pagingHelperIns.getTotalPageList( total_cnt, rows_per_page)

    print('totalPageList', total_page_list)

    #return render_to_response('blog/post_list.html', {'posts': posts, 'totalCnt': total_cnt,
    #                                                    'current_page':int(current_page) ,'totalPageList':total_page_list} )
    return render(request, 'blog/post_list.html',
                  {'posts':posts, 'total_cnt': total_cnt, 'current_page':int(current_page), 'total_page_list': total_page_list})

#===========================================================================================











def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()

    return render(request, 'blog/add_comment_to_post.html', {'form': form})



@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail', pk=post_pk)





