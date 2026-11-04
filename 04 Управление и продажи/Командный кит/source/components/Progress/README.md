# Progress

Полоса «сделано из плана». Дорожка `line` — это 100% плана, заливка — факт.

## Разметка

```html
<div class="dt-progress">
  <div class="dt-progress__row">
    <span class="dt-label">ОПЛАТЫ · 31 ИЗ 42</span>
    <span class="dt-num" style="font-size:32px;font-weight:700">74%</span>
  </div>
  <div class="dt-progress__track">
    <div class="dt-progress__fill dt-progress__fill--muted" style="width:74%"></div>
  </div>
</div>
```

Ты задаёшь `width` заливки в процентах (больше 100 — пиши 100, перевыполнение показывает число справа).

## Правила

- В метке — абсолют («31 из 42»), справа — процент. Одного процента мало.
- Кислотная заливка — у одной полосы (команда или лидер), остальные `--muted`.
- Пара «оплаты / дни недели» сразу показывает, отстаём ли от темпа — хороший приём для середины недели.
