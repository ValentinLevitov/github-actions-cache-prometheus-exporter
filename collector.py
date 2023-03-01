import time
import prometheus_client as prom
import logging
from githubcachemetrics import GitHubCacheMetricsCollector
from githubapi import listActionsCachesForRepository
from config import AppSettings

if __name__ == "__main__":
    settings = AppSettings()
    logging.basicConfig(level=settings.app_log_level)

    prom.start_http_server(settings.port)

    prom.REGISTRY.unregister(prom.PROCESS_COLLECTOR)
    prom.REGISTRY.unregister(prom.PLATFORM_COLLECTOR)
    prom.REGISTRY.unregister(prom.GC_COLLECTOR)

    for repo in settings.repositories:
        collector = GitHubCacheMetricsCollector(
            repo,
            lambda r: listActionsCachesForRepository(r, settings.github_api_token),
            settings,
        )
        prom.REGISTRY.register(collector)

    while True:
        time.sleep(1)
