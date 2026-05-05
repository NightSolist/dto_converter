from src.monitor import MonitorError, save_state, run_monitor
from src.pipeline import Pipeline


def main():
    try:
        print("🔎 Проверяем новые изменения в репозитории Incus...")
        monitor_result = run_monitor()

        if monitor_result.get("no_changes", False):
            print("⏹ Релевантных изменений нет. Pipeline запускаться не будет.")
            return

        latest_sha = monitor_result.get("last_sha")

        print("🚀 Обнаружены изменения. Запускаем pipeline...")
        pipeline = Pipeline()
        success = pipeline.run()

        if success and latest_sha:
            save_state(latest_sha)
            print(f"✅ Состояние обновлено: {latest_sha}")
        elif not success:
            print("⚠️ Pipeline завершился с ошибкой. Состояние НЕ обновлено.")
            raise SystemExit(1)

    except MonitorError as e:
        print(f"❌ Ошибка мониторинга: {e}")
        raise SystemExit(1)
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()