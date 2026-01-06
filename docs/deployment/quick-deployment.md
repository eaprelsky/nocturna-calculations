# Quick Deployment Guide

Упрощенная система развертывания с автоматическим определением слота и единой точкой входа.

## 🚀 Быстрый старт

### Первое развертывание

```bash
# 1. Подготовить .env
cp config/production.env.example .env
vim .env  # Заполнить значения

# 2. Проверить инфраструктуру
./scripts/check-infrastructure.sh

# 3. Развернуть (автоматически выберет blue)
./scripts/deploy.sh auto
```

### Обновление без даунтайма

```bash
# 1. Развернуть на неактивный слот (автоматически определит green)
./scripts/deploy.sh auto

# 2. Проверить статус
./scripts/status.sh

# 3. Переключить трафик
./scripts/switch.sh green

# 4. При проблемах - откат
./scripts/rollback.sh
```

## 📋 Команды

### `deploy.sh` - Развертывание

```bash
# Автоматический выбор слота (рекомендуется)
./scripts/deploy.sh auto

# Развернуть на конкретный слот
./scripts/deploy.sh blue
./scripts/deploy.sh green

# Развернуть staging
./scripts/deploy.sh staging

# С полной пересборкой
./scripts/deploy.sh auto --rebuild
```

**Что делает:**
- Автоматически определяет неактивный слот
- Создает/проверяет shared инфраструктуру (БД, Redis)
- Собирает и запускает контейнер
- Ждет health check
- Показывает следующие шаги

### `switch.sh` - Переключение трафика

```bash
./scripts/switch.sh blue
./scripts/switch.sh green
```

**Что делает:**
- Проверяет health целевого слота
- Запрашивает подтверждение
- Обновляет nginx конфигурацию
- Перезагружает nginx
- Сохраняет метаданные для rollback

### `status.sh` - Показать статус

```bash
./scripts/status.sh
```

**Показывает:**
- Активный слот
- Статус blue/green/staging
- Health checks
- Uptime контейнеров
- Статус инфраструктуры (БД, Redis)
- Быстрые команды

### `rollback.sh` - Откат

```bash
./scripts/rollback.sh
```

**Что делает:**
- Определяет предыдущий активный слот
- Проверяет что он работает
- Запрашивает подтверждение
- Переключает трафик обратно

### `check-infrastructure.sh` - Проверка инфраструктуры

```bash
./scripts/check-infrastructure.sh
```

**Проверяет:**
- Docker и Docker Compose
- PostgreSQL контейнер и health
- Redis контейнер и health
- Docker network
- Volumes
- Статус blue/green/staging

## 🏗️ Архитектура

### Shared Infrastructure

Общая инфраструктура для blue и green:

```
docker-compose.shared.yml
├── postgres (nocturna-postgres:5432)
├── redis (nocturna-redis:6379)
└── network (nocturna-network)
```

### Production Instances

```
docker-compose.blue.yml
└── nocturna-api-blue (port 8200)

docker-compose.green.yml
└── nocturna-api-green (port 8201)
```

Оба используют одну БД и Redis.

### Staging

```
docker-compose.staging.yml
├── nocturna-staging-api (port 8100)
├── nocturna-staging-db (port 5433)
└── nocturna-staging-redis (port 6380)
```

Полностью изолированное окружение.

## 🔄 Типичный workflow

### Сценарий 1: Первое развертывание

```bash
# На сервере
cd /opt/calc/prod
git clone <repo> .
cp .env.example .env
vim .env

# Развернуть
./scripts/deploy.sh auto
# → Развернется на blue (нет активного слота)

# Запустить nginx
docker-compose -f docker-compose.nginx.yml up -d

# Проверить
./scripts/status.sh
```

### Сценарий 2: Обновление версии

```bash
cd /opt/calc/prod
git pull

# Blue активен → развернется на green
./scripts/deploy.sh auto

# Проверить
curl http://localhost:8201/health
./scripts/status.sh

# Переключить
./scripts/switch.sh green

# Остановить старый blue
docker-compose -f docker-compose.blue.yml down
```

### Сценарий 3: Проблема после переключения

```bash
# Быстрый откат
./scripts/rollback.sh
# → Вернется на blue

# Посмотреть логи проблемного green
docker-compose -f docker-compose.green.yml logs

# Исправить проблему и повторить
```

### Сценарий 4: Staging тестирование

```bash
cd /opt/calc/stage
git pull

./scripts/deploy.sh staging

# Тестирование
curl http://localhost:8100/health

# Посмотреть логи
docker-compose -f docker-compose.staging.yml logs -f
```

## 📊 Метаданные

Система использует файлы для отслеживания состояния:

- `.current-env` - текущий активный слот (blue/green)
- `.previous-env` - предыдущий активный слот (для rollback)

Эти файлы создаются автоматически и не должны коммититься в git.

## 🔍 Диагностика

### Проблема: "Failed to ensure shared infrastructure"

```bash
# Проверить статус
./scripts/check-infrastructure.sh

# Пересоздать
docker-compose -f docker-compose.shared.yml down
docker-compose -f docker-compose.shared.yml up -d
```

### Проблема: "Instance failed health check"

```bash
# Посмотреть логи
docker-compose -f docker-compose.blue.yml logs

# Проверить БД
docker exec nocturna-postgres pg_isready

# Проверить Redis
docker exec nocturna-redis redis-cli ping
```

### Проблема: "Network not found"

```bash
# Пересоздать network
docker network rm nocturna-network
docker-compose -f docker-compose.shared.yml up -d
```

## 🎯 Best Practices

1. **Всегда используйте `auto`** для production деплоя
   ```bash
   ./scripts/deploy.sh auto
   ```

2. **Проверяйте статус** перед переключением
   ```bash
   ./scripts/status.sh
   curl http://localhost:8201/health
   ```

3. **Держите старый слот** несколько минут после переключения
   ```bash
   # Не удаляйте сразу
   # docker-compose -f docker-compose.blue.yml down  # ❌
   
   # Подождите 10-15 минут, потом:
   docker-compose -f docker-compose.blue.yml down  # ✓
   ```

4. **Используйте tags** для версионирования
   ```bash
   export IMAGE_TAG=v1.2.0
   ./scripts/deploy.sh auto
   ```

5. **Регулярные бэкапы** БД
   ```bash
   docker exec nocturna-postgres pg_dump -U postgres nocturna_prod > backup.sql
   ```

## 🆚 Сравнение со старой системой

| Функция | Старая система | Новая система |
|---------|---------------|---------------|
| Команд для деплоя | 3+ отдельных скрипта | 1 команда `deploy.sh auto` |
| Определение слота | Ручное | Автоматическое |
| Shared инфраструктура | Дублируется | Общая БД и Redis |
| Проверка здоровья | Ручная | Автоматическая |
| Откат | Сложный | `rollback.sh` |
| Статус | Нет единого места | `status.sh` с красивым выводом |
| Диагностика | Сложная | `check-infrastructure.sh` |

## 📚 Дополнительно

- [Blue-Green Deployment Guide](blue-green-deployment.md) - подробное руководство
- [Docker Deployment](docker.md) - документация по Docker
- [Troubleshooting](../guides/troubleshooting.md) - решение проблем
