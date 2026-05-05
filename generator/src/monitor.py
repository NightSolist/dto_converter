import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from github import Github, GithubException, RateLimitExceededException


INCUS_REPO = "lxc/incus"
STATE_FILE = Path(".sync_state")
CHANGES_FILE = Path("changes.json")
LOOKBACK_DAYS = 30

API_PATH_PREFIX = "shared/api/"
CLIENT_PATH_PREFIX = "client/"


class MonitorError(Exception):
    pass


def load_state(state_file: Path = STATE_FILE) -> Optional[str]:
    if not state_file.exists():
        return None

    value = state_file.read_text(encoding="utf-8").strip()
    return value or None


def save_state(sha: str, state_file: Path = STATE_FILE) -> None:
    state_file.write_text(sha, encoding="utf-8")


def get_github_repo(repo_name: str = INCUS_REPO):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise MonitorError("Не задана переменная окружения GITHUB_TOKEN")

    from github import Auth
    gh = Github(auth=Auth.Token(token))
    return gh.get_repo(repo_name)


def get_commits_since(repo, last_sha: Optional[str], lookback_days: int = LOOKBACK_DAYS):
    """
    Возвращает список коммитов в хронологическом порядке: от старых к новым.
    """
    if last_sha is None:
        since = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        commits = list(repo.get_commits(since=since))
        return list(reversed(commits))

    commits = []
    found_last_sha = False

    for commit in repo.get_commits():
        if commit.sha == last_sha:
            found_last_sha = True
            break
        commits.append(commit)

    if not found_last_sha:
        since = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        commits = list(repo.get_commits(since=since))

    return list(reversed(commits))


def classify_files(commit_files) -> dict:
    api_files = []
    client_files = []

    for file_obj in commit_files:
        path = file_obj.filename

        if path.endswith("_test.go"):
            continue

        if path.startswith(API_PATH_PREFIX) and path.endswith(".go"):
            api_files.append(
                {
                    "path": path,
                    "status": file_obj.status,
                }
            )
        elif path.startswith(CLIENT_PATH_PREFIX) and path.endswith(".go"):
            client_files.append(
                {
                    "path": path,
                    "status": file_obj.status,
                }
            )

    return {
        "api_files": api_files,
        "client_files": client_files,
    }


def merge_file_entries(existing: list[dict], new_entries: list[dict]) -> list[dict]:
    """
    Объединяет списки файлов по path, чтобы не было дублей.
    Если файл встречается несколько раз, сохраняется последний status.
    """
    merged = {item["path"]: dict(item) for item in existing}

    for item in new_entries:
        merged[item["path"]] = dict(item)

    return list(sorted(merged.values(), key=lambda x: x["path"]))


def build_empty_result(last_sha: Optional[str]) -> dict:
    return {
        "no_changes": True,
        "last_sha": last_sha,
        "api_changes": {
            "files": [],
            "commits": [],
        },
        "client_changes": {
            "files": [],
            "commits": [],
        },
    }


def run_monitor(
    repo_name: str = INCUS_REPO,
    state_file: Path = STATE_FILE,
    output_file: Path = CHANGES_FILE,
    lookback_days: int = LOOKBACK_DAYS,
) -> dict:
    try:
        repo = get_github_repo(repo_name)
        last_sha = load_state(state_file)
        commits = get_commits_since(repo, last_sha, lookback_days)

        if not commits:
            result = build_empty_result(last_sha)
            output_file.write_text(
                json.dumps(result, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            print("Изменений не обнаружено.")
            return result

        api_changes = {"files": [], "commits": []}
        client_changes = {"files": [], "commits": []}

        latest_seen_sha = commits[-1].sha

        for commit in commits:
            classified = classify_files(commit.files)

            if classified["api_files"]:
                api_changes["files"] = merge_file_entries(
                    api_changes["files"],
                    classified["api_files"],
                )
                api_changes["commits"].append(commit.sha)

            if classified["client_files"]:
                client_changes["files"] = merge_file_entries(
                    client_changes["files"],
                    classified["client_files"],
                )
                client_changes["commits"].append(commit.sha)

        no_changes = not api_changes["files"] and not client_changes["files"]

        result = {
            "no_changes": no_changes,
            "last_sha": latest_seen_sha,
            "api_changes": api_changes,
            "client_changes": client_changes,
        }

        output_file.write_text(
            json.dumps(result, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # Обновляем состояние даже если изменения нерелевантны,
        # чтобы не обрабатывать те же коммиты повторно.
        save_state(latest_seen_sha, state_file)

        if no_changes:
            print("Новых релевантных изменений в shared/api/ и client/ нет.")
        else:
            print(
                f"Найдено изменений: "
                f"{len(api_changes['files'])} файлов API, "
                f"{len(client_changes['files'])} файлов client/"
            )

        return result

    except RateLimitExceededException as e:
        raise MonitorError(f"Превышен лимит запросов GitHub API: {e}") from e
    except GithubException as e:
        raise MonitorError(f"Ошибка GitHub API: {e}") from e
    except Exception as e:
        raise MonitorError(f"Ошибка мониторинга: {e}") from e


if __name__ == "__main__":
    result = run_monitor()
    print(json.dumps(result, indent=2, ensure_ascii=False))