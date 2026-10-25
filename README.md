# circuit_lab

Моделирование электрических цепей в диалоге с ИИ-агентом: схемы KiCad с SPICE-моделями, симуляция в ngspice. Подробнее — [docs/index.md](docs/index.md).

## Установка

Зависимости и их установка — [docs/infrastructure.md](docs/infrastructure.md#зависимости).

## Запуск

```
uv run tools/build.py              # сборка всех цепей
uv run tools/build.py chandelier   # сборка одной цепи
uv run tools/simulate.py           # сценарий цепи люстры
```
