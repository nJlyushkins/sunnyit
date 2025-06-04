import json
import time
from datetime import timedelta

from background_task import background
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponse, request
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .forms import AuthForm, SignUpForm, GroupAdd, CodeAdd
from .models import Group, Bot, ConfirmCode, Payment
from .vk_module import VkServiceApi
from vk_api import VkApi
import logging

from .statistic_module import GroupStatistics

vk_service = VkServiceApi()

def index(request):
    if request.user.is_authenticated:
        return redirect('panel')
    return redirect('login')

def login(request):
    if request.user.is_authenticated:
        return redirect('panel')
    if request.method == 'POST':
        form = AuthForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request,user)
                return redirect('panel')
            else:
                print('No user')
                return render(request, 'main/login.html', {'form':form, 'user':request.user})
        else:
            return render(request, 'main/login.html', {'form': form, 'user':request.user})
    return render(request, 'main/login.html', {'form':AuthForm(), 'user':request.user})

def signup(request):
    if request.user.is_authenticated:
        return redirect('panel')
    if request.method == 'POST':
        form = SignUpForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                form.add_error('username','Пользователь уже существует!')
                return render(request, 'main/signup.html', {'form': form, 'user':request.user})
            else:
                _user = User(username=username, password=password,email=email)
                _user.save()
                auth.login(request,_user)
                return redirect('panel')
        else:
            print('Form errors: ' + str(form.errors))
            return render(request, 'main/signup.html', {'form': form, 'user':request.user})
    return render(request, 'main/signup.html', {'form':SignUpForm(), 'user':request.user})

def panel(request):
    if not request.user.is_authenticated:
        return redirect('index')
    groups = Group.objects.filter(owner=request.user.id)
    group_count = len(groups)
    group = None
    bots = None
    statistics = None
    if request.method == 'GET':
        logger = logging.getLogger("callback")
        try:
            action = request.GET['action']
            if(action == 'select-group'):
                group_id = request.GET['id']
                if(Group.objects.filter(id=group_id).exists()):
                    _group = Group.objects.filter(id=group_id)[0]
                    if(_group.owner == request.user):
                        group = _group
                        try:
                            _statistics = GroupStatistics(group.id)
                            statistics = _statistics
                        except Exception as e:
                            print(e)
                if(Bot.objects.filter(group_id=group).exists()):
                    bots = Bot.objects.filter(group_id=group)
        except Exception as e:
            logger.error("Error with getting group: "+str(e))
    data = {
        'user': request.user,
        'groups': groups,
        'group_count': group_count,
        'groupForm': GroupAdd(),
        'codeForm': CodeAdd(),
        'group': group,
        'statistics': statistics,
        'bots': bots
    }
    return render(request,'main/panel.html',data)

def logout(request):
    if not request.user.is_authenticated:
        return redirect('index')
    auth.logout(request)
    return redirect('index')

def groupAdd(request):
    if request.method == 'POST':
        res = {}
        try:
            group_id = request.POST['group_id']
            if(Group.objects.filter(group_id=group_id).exists()):
                res = {
                    'res': 'error',
                    'error': 'Группа уже существует!'
                }
            else:
                try:
                    resp = vk_service.groupGet(group_id)['response']
                    if('error' in resp):
                        res = {
                            'res': 'error',
                            'error': 'Что-то пошло не так',
                            'log': str(resp['error']['error_msg'])
                        }
                    else:
                        if(resp['groups'][0]['name'] == ''):
                            res['res'] = 'error'
                            res['error'] = 'Такой группы не существует'
                        else:
                            res['res'] = 'success'
                            res['group'] = resp['groups'][0]
                except Exception as e:
                    res = {
                        'res': 'error',
                        'error': 'Что-то пошло не так',
                        'log': str(e)
                    }
                    print('Group-api err:' + str(e))
        except Exception as e:
            res = {
                'res' : 'error',
                'error' : 'Введено неправильное значение!',
                'log': str(e)
            }
            print('Init err:' + str(e))
        return HttpResponse(json.dumps(res))
    return redirect('index')

def groupConfirm(request):
    if request.method == 'POST':
        try:
            group_id = request.POST['group_id']
            code = request.POST['code']
            token = request.POST['token']
            if(code != '' and group_id != ''):
                resp = vk_service.groupGet(group_id)['response']
                if (token != ''):
                    try:
                        session = VkApi(token=token)
                        api = session.get_api()
                        api.groups.getCallbackServers(group_id=group_id)
                        _token = token
                    except Exception as e:
                        print('Error with vk_api: ' + str(e))
                        res = {
                            'res': 'error',
                            'error': 'Неверный токен!',
                            'log' : str(e)
                        }
                        return HttpResponse(json.dumps(res))
                else:
                    _token = ''
                group = Group(group_id=group_id, owner=request.user,name=resp['groups'][0]['name'],token=_token)
                group.save()
                if(ConfirmCode.objects.filter(group_id=group).exists()):
                    _code = ConfirmCode.objects.get(group_id=group)
                    _code.code = code
                else:
                    _code = ConfirmCode(group_id=Group.objects.filter(group_id=group_id)[0], code=code)
                _code.save()
                try:
                    statistics = GroupStatistics(Group.objects.get(group_id=group_id).id,exist=False)
                except Exception as e:
                    print(e)
                res = {
                    'res' : 'success',
                    'group_id':group_id,
                }
            else:
                res = {
                    'res' : 'error',
                    'error' : 'Введено неправильное значение!'
                }
            return HttpResponse(json.dumps(res))
        except Exception as e:
            res = {
                'res' : 'error',
                'error' : 'Что-то пошло не так.',
                'log': str(e)
            }
            return HttpResponse(json.dumps(res))
    return redirect('index')

@csrf_exempt
def callback(request):
    logger = logging.getLogger("callback")
    logger.info(str(request))
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        logger.info(str(data))
        try:
            type = data['type']
            group_id = data['group_id']
        except Exception as e:
            logger.error('No type in data. ' + str(e))
            return HttpResponse('error')
        if Group.objects.filter(group_id=group_id).exists():
            group = Group.objects.filter(group_id=group_id)[0]
            try:
              groupStatistics = GroupStatistics(group.id)
            except Exception as e:
              logger.error('Error at group statistics: ' + str(e))
              return HttpResponse(e)
        else:
            logger.error('Error, no group')
            return HttpResponse('error')
        if(type == 'confirmation'):
            if(group.status != 1):
                if(ConfirmCode.objects.filter(group_id=group).exists()):
                    confirmCode = ConfirmCode.objects.filter(group_id=group)[0]
                    group.status = 1
                    group.save()
                    logger.info('Return confirmation code: ' + confirmCode.code)
                    return HttpResponse(str(confirmCode.code))
                else:
                  logger.info('No code for this group')
                  return HttpResponse('No code for this group')
            else:
              logger.info('Group is already confirmed')
              return HttpResponse('Group is already confirmed or waiting for confirm.')
        else:
            try:
                token = group.token
                api = VkApi(token=token).get_api()
            except Exception as e:
                api = None
                pass
            if(Bot.objects.filter(group_id=group).exists()):
                bot = Bot.objects.filter(group_id=group)[0]
                if(bot.running):
                    bot_dir = bot.lib
                    _lib = 'static.bots.' + bot_dir
                    try:
                        bot = __import__(_lib, globals=globals(), locals=locals(), fromlist=['Dispatcher'])
                    except Exception as e:
                        print('Error with import: ' + _lib)
                        logger.error('Error with import: ' + str(e))
                        return HttpResponse('error')
                    try:
                        disp = bot.Dispatcher(group.group_id,group.token)
                        res = disp.answer(data)
                        logger.info(res)
                    except Exception as e:
                        print('Error with dispatching: '+ str(e))
                        logger.error('Error with dispatching: ' + str(e))
                        return HttpResponse('ok')
            event_type = str(type).split('_')
            try:
              event_response = {
                'user_id': data['object']['liker_id']
              }
            except:
              try:
                  event_response = {
                      'user_id': data['object']['user_id']
                  }
              except:
                return HttpResponse('ok')
            if event_type[0] == 'message':
                pass
            if event_type[0] == 'photo':
                event_response['type'] = 'photo'
                try:
                    if event_type[1] == 'comment' and event_type[2] == 'new':
                        event_response['count'] = 1
                        try:
                            text = data['object']['text']
                            event_response['text'] = text
                        except:
                            pass
                        groupStatistics.logEvent(1,event_response)
                    elif event_type[1] == 'comment' and event_type[2] == 'delete':
                        event_response['count'] = 0
                        groupStatistics.logEvent(1,event_response)
                except:
                    pass
            if event_type[0] == 'wall':
                try:
                    event_response['type'] = 'wall'
                    if event_type[1] == 'reply' and event_type[2] == 'new':
                        event_response['count'] = 1
                        try:
                            text = data['object']['text']
                            event_response['text'] = text
                        except:
                            pass
                        groupStatistics.logEvent(1,event_response)
                    elif event_type[1] == 'reply' and event_type[2] == 'delete':
                        event_response['count'] = 0
                        groupStatistics.logEvent(1,event_response)
                except:
                    pass
            if event_type[0] == 'video':
                try:
                    event_response['type'] = 'video'
                    if event_type[1] == 'comment' and event_type[2] == 'new':
                        event_response['count'] = 1
                        try:
                            text = data['object']['text']
                            event_response['text'] = text
                        except:
                            pass
                        groupStatistics.logEvent(1,event_response)
                    elif event_type[1] == 'comment' and event_type[2] == 'delete':
                        event_response['count'] = 0
                        groupStatistics.logEvent(1,event_response)
                except:
                    pass
            if event_type[0] == 'like':
                try:
                    event_response['type'] = 'like'
                    if event_type[1] == 'add':
                        event_response['count'] = 1
                        groupStatistics.logEvent(1,event_response)
                    elif event_type[1] == 'remove':
                        event_response['count'] = 0
                        groupStatistics.logEvent(1,event_response)
                except:
                    pass
            if event_type[0] == 'group':
                try:
                    event_response['type'] = 'group'
                    if(api):
                        try:
                            total_subs = api.groups.getById(group_id=group_id,fields='members_count')[0]['members_count']
                        except Exception as e:
                            print('Error with subs: ' + str(e))
                    if event_type[1] == 'join':
                        event_response['count'] = 1
                        groupStatistics.logEvent(0,event_response,total=total_subs)
                    elif event_type[1] == 'leave':
                        event_response['count'] = -1
                        groupStatistics.logEvent(0,event_response,total=total_subs)
                except:
                    pass
        logger.info('Return OK response')
        return HttpResponse('ok')
    logger.info('Return index response')
    return redirect('index')