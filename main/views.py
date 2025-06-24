import logging
import os

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import subprocess
import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from .forms import CustomAuthenticationForm, CustomUserCreationForm
from .models import UserBalance, CustomUser, VKGroup, ChatBot, ConfirmCode, GroupStatistics, BotStatistics
from .models import Messages, Media, States
from .forms import MessageForm
from .utils import process_vk_event
from .vk_api import VkServiceApi, VkTokenValidator
import json
from django.utils import timezone
from datetime import timedelta
import uuid
import random
import string

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'main/home.html')

def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('main:dashboard')
    else:
        form = CustomAuthenticationForm()
    register_form = CustomUserCreationForm()
    return render(request, 'main/auth.html', {'login_form': form, 'register_form': register_form})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserBalance.objects.create(user=user)
            login(request, user)
            return redirect('main:dashboard')
    else:
        form = CustomUserCreationForm()
    login_form = CustomAuthenticationForm()
    return render(request, 'main/auth.html', {'login_form': login_form, 'register_form': form})

@login_required
def dashboard(request):
    user = request.user
    balance = UserBalance.objects.get(user=user)
    groups = VKGroup.objects.filter(owner=user)
    bots = ChatBot.objects.filter(vk_group__owner=user)

    # Данные для графиков (последние 7 дней)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=7)

    # Статистика групп
    group_stats_data = {}
    for group in groups:
        stats = GroupStatistics.objects.filter(
            vk_group=group,
            date__range=[start_date, end_date]
        ).order_by('date')
        group_stats_data[group.id] = {
            'dates': [stat.date.strftime('%Y-%m-%d') for stat in stats],
            'likes': [stat.likes for stat in stats],
            'messages': [stat.messages for stat in stats],
            'subscribers': stats.last().subscribers if stats.exists() else 0,
            'activity_score': stats.last().activity_score if stats.exists() else 0
        }

    # Статистика ботов
    bot_stats_data = {}
    for bot in bots:
        stats = BotStatistics.objects.filter(
            chat_bot=bot,
            date__range=[start_date, end_date]
        ).order_by('date')
        bot_stats_data[bot.id] = {
            'dates': [stat.date.strftime('%Y-%m-%d') for stat in stats],
            'interactions': [stat.interactions for stat in stats],
            'messages_processed': stats.last().messages_processed if stats.exists() else 0,
            'active_users': stats.last().active_users if stats.exists() else []
        }

    # Преобразование QuerySet в сериализуемый формат
    groups_data = [
        {
            'id': g.id,
            'group_id': g.group_id,
            'name': g.name or f"Группа {g.group_id}",
            'verification_status': g.verification_status
        } for g in groups
    ]
    bots_data = [{'id': b.id, 'vk_group_id': b.vk_group_id, 'name': b.name, 'status': b.status} for b in bots]

    context = {
        'balance': balance,
        'groups': groups,
        'bots': bots,
        'group_stats_data': group_stats_data,
        'bot_stats_data': bot_stats_data,
        'groups_data': groups_data,
        'bots_data': bots_data,
    }
    return render(request, 'main/dashboard.html', context)

# В файле main/views.py
import subprocess
import json
import os
import logging
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from .models import ChatBot

logger = logging.getLogger(__name__)

# В файле main/views.py
import subprocess
import json
import os
import logging
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from .models import ChatBot

logger = logging.getLogger(__name__)

@require_GET
@login_required
def get_bot_data(request, bot_id):
    bot = ChatBot.objects.get(id=bot_id, vk_group__owner=request.user)
    bot_path = bot.library_path.rstrip(os.sep)  # Удаляем лишний слеш в конце
    bot_file = os.path.normpath(os.path.join(bot_path, 'bot.py'))  # Нормализуем путь

    # Отладочная информация
    logger.debug(f"Bot path: {bot_path}")
    logger.debug(f"Bot file: {bot_file}")

    if not os.path.exists(bot_file):
        logger.error(f"Bot file not found at: {bot_file}")
        return JsonResponse({'success': False, 'error': f'Bot file not found at: {bot_file}'}, status=400)

    action = request.GET.get('action')  # 'get_users', 'get_states', 'get_messages'

    try:
        result = subprocess.run(
            ['python', bot_file, action],
            capture_output=True,
            text=True,
            check=True,
            cwd=bot_path  # Указываем рабочую директорию
        )
        output = result.stdout.strip()
        if not output:
            return JsonResponse({'success': False, 'error': 'Empty response from bot.py'}, status=500)
        data = json.loads(output)
        return JsonResponse({'success': True, 'data': data})
    except subprocess.CalledProcessError as e:
        logger.error(f"Subprocess error for bot {bot_id}: {e.stderr}")
        return JsonResponse({'success': False, 'error': f'Bot execution failed: {e.stderr}'}, status=500)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error for bot {bot_id}: {output} - {str(e)}")
        return JsonResponse({'success': False, 'error': f'Invalid JSON from bot.py: {str(e)}'}, status=500)
    except Exception as e:
        logger.error(f"Unexpected error for bot {bot_id}: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def connect_group_ajax(request):
    vk_service = VkServiceApi()
    vk_validator = VkTokenValidator()

    if request.method == 'POST':
        step = request.POST.get('step')

        if step == '1':
            group_id = request.POST.get('group_id')
            group_data = vk_service.groupGet(group_id)
            if not group_data or 'error' in group_data:
                return JsonResponse({'error': 'Не удалось получить данные о группе'}, status=400)
            group_info = group_data['response']['groups'][0]
            return JsonResponse({
                'group_id': group_info['id'],
                'name': group_info['name'],
                'screen_name': group_info['screen_name'],
                'photo_100': group_info['photo_100']
            })

        elif step == '2':
            group_id = request.POST.get('group_id')
            access_token = request.POST.get('access_token')

            is_valid, message = vk_validator.validate_token(group_id, access_token)
            if not is_valid:
                return JsonResponse({'error': message}, status=400)

            if VKGroup.objects.filter(group_id=group_id).exists():
                return JsonResponse({'error': 'Группа уже подключена'}, status=400)

            group_data = vk_service.groupGet(group_id)
            if not group_data or 'error' in group_data:
                return JsonResponse({'error': 'Не удалось получить данные о группе'}, status=400)
            group_info = group_data['response']['groups'][0]

            vk_group = VKGroup.objects.create(
                group_id=group_id,
                name=group_info['name'],
                owner=request.user,
                access_token=access_token,
                verification_status='Ожидает'
            )

            confirm_code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
            ConfirmCode.objects.create(vk_group=vk_group, code=confirm_code)

            callback_url = request.build_absolute_uri('https://sunnyit.online/vk-callback')
            callback_response = vk_service.addCallbackServer(
                group_id=group_id,
                access_token=access_token,
                url=callback_url,
                title=f"SunnyBots",
                secret_key=confirm_code
            )

            if not callback_response or 'error' in callback_response:
                logging.log(logging.ERROR, callback_response)
                return JsonResponse({
                    'manual_setup_required': True,
                    'group_id': group_id,
                    'callback_url': callback_url,
                    'secret_key': confirm_code,
                    'access_token': access_token,
                    'error': callback_response
                })

            vk_group.verification_status = 'Успешно'
            vk_group.save()

            return JsonResponse({'success': 'Группа успешно подключена!'})

        elif step == '3':
            group_id = request.POST.get('group_id')
            access_token = request.POST.get('access_token')
            secret_key = request.POST.get('secret_key')
            confirmation_code = request.POST.get('confirmation_code')

            if not confirmation_code:
                return JsonResponse({'error': 'Пожалуйста, укажите код подтверждения'}, status=400)

            confirmation_response = vk_service.getCallbackConfirmationCode(
                group_id=group_id,
                access_token=access_token
            )

            if not confirmation_response or 'error' in confirmation_response:
                return JsonResponse({'error': 'Не удалось получить код подтверждения от VK'}, status=400)

            expected_code = confirmation_response.get('response', {}).get('code')
            if confirmation_code != expected_code:
                return JsonResponse({'error': 'Неверный код подтверждения'}, status=400)

            try:
                vk_group = VKGroup.objects.get(group_id=group_id, owner=request.user)
                vk_group.verification_status = 'Успешно'
                vk_group.save()
                return JsonResponse({'success': 'Группа успешно подключена!'})
            except VKGroup.DoesNotExist:
                return JsonResponse({'error': 'Группа не найдена'}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def edit_messages(request, bot_id):
    bot = get_object_or_404(ChatBot, id=bot_id, vk_group__owner=request.user)
    bot_path = bot.library_path.rstrip(os.sep)
    bot_file = os.path.normpath(os.path.join(bot_path, 'bot.py'))

    if not os.path.exists(bot_file):
        logger.error(f"Bot file not found at: {bot_file}")
        return render(request, 'main/edit_messages.html', {'error': 'Bot file not found', 'bot': bot, 'bot_id': bot_id})

    # Получаем сообщения
    try:
        result_messages = subprocess.run(
            ['python', bot_file, 'get_messages'],
            capture_output=True,
            text=True,
            check=True,
            cwd=bot_path
        )
        messages = json.loads(result_messages.stdout.strip()) if result_messages.stdout.strip() else []
    except subprocess.CalledProcessError as e:
        logger.error(f"Subprocess error for bot {bot_id} (get_messages): {e.stderr}")
        messages = []
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error for bot {bot_id} (get_messages): {e}")
        messages = []

    # Получаем состояния
    try:
        result_states = subprocess.run(
            ['python', bot_file, 'get_states'],
            capture_output=True,
            text=True,
            check=True,
            cwd=bot_path
        )
        states = json.loads(result_states.stdout.strip()) if result_states.stdout.strip() else []
    except subprocess.CalledProcessError as e:
        logger.error(f"Subprocess error for bot {bot_id} (get_states): {e.stderr}")
        states = []
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error for bot {bot_id} (get_states): {e}")
        states = []

    return render(request, 'main/edit_messages.html', {'messages': messages, 'states': states, 'bot': bot, 'bot_id': bot_id})

@require_GET
@login_required
def get_message(request, message_id):
    bot_id = request.GET.get('bot_id')
    bot = get_object_or_404(ChatBot, id=bot_id, vk_group__owner=request.user)
    bot_path = bot.library_path.rstrip(os.sep)
    bot_file = os.path.normpath(os.path.join(bot_path, 'bot.py'))

    if not os.path.exists(bot_file):
        return JsonResponse({'success': False, 'error': 'Bot file not found'}, status=400)

    try:
        result = subprocess.run(
            ['python', bot_file, 'get_message_by_id', str(message_id)],
            capture_output=True,
            text=True,
            check=True,
            cwd=bot_path
        )
        output = result.stdout.strip()
        if not output:
            return JsonResponse({'success': False, 'error': 'Empty response from bot.py'}, status=500)
        data = json.loads(output)
        if not data.get('success'):
            return JsonResponse({'success': False, 'error': data.get('error')}, status=400)
        return JsonResponse(data)
    except subprocess.CalledProcessError as e:
        logger.error(f"Subprocess error for bot {bot_id}: {e.stderr}")
        return JsonResponse({'success': False, 'error': f'Bot execution failed: {e.stderr}'}, status=500)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error for bot {bot_id}: {output} - {str(e)}")
        return JsonResponse({'success': False, 'error': f'Invalid JSON from bot.py: {str(e)}'}, status=500)

def update_message(request, message_id):
    bot_id = request.POST.get('bot_id')
    bot = get_object_or_404(ChatBot, id=bot_id, vk_group__owner=request.user)
    bot_path = bot.library_path.rstrip(os.sep)
    bot_file = os.path.normpath(os.path.join(bot_path, 'bot.py'))

    if not os.path.exists(bot_file):
        return JsonResponse({'success': False, 'error': 'Bot file not found'}, status=400)

    if request.method == 'POST':
        text = request.POST.get('text')
        state_id = request.POST.get('state_id')
        media_urls = [request.POST.get(f'media_url_{i}') for i in range(5)]
        try:
            result = subprocess.run(
                ['python', bot_file, 'update_message', str(message_id), text, str(state_id)] + [url for url in media_urls if url],
                capture_output=True,
                text=True,
                check=True,
                cwd=bot_path
            )
            output = json.loads(result.stdout.strip())
            return JsonResponse(output)
        except subprocess.CalledProcessError as e:
            logger.error(f"Subprocess error for bot {bot_id}: {e.stderr}")
            return JsonResponse({'success': False, 'error': f'Bot execution failed: {e.stderr}'}, status=500)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for bot {bot_id}: {output} - {str(e)}")
            return JsonResponse({'success': False, 'error': f'Invalid JSON from bot.py: {str(e)}'}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

def add_message(request, bot_id):
    bot = get_object_or_404(ChatBot, id=bot_id, vk_group__owner=request.user)
    bot_path = bot.library_path.rstrip(os.sep)
    bot_file = os.path.normpath(os.path.join(bot_path, 'bot.py'))

    if not os.path.exists(bot_file):
        return JsonResponse({'success': False, 'error': 'Bot file not found'}, status=400)

    if request.method == 'POST':
        text = request.POST.get('text')
        state_id = request.POST.get('state_id')
        media_urls = [request.POST.get(f'media_url_{i}') for i in range(5)]
        try:
            result = subprocess.run(
                ['python', bot_file, 'add_message', text, str(state_id)] + [url for url in media_urls if url],
                capture_output=True,
                text=True,
                check=True,
                cwd=bot_path
            )
            output = json.loads(result.stdout.strip())
            return JsonResponse(output)
        except subprocess.CalledProcessError as e:
            logger.error(f"Subprocess error for bot {bot_id}: {e.stderr}")
            return JsonResponse({'success': False, 'error': f'Bot execution failed: {e.stderr}'}, status=500)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for bot {bot_id}: {output} - {str(e)}")
            return JsonResponse({'success': False, 'error': f'Invalid JSON from bot.py: {str(e)}'}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
def check_callback_server(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        try:
            vk_group = VKGroup.objects.get(group_id=group_id, owner=request.user)
        except VKGroup.DoesNotExist:
            return JsonResponse({'error': 'Группа не найдена'}, status=400)

        vk_service = VkServiceApi()
        response = vk_service.getCallbackServers(
            group_id=group_id,
            access_token=vk_group.access_token
        )

        if not response or 'error' in response:
            return JsonResponse({'error': 'Не удалось получить список серверов'}, status=400)

        servers = response.get('response', {}).get('items', [])
        target_url = 'sunnyit.online'
        for server in servers:
            if target_url in server.get('url', ''):
                status = server.get('status')
                if status == 'failed':
                    vk_group.verification_status = 'Ошибка'
                elif status == 'ok':
                    vk_group.verification_status = 'Успешно'
                else:
                    vk_group.verification_status = 'Ожидает'
                vk_group.save()
                return JsonResponse({'status': status, 'group_status': vk_group.verification_status})

        return JsonResponse({'error': 'Сервер с указанным URL не найден'}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def toggle_bot_status(request):
    if request.method == 'POST':
        bot_id = request.POST.get('bot_id')
        new_status = request.POST.get('status')
        try:
            bot = ChatBot.objects.get(id=bot_id, vk_group__owner=request.user)
            bot.status = new_status
            bot.save()
            return JsonResponse({'success': True})
        except ChatBot.DoesNotExist:
            return JsonResponse({'error': 'Бот не найден'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def profile(request):
    pass

def faq(request):
    pass

@login_required
def payment(request):
    pass

@login_required
def order_bot(request):
    pass

@csrf_exempt
def vk_callback(request):
    if request.method == "POST":
        data = json.loads(request.body)
        group_id = data.get("group_id")
        event_type = data.get("type")
        event_id = data.get("event_id")
        object_data = data.get("object", {})

        try:
            vk_group = VKGroup.objects.get(group_id=group_id)
        except VKGroup.DoesNotExist:
            return HttpResponse("ok")

        if event_type == "confirmation":
            confirm_code = ConfirmCode.objects.filter(vk_group=vk_group).order_by('-date').first()
            if confirm_code:
                vk_group.verification_status = "Успешно"
                vk_group.save()
                return HttpResponse(confirm_code.code)
            vk_group.verification_status = "Ошибка"
            vk_group.save()
            return HttpResponse("ok")

        today = timezone.now().date()
        group_stats, created = GroupStatistics.objects.get_or_create(
            vk_group=vk_group,
            date__date=today,
            defaults={'date': timezone.now()}
        )
        if event_type in ["group_join", "user_block", "user_unblock", "group_change_settings", "group_officers_edit", "group_change_photo"]:
            group_stats.activity_score += 1
        elif event_type == "group_leave":
            group_stats.subscribers = max(0, group_stats.subscribers - 1)
            group_stats.activity_score += 1
        elif event_type == "message_new" or event_type == "message_reply" or event_type == "message_edit":
            group_stats.messages += 1
            group_stats.activity_score += 1
        elif event_type == "like_add" or event_type == "wall_post_new" or event_type == "wall_repost":
            group_stats.likes += 1
            group_stats.activity_score += 1
        elif event_type in ["photo_new", "video_new", "board_post_new", "market_comment_new"]:
            group_stats.activity_score += 1
        group_stats.save()

        bots = ChatBot.objects.filter(vk_group=vk_group)
        for bot in bots:
            bot_stats, created = BotStatistics.objects.get_or_create(
                chat_bot=bot,
                date__date=today,
                defaults={'date': timezone.now()}
            )
            if event_type in ["message_new", "message_reply", "message_edit", "group_leave", "group_join"]:
                bot_stats.messages_processed += 1
                bot_stats.interactions += 1
                user_id = None
                if event_type in ["message_new", "message_reply", "message_edit"]:
                    user_id = object_data.get("message", {}).get("from_id")
                elif event_type in ["group_join", "group_leave"]:
                    user_id = object_data.get("user_id")
                if user_id:
                    active_users = bot_stats.active_users
                    if event_type == "group_leave":
                        active_users = [u for u in active_users if u.get("user_id") != user_id]
                    elif event_type == "group_join":
                        active_users.append({"user_id": user_id, "state": "new"})
                    elif event_type in ["message_new", "message_reply", "message_edit"]:
                        active_users = [{"user_id": user_id, "state": "active"} if u.get("user_id") == user_id else u for u in active_users]
                        if not any(u.get("user_id") == user_id for u in active_users):
                            active_users.append({"user_id": user_id, "state": "active"})
                    bot_stats.active_users = active_users
            bot_stats.save()

            process_vk_event(bot.library_path, data)

        return HttpResponse("ok")
    return HttpResponse("ok")

def edit_bot(request):
    pass