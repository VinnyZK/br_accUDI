from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "openudi-dev-2026"
    neo4j_database: str = "neo4j"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "info"
    app_env: str = "dev"

    # Auth
    jwt_secret_key: str = "change-me-in-production-min-32-chars!!"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    rate_limit_anon: str = "60/minute"
    rate_limit_auth: str = "300/minute"

    # CORS
    cors_origins: str = "http://localhost:3000"

    # Feature flags
    product_tier: str = "community"
    patterns_enabled: bool = False
    public_mode: bool = True
    public_allow_person: bool = False
    public_allow_entity_lookup: bool = False

    # Pattern thresholds
    pattern_split_threshold_value: float = 80000.0
    pattern_split_min_count: int = 3
    pattern_share_threshold: float = 0.6
    pattern_max_evidence_refs: int = 50
    pattern_temporal_window_years: int = Field(default=4, ge=1, le=20)
    pattern_min_contract_value: float = Field(default=100000.0, ge=0)
    pattern_min_contract_count: int = Field(default=2, ge=1)
    pattern_min_debt_value: float = Field(default=50000.0, ge=0)
    pattern_min_recurrence: int = Field(default=2, ge=1)
    pattern_min_discrepancy_ratio: float = Field(default=0.30, ge=0, le=1)

    # Municipality
    city_name: str = "Uberlândia"
    city_code: str = "3170206"
    city_uf: str = "MG"

    model_config = {"env_prefix": "", "env_file": ".env"}


settings = Settings()
