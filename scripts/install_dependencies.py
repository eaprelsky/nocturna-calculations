"""
Dependency installation script for the project.
"""
import os
import sys
import subprocess

# Список обязательных зависимостей
REQUIRED_PYTHON_PACKAGES = [
    "psycopg2-binary",  # Для PostgreSQL
    "redis",            # Для Redis
    "alembic",          # Для миграций
    "sqlalchemy",       # Для работы с БД
    "prometheus-client" # Для метрик
]

def install_package(package):
    """Установка одного пакета."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"Успешно установлен: {package}")
    except subprocess.CalledProcessError:
        print(f"Ошибка при установке {package}")
        sys.exit(1)

def check_and_install_dependencies():
    """Проверка и установка всех зависимостей."""
    print("Проверка зависимостей...")
    for package in REQUIRED_PYTHON_PACKAGES:
        try:
            __import__(package.split("==")[0])  # Игнорируем версии (если указаны)
            print(f"Найдено: {package}")
        except ImportError:
            print(f"Не найдено: {package}")
            install_package(package)

if __name__ == "__main__":
    check_and_install_dependencies() 