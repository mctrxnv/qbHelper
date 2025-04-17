#! /usr/bin/env python3

from urllib.parse import urljoin
from typing import Dict, List, Optional
#
import requests
import argparse
import json
import sys
import os

class QBittorrentController:
    def __init__(self, base_url: str = "http://localhost:8080/", username: str = "admin", password: str = "adminadmin"):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self._authenticated = False
        
    def _ensure_authenticated(self):
        if not self._authenticated:
            self.login()
            
    def login(self) -> bool:
        """Аутентификация в qBittorrent WebUI"""
        login_url = urljoin(self.base_url, "api/v2/auth/login")
        data = {
            "username": self.username,
            "password": self.password
        }
        try:
            response = self.session.post(login_url, data=data)
            if response.text == "Ok.":
                self._authenticated = True
                return True
            else:
                print(f"Ошибка аутентификации: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Ошибка подключения к qBittorrent: {e}")
            return False
    
    def logout(self) -> bool:
        """Выход из системы"""
        logout_url = urljoin(self.base_url, "api/v2/auth/logout")
        try:
            response = self.session.post(logout_url)
            self._authenticated = False
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при выходе: {e}")
            return False
    
    def get_torrents(self, filter: str = "all", sort: str = None) -> List[Dict]:
        """Получить список торрентов"""
        self._ensure_authenticated()
        url = urljoin(self.base_url, "api/v2/torrents/info")
        params = {"filter": filter}
        if sort:
            params["sort"] = sort
            
        try:
            response = self.session.get(url, params=params)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении списка торрентов: {e}")
            return []
    
    def add_torrent(self, torrent: str, save_path: str = None, 
                    is_paused: bool = False) -> bool:
        """Добавить новый торрент"""
        self._ensure_authenticated()
        url = urljoin(self.base_url, "api/v2/torrents/add")
        
        data = {}
        if save_path:
            data["savepath"] = save_path
        if is_paused:
            data["paused"] = "true"
        
        files = None
        torrent_data = None
        
        if torrent.startswith("magnet:"):
            data["urls"] = torrent
        elif os.path.exists(torrent):
            files = {"torrents": open(torrent, "rb")}
        else:
            print("Неверный источник торрента. Должен быть magnet-ссылка или путь к .torrent файлу")
            return False
        
        try:
            if files:
                response = self.session.post(url, data=data, files=files)
                files["torrents"].close()
            else:
                response = self.session.post(url, data=data)
            
            if response.status_code == 200:
                return True
            else:
                print(f"Ошибка при добавлении торрента: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при добавлении торрента: {e}")
            return False
    
    def delete_torrents(self, hashes: List[str], delete_files: bool = False) -> bool:
        """Удалить торренты"""
        self._ensure_authenticated()
        url = urljoin(self.base_url, "api/v2/torrents/delete")
        data = {
            "hashes": "|".join(hashes),
            "deleteFiles": "true" if delete_files else "false"
        }
        
        try:
            response = self.session.post(url, data=data)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при удалении торрентов: {e}")
            return False
    
    def pause_torrents(self, hashes: List[str]) -> bool:
        """Приостановить торренты"""
        self._ensure_authenticated()
        url = urljoin(self.base_url, "api/v2/torrents/pause")
        data = {
            "hashes": "|".join(hashes)
        }
        
        try:
            response = self.session.post(url, data=data)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при приостановке торрентов: {e}")
            return False
    
    def resume_torrents(self, hashes: List[str]) -> bool:
        """Возобновить торренты"""
        self._ensure_authenticated()
        url = urljoin(self.base_url, "api/v2/torrents/resume")
        data = {
            "hashes": "|".join(hashes)
        }
        
        try:
            response = self.session.post(url, data=data)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при возобновлении торрентов: {e}")
            return False
    
    def get_torrent_properties(self, torrent_hash: str) -> Optional[Dict]:
        """Получить свойства торрента"""
        self._ensure_authenticated()
        url = urljoin(self.base_url, f"api/v2/torrents/properties?hash={torrent_hash}")
        
        try:
            response = self.session.get(url)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении свойств торрента: {e}")
            return None
    
    def get_torrent_trackers(self, torrent_hash: str) -> Optional[List[Dict]]:
        """Получить трекеры торрента"""
        self._ensure_authenticated()
        url = urljoin(self.base_url, f"api/v2/torrents/trackers?hash={torrent_hash}")
        
        try:
            response = self.session.get(url)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении трекеров торрента: {e}")
            return None
    
    def recheck_torrents(self, hashes: List[str]) -> bool:
        """Проверить торренты"""
        self._ensure_authenticated()
        url = urljoin(self.base_url, "api/v2/torrents/recheck")
        data = {
            "hashes": "|".join(hashes)
        }
        
        try:
            response = self.session.post(url, data=data)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при проверке торрентов: {e}")
            return False

    def get_torrents_for_completion(self) -> List[Dict]:
        """Получить список торрентов для автодополнения"""
        self._ensure_authenticated()
        try:
            response = self.session.get(urljoin(self.base_url, "api/v2/torrents/info"))
            torrents = response.json()
            return [{"hash": t["hash"], "name": t["name"]} for t in torrents]
        except:
            return []

def main():
    parser = argparse.ArgumentParser(description="Управление qBittorrent через CLI")
    parser.add_argument("--host", default="http://localhost:8080/", help="URL qBittorrent WebUI")
    parser.add_argument("--username", default="admin", help="Имя пользователя qBittorrent")
    parser.add_argument("--password", default="adminadmin", help="Пароль qBittorrent")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Список торрентов
    list_parser = subparsers.add_parser("list", help="Показать список торрентов")
    list_parser.add_argument("--filter", default="all", 
                            choices=["all", "downloading", "seeding", "completed", "paused", "active", "inactive", "resumed", "stalled", "stalled_uploading", "stalled_downloading"],
                            help="Фильтр торрентов")
    list_parser.add_argument("--sort", help="Сортировка")
    list_parser.add_argument("--details", action="store_true", help="Показать детальную информацию")
    
    # Добавление торрента
    add_parser = subparsers.add_parser("add", help="Добавить торрент")
    add_parser.add_argument("source", help="Magnet-ссылка или путь к .torrent файлу")
    add_parser.add_argument("--save-path", help="Путь для сохранения файлов")
    add_parser.add_argument("--paused", action="store_true", help="Добавить в приостановленном состоянии")
    
    # Удаление торрента
    delete_parser = subparsers.add_parser("delete", help="Удалить торрент")
    delete_parser.add_argument("hashes", nargs="+", help="Хэши торрентов для удаления")
    delete_parser.add_argument("--delete-files", action="store_true", help="Удалить файлы торрента")
    
    # Пауза
    pause_parser = subparsers.add_parser("pause", help="Приостановить торренты")
    pause_parser.add_argument("hashes", nargs="+", help="Хэши торрентов для приостановки")
    
    # Возобновление
    resume_parser = subparsers.add_parser("resume", help="Возобновить торренты")
    resume_parser.add_argument("hashes", nargs="+", help="Хэши торрентов для возобновления")
    
    # Проверка
    recheck_parser = subparsers.add_parser("recheck", help="Проверить торренты")
    recheck_parser.add_argument("hashes", nargs="+", help="Хэши торрентов для проверки")
    
    args = parser.parse_args()
    
    qbt = QBittorrentController(base_url=args.host, username=args.username, password=args.password)
    
    if not qbt.login():
        print("Не удалось подключиться к qBittorrent. Проверьте параметры подключения.")
        return

    if "--complete" in sys.argv:
        qbt = QBittorrentController()
        if qbt.login():
            torrents = qbt.get_torrents_for_completion()
            if sys.argv[2] in ["delete", "pause", "resume", "recheck"]:
                for t in torrents:
                    print(f"{t['hash']}\t{t['name']}")
            return
    
    try:
        if args.command == "list":
            torrents = qbt.get_torrents(filter=args.filter, sort=args.sort)
            if args.details:
                for torrent in torrents:
                    print(json.dumps(torrent, indent=2, ensure_ascii=False))
            else:
                # Определяем ширину столбцов
                hash_width = 10
                name_width = 30
                size_width = 8
                progress_width = 10
                state_width = 10
                speed_width = 15
                
                # Форматируем заголовок
                header = (f"{'Хэш':<{hash_width}} "
                         f"{'Название':<{name_width}} "
                         f"{'Размер':<{size_width}} "
                         f"{'Прогресс':<{progress_width}} "
                         f"{'Состояние':<{state_width}} "
                         f"{'Скорость':<{speed_width}}")
                print(header)
                print("-" * len(header.expandtabs()))
                
                # Форматируем каждую строку с торрентом
                for torrent in torrents:
                    name = torrent["name"]
                    if len(name) > name_width:
                        name = name[:name_width-3] + "..."
                    
                    print(f"{torrent['hash'][:hash_width-1]:<{hash_width}} "
                          f"{name:<{name_width}} "
                          f"{sizeof_fmt(torrent['size']):<{size_width}} "
                          f"{torrent['progress']*100:>{progress_width-1}.1f}% "
                          f"{torrent['state']:<{state_width}} "
                          f"{sizeof_fmt(torrent['dlspeed'])+'/s':<{speed_width}}")
        
        elif args.command == "add":
            if qbt.add_torrent(
                torrent=args.source,
                save_path=args.save_path,
                is_paused=args.paused
            ):
                print("Торрент успешно добавлен")
            else:
                print("Не удалось добавить торрент")
        
        elif args.command == "delete":
            if qbt.delete_torrents(hashes=args.hashes, delete_files=args.delete_files):
                print("Торренты успешно удалены")
            else:
                print("Не удалось удалить торренты")
        
        elif args.command == "pause":
            if qbt.pause_torrents(hashes=args.hashes):
                print("Торренты приостановлены")
            else:
                print("Не удалось приостановить торренты")
        
        elif args.command == "resume":
            if qbt.resume_torrents(hashes=args.hashes):
                print("Торренты возобновлены")
            else:
                print("Не удалось возобновить торренты")
        
        elif args.command == "recheck":
            if qbt.recheck_torrents(hashes=args.hashes):
                print("Торренты поставлены в очередь на проверку")
            else:
                print("Не удалось начать проверку торрентов")
    
    finally:
        qbt.logout()

def sizeof_fmt(num, suffix="B"):
    """Конвертировать размер в байтах в читаемый формат"""
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

if __name__ == "__main__":
    main()
