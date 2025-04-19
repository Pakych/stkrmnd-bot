from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class CustomHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Додаємо заголовок для пропуску попередження ngrok
        self.send_header('ngrok-skip-browser-warning', 'true')
        SimpleHTTPRequestHandler.end_headers(self)

    def do_GET(self):
        # Якщо шлях кореневий, перенаправляємо на index.html
        if self.path == '/':
            self.path = '/index.html'
        return SimpleHTTPRequestHandler.do_GET(self)

def run_server(port=8000):
    try:
        # Змінюємо робочу директорію на web/
        web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')
        os.chdir(web_dir)
        
        # Запускаємо HTTP сервер
        server = HTTPServer(('0.0.0.0', port), CustomHandler)
        print(f"\nЛокальний сервер запущено на порту {port}")
        print(f"Локальна адреса: http://localhost:{port}")
        print("\nНатисніть Ctrl+C для зупинки сервера")
        
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nЗупиняємо сервер...")
    except Exception as e:
        print(f"Помилка: {e}")

if __name__ == '__main__':
    # Переходимо в директорію зі скриптом
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run_server() 