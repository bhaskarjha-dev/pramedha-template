"""
Unit tests for repository validation:
- .pramedha/validate.py
"""

import sys
from pathlib import Path
import pytest
import yaml

# Robust dynamic repo root discovery (anchoring on config.yaml)
REPO_ROOT = Path(__file__).resolve()
while REPO_ROOT.name and not (REPO_ROOT / "config.yaml").exists():
    REPO_ROOT = REPO_ROOT.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import validator module using importlib because folder name has a dot (.pramedha)
import importlib.util
validator_path = REPO_ROOT / ".pramedha" / "validate.py"
spec = importlib.util.spec_from_file_location("pramedha_validate", str(validator_path))
pramedha_validate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pramedha_validate)

ValidationResult = pramedha_validate.ValidationResult
check_yaml_valid = pramedha_validate.check_yaml_valid
check_config = pramedha_validate.check_config
check_experience = pramedha_validate.check_experience
check_verification_tags = pramedha_validate.check_verification_tags
check_skill_enums = pramedha_validate.check_skill_enums
check_date_chronology = pramedha_validate.check_date_chronology
check_cross_file_consistency = pramedha_validate.check_cross_file_consistency


class TestPramedhaValidator:
    def test_validation_result_collector(self):
        result = ValidationResult()
        assert not result.errors
        assert not result.warnings
        assert not result.info

        result.error("Test error")
        result.warn("Test warning")
        result.note("Test note")

        assert len(result.errors) == 1
        assert len(result.warnings) == 1
        assert len(result.info) == 1

    def test_repository_yaml_syntax_validity(self):
        result = ValidationResult()
        check_yaml_valid(result)
        assert result.errors == [], f"YAML errors found: {result.errors}"

    def test_repository_experience_structure(self):
        result = ValidationResult()
        check_experience(result)
        assert result.errors == [], f"Experience errors found: {result.errors}"
