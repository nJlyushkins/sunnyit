import importlib.util
import os

def process_vk_event(library_path, event_data):
    try:
        # Динамическая загрузка модуля бота
        spec = importlib.util.spec_from_file_location("bot_module", library_path)
        bot_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bot_module)

        # Вызов метода обработки события (предполагается, что он есть)
        if hasattr(bot_module, 'handle_event'):
            bot_module.handle_event(event_data)
    except Exception as e:
        print(f"Ошибка при обработке события: {e}")