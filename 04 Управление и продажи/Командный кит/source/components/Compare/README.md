# Compare

Два варианта рядом: пункты с `[+]` и `[–]`, рекомендуемый вариант — справа в рамке `acid`.

## Разметка

```html
<div class="dt-compare">
  <div class="dt-compare__col">
    <span class="dt-label">ПОМЕСЯЧНО</span>
    <div class="dt-compare__item"><span class="dt-compare__no"></span><span>Пункт</span></div>
  </div>
  <div class="dt-compare__col dt-compare__col--pick">
    <span class="dt-label dt-label--acid">ПАКЕТ · ВЫГОДНЕЕ</span>
    <div class="dt-compare__item"><span class="dt-compare__yes"></span><span>Пункт</span></div>
  </div>
</div>
```

## Правила

- Рекомендуемый — справа: взгляд заканчивает на нём.
- Пункты в одинаковом порядке в обеих колонках — сравнивают построчно.
- 3–5 пунктов. Больше — это таблица (`DataTable`).
- Только два варианта. Три тарифа — таблица с колонкой на тариф.
