# Leaderboard

Рейтинг для картинки: место, имя, результат, динамика. Лидер — на `acid-deep`, номер в `acid`.

## Разметка

```html
<div class="dt-board">
  <div class="dt-board__head">
    <span class="dt-label">#</span><span class="dt-label">МЕНЕДЖЕР</span>
    <span class="dt-label">ОПЛАТЫ</span><span class="dt-label">Δ</span>
  </div>
  <div class="dt-board__row dt-board__row--leader">
    <span class="dt-board__place">01</span>
    <span class="dt-board__name">Алиса В.</span>
    <span class="dt-board__value">14</span>
    <span class="dt-board__delta dt-delta dt-delta--up">3</span>
  </div>
  …
</div>
```

## Правила

- Порядок колонок: место → имя → результат → (% плана) → динамика.
- Места двузначные: `01`, `02` — колонка не прыгает.
- Имя + первая буква фамилии. Длинное обрезается многоточием.
- До 10 строк на 1080×1350. Больше — топ-10 на картинке, полная таблица файлом.
- Хвост рейтинга не выделяем ничем. `alert` в рейтинге людей не используется.
- Ничья — одинаковый номер места у обоих (`03`, `03`, `05`).
