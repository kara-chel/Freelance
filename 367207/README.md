# Парсинг табличных данных


[Парсинг табличных данных](https://freelance.habr.com/tasks/367207)


[2017](https://old-tender.rzd.ru/tender-plan/public/ru?layer_id=6055&STRUCTURE_ID=704&planned_year=2017),
[2018](https://old-tender.rzd.ru/tender-plan/public/ru?layer_id=6055&STRUCTURE_ID=704&planned_year=2018),
[2019](https://old-tender.rzd.ru/tender-plan/public/ru?layer_id=6055&STRUCTURE_ID=704&planned_year=2019),
[2020](https://old-tender.rzd.ru/tender-plan/public/ru?layer_id=6055&STRUCTURE_ID=704&planned_year=2020),
[2021](https://old-tender.rzd.ru/tender-plan/public/ru?layer_id=6055&STRUCTURE_ID=704&planned_year=2021)


## Устанавливаем зависимости
```bash
pip3 install scrapy
pip3 install pproxy
```

## Запуск проекта
```bash
# Запустить тор браузер
tor
# Запустить прокси "конвертр" http -> socks5
pproxy -l http://:8181 -r socks5://127.0.0.1:9150 -vv
# Запустить скрипт
python3 main.py
```


```
16:28
18:00
```