from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import JsonResponse

from .models import Pin, Board, Comment, CATEGORY_CHOICES
from .forms import RegisterForm, PinForm, BoardForm, CommentForm

PINS_PER_PAGE = 20


def _filtered_pins(request):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    pins = Pin.objects.select_related('owner').all()
    if query:
        pins = pins.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query))
    if category:
        pins = pins.filter(category=category)
    return pins, query, category


def home(request):
    if not request.user.is_authenticated:
        return render(request, 'pins/landing.html')

    pins, query, category = _filtered_pins(request)

    paginator = Paginator(pins, PINS_PER_PAGE)
    page_obj = paginator.get_page(1)

    saved_ids = set()
    if request.user.is_authenticated:
        saved_ids = set(request.user.saved_pins.values_list('pk', flat=True))

    return render(request, 'pins/home.html', {
        'pins': page_obj,
        'page_obj': page_obj,
        'query': query,
        'category': category,
        'categories': CATEGORY_CHOICES,
        'saved_ids': saved_ids,
        'total_pins': paginator.count,
        'has_next': page_obj.has_next(),
    })


def load_more_pins(request):
    """AJAX endpoint used for infinite scroll: returns the next page of pins
    as a rendered HTML fragment so the feed can keep growing as the user
    scrolls, the way the real Pinterest feed does."""
    pins, query, category = _filtered_pins(request)
    page_number = request.GET.get('page', 2)

    paginator = Paginator(pins, PINS_PER_PAGE)
    page_obj = paginator.get_page(page_number)

    saved_ids = set()
    if request.user.is_authenticated:
        saved_ids = set(request.user.saved_pins.values_list('pk', flat=True))

    html = render_to_string('pins/partials/pin_grid.html', {
        'pins': page_obj,
        'saved_ids': saved_ids,
    }, request=request)

    return JsonResponse({
        'html': html,
        'has_next': page_obj.has_next(),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
    })


def pin_detail(request, pk):
    pin = get_object_or_404(Pin, pk=pk)
    comments = pin.comments.select_related('author').all()
    comment_form = CommentForm()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.pin = pin
            comment.author = request.user
            comment.save()
            return redirect('pin_detail', pk=pin.pk)

    is_saved = request.user.is_authenticated and pin.saved_by.filter(pk=request.user.pk).exists()
    same_category = list(Pin.objects.filter(category=pin.category).exclude(pk=pin.pk).order_by('?')[:12])
    if len(same_category) < 12:
        extra = Pin.objects.exclude(pk=pin.pk).exclude(pk__in=[p.pk for p in same_category]).order_by('?')[:12 - len(same_category)]
        same_category += list(extra)
    related = same_category

    saved_ids = set()
    if request.user.is_authenticated:
        saved_ids = set(request.user.saved_pins.values_list('pk', flat=True))

    return render(request, 'pins/pin_detail.html', {
        'pin': pin, 'comments': comments, 'comment_form': comment_form,
        'is_saved': is_saved, 'related': related, 'saved_ids': saved_ids,
    })


@login_required
def pin_create(request):
    if request.method == 'POST':
        form = PinForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            pin = form.save(commit=False)
            pin.owner = request.user
            pin.save()
            messages.success(request, 'Pin created!')
            return redirect('pin_detail', pk=pin.pk)
    else:
        form = PinForm(user=request.user)
    return render(request, 'pins/pin_form.html', {'form': form})


@login_required
def pin_delete(request, pk):
    pin = get_object_or_404(Pin, pk=pk, owner=request.user)
    if request.method == 'POST':
        pin.delete()
        messages.success(request, 'Pin deleted.')
        return redirect('home')
    return render(request, 'pins/pin_confirm_delete.html', {'pin': pin})


@login_required
def pin_save_toggle(request, pk):
    pin = get_object_or_404(Pin, pk=pk)
    if pin.saved_by.filter(pk=request.user.pk).exists():
        pin.saved_by.remove(request.user)
    else:
        pin.saved_by.add(request.user)
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('pin_detail', pk=pin.pk)


@login_required
def board_list(request):
    boards = Board.objects.filter(owner=request.user)
    return render(request, 'pins/board_list.html', {'boards': boards})


@login_required
def board_create(request):
    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.owner = request.user
            board.save()
            return redirect('board_list')
    else:
        form = BoardForm()
    return render(request, 'pins/board_form.html', {'form': form})


def board_detail(request, pk):
    board = get_object_or_404(Board, pk=pk)
    pins = board.pins.all()
    saved_ids = set()
    if request.user.is_authenticated:
        saved_ids = set(request.user.saved_pins.values_list('pk', flat=True))
    return render(request, 'pins/board_detail.html', {'board': board, 'pins': pins, 'saved_ids': saved_ids})


@login_required
def saved_pins(request):
    pins = request.user.saved_pins.all()
    saved_ids = set(request.user.saved_pins.values_list('pk', flat=True))
    return render(request, 'pins/saved_pins.html', {'pins': pins, 'saved_ids': saved_ids})


def profile(request, username):
    from django.contrib.auth.models import User
    user = get_object_or_404(User, username=username)
    pins = user.pins.all()
    boards = user.boards.all()
    saved_ids = set()
    if request.user.is_authenticated:
        saved_ids = set(request.user.saved_pins.values_list('pk', flat=True))
    return render(request, 'pins/profile.html', {
        'profile_user': user, 'pins': pins, 'boards': boards, 'saved_ids': saved_ids,
    })


def explore(request):
    """Public teaser page for logged-out visitors: shows the category list
    without exposing the live pin feed, which is reserved for members."""
    return render(request, 'pins/explore.html', {'categories': CATEGORY_CHOICES})


def about(request):
    return render(request, 'pins/about.html')


def businesses(request):
    return render(request, 'pins/businesses.html')


def news(request):
    return render(request, 'pins/news.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to Pinterest!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})
