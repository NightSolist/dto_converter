from src.github_publisher import GitHubPublisher
from src.monitor import MonitorError, save_state, run_monitor
from src.pipeline import Pipeline
from src.woodpecker_trigger import WoodpeckerError, WoodpeckerTrigger


# Репозиторий Rust-клиента, куда будут публиковаться сгенерированные DTO.
RUST_REPO_NAME = "NightSolist/incus-lab-manager"

# Опционально: GitHub username ревьюера.
GITHUB_REVIEWER = None


def main():
    try:
        if RUST_REPO_NAME == "YOUR_GITHUB_USERNAME/incus-lab-manager":
            raise ValueError(
                "Не настроен RUST_REPO_NAME в main.py. "
                "Укажите реальный GitHub-репозиторий Rust-клиента."
            )

        print("🔎 Проверяем новые изменения в репозитории Incus...")
        monitor_result = run_monitor()

        if monitor_result.get("no_changes", False):
            print("⏹ Релевантных изменений нет. Pipeline запускаться не будет.")
            return

        latest_sha = monitor_result.get("last_sha")

        print("🚀 Обнаружены изменения. Запускаем pipeline...")
        pipeline = Pipeline()
        success = pipeline.run()

        if not success:
            print("⚠️ Pipeline завершился с ошибкой. Состояние НЕ обновлено.")
            raise SystemExit(1)

        print("\n🌐 Публикуем результат в GitHub...")
        publisher = GitHubPublisher(
            repo_name=RUST_REPO_NAME,
            reviewer=GITHUB_REVIEWER,
        )

        pr_url = publisher.publish(
            generated_dir=pipeline.config.output_dir,
            target_path="src/incus/generated_prototype",
        )

        print(f"🎉 Pull Request создан: {pr_url}")

        # === Триггер Woodpecker CI/CD pipeline ===
        print("\n⚙️  Запускаем self-hosted Woodpecker CI/CD pipeline...")
        try:
            trigger = WoodpeckerTrigger()
            wp_url = trigger.trigger_pipeline(branch="main")
            print(f"📊 Pipeline в Woodpecker: {wp_url}")
            print("📧 Email-уведомление будет отправлено после завершения CI.")
        except WoodpeckerError as e:
            print(f"⚠️ Woodpecker pipeline не запущен: {e}")
        except Exception as e:
            print(f"⚠️ Триггер CI пропущен: {e}")

        if latest_sha:
            save_state(latest_sha)
            print(f"✅ Состояние обновлено: {latest_sha}")

    except MonitorError as e:
        print(f"❌ Ошибка мониторинга: {e}")
        raise SystemExit(1)
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()