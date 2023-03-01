from collections import namedtuple
from prometheus_client.core import GaugeMetricFamily, Metric
from typing import Callable, Iterator
from yo_fluq import Query
from config import Repository, AppSettings
import json
import re


class GitHubCacheMetricsCollector(object):
    def __init__(
        self,
        repo: Repository,
        get_github_raw_statistics: Callable[[Repository], dict],
        settings: AppSettings,
    ):
        self.get_github_raw_statistics: Callable[
            [Repository], dict
        ] = get_github_raw_statistics
        self.repo: Repository = repo
        self.settings: AppSettings = settings

    def collect(self) -> Iterator[Metric]:
        stat_size_and_count_by_branch = (
            Query.en(self.get_github_raw_statistics(self.repo)["actions_caches"])
            .select(lambda d: namedtuple("CacheInfoRaw", d.keys())(*d.values()))
            .select(
                lambda c: namedtuple(
                    "CacheInfoEnriched",
                    "id, key, ref, size_in_bytes, branchPattern, keyPattern",
                )(
                    c.id,
                    c.key,
                    c.ref,
                    int(c.size_in_bytes),
                    next(
                        (
                            bp.pattern
                            for bp in self.settings.branch_patterns
                            if re.search(bp.rx, c.ref)
                        ),
                        c.ref,
                    ),
                    next(
                        (
                            kp.pattern
                            for kp in self.settings.key_patterns
                            if re.search(kp.rx, c.key)
                        ),
                        c.key,
                    ),
                )
            )
            .group_by(
                lambda c: namedtuple("BranchKeyPair", "branchPattern, keyPattern")(
                    c.branchPattern, c.keyPattern
                )
            )
            .select(
                lambda g: namedtuple(
                    "Statistics", "branch, key, caches_size, caches_count"
                )(
                    g.key.branchPattern,
                    g.key.keyPattern,
                    sum([c.size_in_bytes for c in g.value]),
                    len(g.value),
                )
            )
        )

        for stat in stat_size_and_count_by_branch:
            repo = f"{self.repo.org}/{self.repo.name}"
            size_gauge = GaugeMetricFamily(
                "github_caches_size", "Caches size", labels=["repo", "branch", "key"]
            )
            size_gauge.add_metric([repo, stat.branch, stat.key], stat.caches_size)
            yield size_gauge
            count_gauge = GaugeMetricFamily(
                "github_caches_count", "Caches count", labels=["repo", "branch", "key"]
            )
            count_gauge.add_metric([repo, stat.branch, stat.key], stat.caches_count)
            yield count_gauge


if __name__ == "__main__":
    repo = Repository(org="vl", name="test-repo")
    with open("test.json", "r") as f:
        collector = GitHubCacheMetricsCollector(
            repo, lambda _: json.load(f), AppSettings()
        )
        for metric in collector.collect():
            print(metric)
