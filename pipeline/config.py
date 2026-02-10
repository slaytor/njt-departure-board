import os
from pydantic_settings import BaseSettings

# --- Streamlit Cloud Compatibility ---
# When running on Streamlit Cloud, variables are stored in st.secrets.
# Pydantic BaseSettings reads from os.environ.
# We inject secrets into os.environ before the Settings class is instantiated.
try:
    import streamlit as st
    # Check if we are actually in a Streamlit context and have secrets
    if hasattr(st, "secrets"):
        # We iterate through common keys. You might need to adjust this if your
        # secrets.toml structure is nested (e.g. [db] url = ...).
        # This assumes top-level keys like NJT_USERNAME="foo"
        target_keys = ["NJT_USERNAME", "NJT_PASSWORD", "DATABASE_URL"]
        
        for key in target_keys:
            # If the key exists in secrets and NOT in os.environ (or we want to overwrite), set it.
            # We convert to string to be safe.
            if key in st.secrets:
                os.environ[key] = str(st.secrets[key])
except ImportError:
    # Streamlit is not installed or we are running in a different context (e.g. GitHub Actions)
    pass


class Settings(BaseSettings):
    njt_username: str
    njt_password: str
    database_url: str

    class Config:
        env_file = ".env"


settings = Settings()
