import os
from typing import Optional

import requests


class WoodpeckerError(Exception):
    pass


class WoodpeckerTrigger:
    """
    Триггерит pipeline в локальном Woodpecker через REST API.

    Параметры через переменные окружения:
        WOODPECKER_URL    — например, http://woodpecker-server:8000
        WOODPECKER_TOKEN  — Personal Access Token из Woodpecker UI
        WOODPECKER_REPO   — например, NightSolist/incus-lab-manager
    """

    def __init__(
        self,
        woodpecker_url: Optional[str] = None,
        token: Optional[str] = None,
        repo_full_name: Optional[str] = None,
    ):
        url = (
            woodpecker_url
            or os.getenv("WOODPECKER_URL")
            or "http://woodpecker-server:8000"
        )
        self.url = url.rstrip("/")
        self.token = token or os.getenv("WOODPECKER_TOKEN")
        self.repo_full_name = (
            repo_full_name
            or os.getenv("WOODPECKER_REPO")
            or "NightSolist/incus-lab-manager"
        )

        if not self.token:
            raise WoodpeckerError(
                "Не задан WOODPECKER_TOKEN в переменных окружения."
            )

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }

    def _get_repo_id(self) -> int:
        endpoint = (
            f"{self.url}/api/repos/lookup/{self.repo_full_name}"
        )
        resp = requests.get(
            endpoint, headers=self._headers(), timeout=10
        )
        if resp.status_code != 200:
            raise WoodpeckerError(
                f"Не удалось получить repo id "
                f"для {self.repo_full_name}: "
                f"{resp.status_code} {resp.text[:200]}"
            )
        return int(resp.json()["id"])

    def trigger_pipeline(
        self,
        branch: str = "main",
        commit_sha: Optional[str] = None,
    ) -> str:
        repo_id = self._get_repo_id()
        endpoint = f"{self.url}/api/repos/{repo_id}/pipelines"

        payload = {"branch": branch}
        if commit_sha:
            payload["commit"] = commit_sha

        resp = requests.post(
            endpoint,
            headers=self._headers(),
            json=payload,
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            raise WoodpeckerError(
                f"Не удалось триггернуть pipeline: "
                f"{resp.status_code} {resp.text[:200]}"
            )

        data = resp.json()
        pipeline_number = data.get("number")

        pipeline_url = (
            f"{self.url}/repos/"
            f"{self.repo_full_name}/pipeline/{pipeline_number}"
        )

        print(f"Lab CI pipeline triggered: {pipeline_url}")
        return pipeline_url