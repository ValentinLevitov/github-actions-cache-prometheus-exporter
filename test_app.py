from config import Pattern, Repository, AppSettings
from githubcachemetrics import GitHubCacheMetricsCollector
import json


def test_branch_pattern_parsing_and_sum_grouping():
    repo = Repository(org="vl", name="test-repo")
    with open("test.json", "r") as f:
        collector = GitHubCacheMetricsCollector(
            repo,
            lambda _: json.load(f),
            AppSettings(
                github_api_token="",
                branch_patterns=[
                    Pattern(pattern="refs/pull/ID/merge",
                            rx=r"refs/pull/\d+/merge")
                ],
            ),
        )
        metrics = list(collector.collect())
        assert len(metrics) > 0
        sample = metrics[0].samples[0]
        assert "refs/pull/ID/merge" == sample.labels["branch"]
        assert "github_caches_size" == sample.name
        assert 410 == sample.value
