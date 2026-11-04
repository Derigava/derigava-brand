# DoDont

Два столбца «так / не так» для разбора формулировок и ошибок. Всегда с текстовыми метками `[OK] ТАК` и `[!] НЕ ТАК` — цвет не единственный сигнал.

## Разметка

```html
<div class="dt-dodont">
  <div class="dt-dodont__col dt-dodont__col--do">
    <span class="dt-label dt-label--acid">[OK] ТАК</span>
    <p class="dt-dodont__quote">«Правильная формулировка»</p>
    <p class="dt-dodont__why">Почему работает.</p>
  </div>
  <div class="dt-dodont__col dt-dodont__col--dont">
    <span class="dt-label dt-label--alert">[!] НЕ ТАК</span>
    <p class="dt-dodont__quote">«Ошибочная формулировка»</p>
    <p class="dt-dodont__why">Что ломает.</p>
  </div>
</div>
```

## Правила

- «Так» всегда слева — читают сначала правильное.
- Примеры — реальные фразы из звонков, но без имён и узнаваемых деталей сотрудника.
- Пояснение «почему» обязательно: без него это просто запрет.
