from yo_fluq import Query
from config import Repository
from requests import Response, get
from math import ceil
from typing import Tuple
import logging


class _CachePager:
    def __init__(self, repo: Repository, token: str):
        self.repo: Repository = repo
        self.token: str = token
        self.per_page: int = 100

    def _getResponse(self, url: str) -> Response:
        headers = {"Authorization": f"Bearer {self.token}"}
        return get(url, headers=headers)

    def __call__(self, page: int) -> Tuple[int, list]:
        endpoint = f"https://api.github.com/repos/{self.repo.org}\
            /{self.repo.name}/actions/caches?per_page={self.per_page}&page={page}"
        response = self._getResponse(endpoint)
        logging.info(
            f"repo: {self.repo.org}/{self.repo.name}, page: {page}, response code: {response.status_code}"
        )
        return page, response.json()["actions_caches"]

    def getPagesCount(self) -> int:
        endpoint = f"https://api.github.com/repos/{self.repo.org}/\
            {self.repo.name}/actions/caches?per_page=0"
        response = self._getResponse(endpoint)
        logging.info(
            f"repo: {self.repo.org}/{self.repo.name}, get pages count, response code: {response.status_code}"
        )
        caches_count = int(response.json()["total_count"])
        pages_count = ceil(caches_count / self.per_page)
        return pages_count


def listActionsCachesForRepository(repo: Repository, token: str) -> dict:
    pager = _CachePager(repo, token)
    actions_caches = (
        Query.loop(1, 1, pager.getPagesCount() + 1)
        # .parallel_select(pager) # Unfortunately uses multiprocesses instead of threads
        .select(pager)
        .select_many(lambda p: p[1])
        .to_list()
    )
    return {"actions_caches": actions_caches}
