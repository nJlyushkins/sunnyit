# В файле main/utils.py
import importlib.util
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_vk_event(library_path, event_data):
    try:
        # Формируем полный путь к bot.py с учетом платформы
        bot_path = os.path.join(library_path, 'bot.py')
        if not os.path.exists(bot_path):
            raise FileNotFoundError(f"Bot file not found at: {bot_path}")

        # Динамическая загрузка модуля бота
        spec = importlib.util.spec_from_file_location("bot_module", bot_path)
        bot_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bot_module)

        # Проверка наличия метода handle_event
        if not hasattr(bot_module, 'handle_event'):
            raise AttributeError(f"Module {bot_path} has no handle_event method")

        # Вызов метода обработки события
        bot_module.handle_event(event_data)
        return {'success': True, 'message': 'Event processed successfully'}

    except Exception as e:
        logger.error(f"Error processing VK event: {e}")
        return {'success': False, 'message': str(e)}