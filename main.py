from typing import List
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS: lets the grader's web page call your API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- The four layers (low -> high precedence) ----
DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": "false",
    "log_level": "info",
    "api_key": "default-secret-000",
}

YAML_LAYER = {"workers": 15}  # config.development.yaml

DOTENV_LAYER = {              # .env file
    "APP_DEBUG": "false",
    "APP_API_KEY": "key-cxqy4o2bd5",
}

OS_ENV_LAYER = {              # OS environment variables
    "APP_PORT": "8434",
    "APP_DEBUG": "false",
    "APP_LOG_LEVEL": "warning",
    "APP_API_KEY": "key-741wstt8l6",
}

ALIASES = {"num_workers": "workers"}


def normalize(raw: dict) -> dict:
    """Turn APP_LOG_LEVEL -> log_level, NUM_WORKERS -> workers, etc."""
    out = {}
    for key, value in raw.items():
        key = key.lower()
        if key.startswith("app_"):
            key = key[4:]
        key = ALIASES.get(key, key)
        out[key] = value
    return out


def coerce(key: str, value):
    """Convert each value to the right type."""
    if key in ("port", "workers"):
        return int(value)
    if key == "debug":
        return str(value).strip().lower() in ("true", "1", "yes", "on")
    return str(value)


@app.get("/effective-config")
def effective_config(set: List[str] = Query(default=[])):
    config = {}
    # Later layers overwrite earlier ones
    for layer in (DEFAULTS, YAML_LAYER, DOTENV_LAYER, OS_ENV_LAYER):
        config.update(normalize(layer))

    # CLI overrides: "port=9000" -> key "port", value "9000"
    for item in set:
        if "=" in item:
            key, value = item.split("=", 1)
            config.update(normalize({key.strip(): value.strip()}))

    result = {k: coerce(k, v) for k, v in config.items()}
    result["api_key"] = "****"  # never reveal the secret
    return result