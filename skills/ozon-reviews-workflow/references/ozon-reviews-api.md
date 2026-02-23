# Ozon Reviews API Reference

## Endpoints

### GET /v1/review/list

Получить список отзывов.

**Request:**
```json
{
  "limit": 20,
  "sort_dir": "DESC",
  "sku": 123456
}
```

**Response:**
```json
{
  "reviews": [
    {
      "id": "uuid",
      "sku": 123456,
      "text": "текст отзыва",
      "rating": 5,
      "status": "UNPROCESSED",
      "published_at": "2026-02-02T10:00:00Z",
      "comments_amount": 0,
      "photos_amount": 0,
      "videos_amount": 0,
      "order_status": "DELIVERED"
    }
  ],
  "has_next": true,
  "last_id": "uuid"
}
```

### GET /v1/review/comment/list

Получить комментарии к отзыву.

**Request:**
```json
{
  "review_id": "uuid",
  "limit": 20
}
```

**Response:**
```json
{
  "comments": [
    {
      "id": "uuid",
      "text": "текст комментария",
      "published_at": "2026-02-02T10:00:00Z",
      "is_owner": false,
      "is_official": false
    }
  ],
  "offset": 0
}
```

### POST /v1/review/comment/create

Ответить на отзыв.

**Request:**
```json
{
  "review_id": "uuid",
  "text": "Благодарим за отзыв!"
}
```

**Response:**
```json
{
  "comment_id": "uuid"
}
```

### POST /v1/review/change-status ⚠️ ОБЯЗАТЕЛЬНО

**Обновить статус отзыва после отправки ответа!**

Без этого отзыв останется `UNPROCESSED` даже с комментарием.

**Request:**
```json
{
  "review_ids": [
    "017c0ddf-8b43-854b-4b67-75676025a1c1",
    "017c0de6-3b86-8e7f-4f81-6bf2147fa38b"
  ],
  "status": "PROCESSED"
}
```

**Parameters:**
- `review_ids`: array of strings, 1-100 items
- `status`: "PROCESSED" или "UNPROCESSED"

**Response:**
```json
{}
```

**Пример использования:**
```python
# После отправки ответов
review_ids = [r['id'] for r in replied_reviews]
requests.post(
    "https://api-seller.ozon.ru/v1/review/change-status",
    headers=headers,
    json={
        "review_ids": review_ids,
        "status": "PROCESSED"
    }
)
```

## Поля отзыва

| Поле | Тип | Описание |
|------|-----|----------|
| id | string | UUID отзыва |
| sku | int | Артикул товара |
| text | string | Текст отзыва |
| rating | int | 1-5 звёзд |
| status | string | UNPROCESSED/PROCESSED |
| published_at | string | ISO 8601 дата |
| comments_amount | int | Кол-во комментариев |
| photos_amount | int | Кол-во фото |
| videos_amount | int | Кол-во видео |

## Лимиты

- 40 запросов/минуту
- `limit`: 20-100
- `review_ids` в change-status: 1-100 ID

## Рабочий процесс

```
1. GET /v1/review/list
   ↓
2. POST /v1/review/comment/create (ответить)
   ↓
3. POST /v1/review/change-status ← ⚠️ ОБЯЗАТЕЛЬНО!
   ↓
4. Проверить: status = "PROCESSED"
```

## Фильтры

- По рейтингу: min/max
- По дате: sort_dir ASC/DESC
- По артикулу: sku
- По статусу: status

## Статусы отзывов

| Статус | Описание | Комментарии | Действие |
|--------|----------|-------------|----------|
| UNPROCESSED | Новый отзыв | 0 | Ответить |
| UNPROCESSED | С ответом | >0 | ⚠️ Обновить статус! |
| PROCESSED | Обработан | >0 | ✅ Готово |
