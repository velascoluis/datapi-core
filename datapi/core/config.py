import yaml
import os
from typing import Any, Dict


class Config:
    REQUIRED_KEYS = {
        "metastore_type": {"expected_value": "POLARIS"},
        "metastore_uri": {"required": True},
        "metastore_credentials": {"required": True},
        "metastore_catalog": {"required": True},
        "deployment": {
            "required": True,
            "sub_keys": {
                "deployment_target": {"expected_value": "GCP_CLOUD_RUN"},
                "build_service": {"expected_value": "GCP_CLOUD_BUILD"},
                "project_id": {"required": True},
                "registry_url": {"required": True},
                "region": {"required": True},
            },
        },
    }

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.config_data = self._load_config()
        self._validate_config()

    def _load_config(self) -> Dict[str, Any]:
        config_path = os.path.join(self.project_path, "config.yml")
        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"config.yml not found in the project directory: {self.project_path}"
            )
        with open(config_path, "r") as config_file:
            return yaml.safe_load(config_file) or {}

    def _validate_config(self):
        """
        Validates that the configuration contains all required keys.
        Specific keys have expected values.
        Raises:
            KeyError: If a required key is missing.
            ValueError: If a key has an unexpected value.
        """
        for key, criteria in self.REQUIRED_KEYS.items():
            if key not in self.config_data:
                raise KeyError(f"Missing required key: '{key}' in config.yml")

            if isinstance(criteria, dict) and "sub_keys" in criteria:
                # Validate sub-keys within a section
                sub_section = self.config_data[key]
                for sub_key, sub_criteria in criteria["sub_keys"].items():
                    if sub_key not in sub_section:
                        raise KeyError(
                            f"Missing required key: '{key}.{sub_key}' in config.yml"
                        )
                    if "expected_value" in sub_criteria:
                        actual_value = sub_section[sub_key]
                        expected = sub_criteria["expected_value"]
                        if actual_value != expected:
                            raise ValueError(
                                f"Invalid value for '{key}.{sub_key}': "
                                f"Expected '{expected}', got '{actual_value}'"
                            )
            else:
                # Validate specific keys with expected values
                if "expected_value" in criteria:
                    actual_value = self.config_data[key]
                    expected = criteria["expected_value"]
                    if actual_value != expected:
                        raise ValueError(
                            f"Invalid value for '{key}': Expected '{expected}', got '{actual_value}'"
                        )
                elif criteria.get("required", False):
                    # Ensure the key is present (already checked)
                    pass  # No specific value to validate

    def get(self, key: str, default: Any = None) -> Any:
        return self.config_data.get(key, default)

    def get_deployment_config(self) -> Dict[str, Any]:
        return self.config_data.get("deployment", {})
