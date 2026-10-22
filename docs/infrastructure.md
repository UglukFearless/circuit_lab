# Инфраструктура

Платформа — Windows 10/11.

## Зависимости

| Компонент | Версия | Назначение | Установка | Расположение |
|---|---|---|---|---|
| uv | 0.13 | Python, окружение, зависимости | `winget install astral-sh.uv` | в PATH |
| Python | ≥ 3.12 | скрипты проекта | `uv sync` | `.venv/` |
| KiCad | 10.0.6 | модели цепей, `kicad-cli` | `winget install KiCad.KiCad` | `%LOCALAPPDATA%\Programs\KiCad\10.0` |
| ngspice | 47 | симуляция | [вручную](#установка-ngspice) | `%LOCALAPPDATA%\Programs\ngspice` |
| 7-Zip | любая | распаковка архива ngspice | `winget install 7zip.7zip` | — |

Скрипты ищут `kicad-cli` в переменной окружения `KICAD_CLI`, затем в PATH, затем в `%LOCALAPPDATA%\Programs\KiCad\10.0\bin`; ngspice — в переменной `NGSPICE`, затем `ngspice_con` и `ngspice` в PATH.

## Установка ngspice

1. Скачать `ngspice-47_64.7z` со страницы загрузки [ngspice.sourceforge.io](https://ngspice.sourceforge.io/download.html). SHA256: `59225971bd68cdd1199443649aa4615a9e6d684933f205ab49006a3942518f5a`.
2. Распаковать 7-Zip, скопировать `Spice64` в `%LOCALAPPDATA%\Programs\ngspice`.
3. Добавить `%LOCALAPPDATA%\Programs\ngspice\bin` в PATH пользователя.

## Известные сообщения

Сценарий выводит `Could not find library '"…/models.lib"'`: `spicelib` не снимает кавычки с пути в `.include`. На результат не влияет — библиотеку находит ngspice.
