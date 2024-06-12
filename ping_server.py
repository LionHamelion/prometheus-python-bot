import requests
import time
import threading

# Функція для періодичного запиту до сервера
def ping_server():
    while True:
        try:
            url = os.getenv('ENDPOINT_URL')
            response = requests.get(url)
            if response.status_code == 200:
                print('Server is awake')
            else:
                print(f'Failed to ping server with status code: {response.status_code}')
        except Exception as e:
            print(f'Error pinging server: {e}')
        time.sleep(14 * 60)  # Чекати 14 хвилин перед наступним запитом

# Запуск пінгування сервера у окремому потоці
def start_ping_server():
    threading.Thread(target=ping_server, daemon=True).start()
