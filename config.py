from pydantic import BaseModel, BaseSettings
from typing import List, Dict, Any
import yaml
import os


class Repository(BaseModel):
    org: str
    name: str


class Pattern(BaseModel):
    pattern: str
    rx: str


def yaml_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    if os.path.exists("config.yaml"):
        with open("config.yaml") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        if data is not None:
            return data
    return {}


class AppSettings(BaseSettings):
    repositories: List[Repository]  # at least 1 repo should be
    branch_patterns: List[Pattern] = []  # optional
    key_patterns: List[Pattern] = []  # optional
    github_api_token: str  # required
    port: int = 9095
    app_log_level: str = "INFO"

    class Config:
        # env_prefix = 'prometheus_exporter_'
        case_sensitive = False
        secrets_dir = "/run/secrets"  # docker-way secrets supplying support

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return (
                init_settings,
                env_settings,
                yaml_config_settings_source,
                file_secret_settings,
            )


if __name__ == "__main__":
    print(AppSettings())
