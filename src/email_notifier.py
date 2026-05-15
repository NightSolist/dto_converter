import os
import smtplib
import ssl
from email.message import EmailMessage
from typing import Optional


class EmailNotifierError(Exception):
    pass


class EmailNotifier:
    """
    Отправляет уведомления инженеру по email.

    Параметры через переменные окружения:
        SMTP_HOST       — например, smtp.mail.ru
        SMTP_PORT       — 465 (SSL) или 587 (STARTTLS)
        SMTP_USER       — полный email отправителя
        SMTP_PASS       — пароль приложения
        NOTIFY_EMAIL    — email получателя
        NOTIFY_FROM     — отображаемое имя отправителя
    """

    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_pass: Optional[str] = None,
        notify_email: Optional[str] = None,
        from_name: Optional[str] = None,
    ):
        self.smtp_host = smtp_host or os.getenv(
            "SMTP_HOST", "smtp.mail.ru"
        )
        self.smtp_port = int(
            smtp_port or os.getenv("SMTP_PORT", "465")
        )
        self.smtp_user = smtp_user or os.getenv("SMTP_USER")
        self.smtp_pass = smtp_pass or os.getenv("SMTP_PASS")
        self.notify_email = notify_email or os.getenv(
            "NOTIFY_EMAIL"
        )
        self.from_name = from_name or os.getenv(
            "NOTIFY_FROM", "Incus Sync Bot"
        )

        if not self.smtp_user or not self.smtp_pass:
            raise EmailNotifierError(
                "Не заданы SMTP_USER / SMTP_PASS "
                "в переменных окружения."
            )
        if not self.notify_email:
            raise EmailNotifierError(
                "Не задан NOTIFY_EMAIL в переменных окружения."
            )

    def _send(self, msg: EmailMessage) -> None:
        ctx = ssl.create_default_context()
        try:
            if self.smtp_port == 465:
                with smtplib.SMTP_SSL(
                    self.smtp_host,
                    self.smtp_port,
                    context=ctx,
                ) as server:
                    server.login(self.smtp_user, self.smtp_pass)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(
                    self.smtp_host, self.smtp_port
                ) as server:
                    server.starttls(context=ctx)
                    server.login(self.smtp_user, self.smtp_pass)
                    server.send_message(msg)
        except smtplib.SMTPException as e:
            raise EmailNotifierError(
                f"Ошибка отправки email: {e}"
            ) from e

    def send_pr_notification(
        self,
        pr_url: str,
        pr_number: Optional[int] = None,
        files_count: Optional[int] = None,
        commit_sha: Optional[str] = None,
    ) -> None:
        """Отправляет уведомление о создании Pull Request."""
        subject = "🤖 Incus Sync: создан новый Pull Request"
        if pr_number:
            subject = (
                f"🤖 Incus Sync: PR #{pr_number} готов к review"
            )

        body_lines = [
            "Здравствуйте!",
            "",
            "Система автоматической синхронизации Incus DTO "
            "обнаружила изменения в Go-репозитории и "
            "сгенерировала обновлённые Rust-модели данных.",
            "",
            "Сводка:",
            f"  • Pull Request: {pr_url}",
        ]
        if files_count is not None:
            body_lines.append(f"  • Файлов в PR:  {files_count}")
        if commit_sha:
            body_lines.append(
                f"  • Source SHA:    {commit_sha[:12]}"
            )

        body_lines.extend([
            "",
            "Этапы проверки:",
            "  ✓ Парсинг Go-структур",
            "  ✓ Шаблонная генерация (Jinja2)",
            "  ✓ LLM repair при необходимости (Ollama)",
            "  ✓ Компиляционная валидация (cargo check)",
            "  ✓ Pull Request создан в Rust-репозитории",
            "  ✓ Запущен self-hosted Woodpecker CI/CD pipeline",
            "",
            "Пожалуйста, проверьте изменения и выполните merge, "
            "если всё корректно.",
            "",
            "—",
            "Incus Sync Bot",
            "Автоматическое сообщение, не отвечайте на него.",
        ])

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.smtp_user}>"
        msg["To"] = self.notify_email
        msg.set_content("\n".join(body_lines))

        self._send(msg)
        print(f"📧 PR email отправлен на {self.notify_email}")

    def send_sync_failure_notification(
        self,
        failed_entities: list[dict],
        changed_files: list[str],
        commit_sha: Optional[str] = None,
    ) -> None:
        """
        Уведомляет инженера о типах, которые не удалось
        синхронизировать ни шаблоном, ни LLM repair.
        """
        subject = (
            "⚠️ Incus Sync: автоматическая синхронизация "
            "не выполнена"
        )

        body_lines = [
            "Здравствуйте!",
            "",
            "Система автоматической синхронизации Incus DTO "
            "обнаружила изменения в Go-репозитории, но не смогла "
            "выполнить синхронизацию средствами программного "
            "прототипа.",
            "",
            "Использованные методы:",
            "  ✗ Шаблонная генерация (Jinja2)",
            "  ✗ LLM repair (Ollama + qwen2.5-coder:1.5b)",
            "",
        ]

        if commit_sha:
            body_lines.append(
                f"Коммит Incus: {commit_sha[:12]}"
            )
            body_lines.append(
                f"Ссылка: "
                f"https://github.com/lxc/incus/commit/{commit_sha}"
            )
            body_lines.append("")

        if changed_files:
            body_lines.append("Изменённые Go-файлы:")
            for path in changed_files:
                body_lines.append(f"  • {path}")
            body_lines.append("")

        body_lines.append(
            f"Типы, требующие ручной синхронизации "
            f"({len(failed_entities)}):"
        )
        for item in failed_entities:
            body_lines.append(
                f"  • {item['name']} "
                f"({item['kind']}): {item['error']}"
            )

        body_lines.extend([
            "",
            "Необходимые действия:",
            "  1. Изучить изменения в Go-репозитории Incus",
            "  2. Вручную обновить соответствующие Rust-модели",
            "  3. Запустить cargo check и cargo test",
            "  4. При необходимости обновить правила "
            "шаблонной генерации",
            "",
            "—",
            "Incus Sync Bot",
            "Автоматическое сообщение, не отвечайте на него.",
        ])

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.smtp_user}>"
        msg["To"] = self.notify_email
        msg.set_content("\n".join(body_lines))

        self._send(msg)
        print(
            f"📧 Failure email отправлен на {self.notify_email}"
        )