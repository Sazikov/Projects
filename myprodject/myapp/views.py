from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import *
from .models import *


def index(request):
    title = 'Заполнение анкеты'
    initial = {'user_surname': '', 'user_name': '', 'user_name2': '', 'date_birth': '1970-01-01', 'comment': ''}
    admin_url = reverse('admin:index')
    login_url = reverse('login')
    logout_url = reverse('logout')
    if request.user.is_staff:
        info_table_url = reverse('info_table')
    else:
        info_table_url = ''

    if request.method == 'POST':
        my_form = EditUserForm(request.POST, initial=initial)
        if my_form.is_valid():
            cd = my_form.cleaned_data
            try:
                UsersInfo.objects.create(user_surname=cd['user_surname'], user_name=cd['user_name'],
                                         user_name2=cd['user_name2'], date_birth=cd['date_birth'], comment=cd['comment'])
            except Exception as er:
                return HttpResponse("Данные не сохранены!")
        else:
            return HttpResponse("Данные не сохранены!")

        return HttpResponse("Данные сохранены!")

    else:
        my_form = EditUserForm(initial=initial)
        return render(request, 'main.html', {'form': my_form, 'title': title, 'login_url': login_url,
                                             'info_table_url': info_table_url, 'admin_url': admin_url, 'logout_url': logout_url})


def login_user(request):

    if request.method == 'POST':

        my_form = LoginUserForm(request.POST)

        if my_form.is_valid():
            cd = my_form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user and user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('home'))

        return HttpResponseRedirect(reverse('login'))
    else:
        my_form = LoginUserForm()
        return render(request, 'login.html', {'form': my_form})


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))


@login_required
def info_table(request):
    users_all = UsersInfo.objects.all()
    users_info_table = []
    for line in users_all:
        full_name = line.user_surname + ' ' + line.user_name + ' ' + line.user_name2
        users_info_table.append([reverse('info_edit', args=(line.id,)), full_name, line.date_birth.strftime("%d-%m-%Y")])

    return render(request, 'info_table.html', {'users_info_table': users_info_table})


@login_required
def info_edit(request, cat_id):
    try:
        ank = UsersInfo.objects.get(id=cat_id)

        if request.method == 'POST':
            UsersInfo.objects.filter(id=cat_id).delete()
            return HttpResponse("Анкета удалена!")

        else:
            return render(request, 'info_edit.html', {'nom_ank': ank.id, 'user_surname': ank.user_surname,
                                                      'user_name': ank.user_name, 'user_name2': ank.user_name2,
                                                      'date_birth': ank.date_birth, 'comment': ank.comment})
    except:
        return HttpResponse("Анкета не найдена!")
