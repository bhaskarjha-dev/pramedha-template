"""
Unit tests for Pramedha resume cascade and build tooling:
- tools/resume/_yaml_utils.py
- tools/resume/sync.py
- tools/resume/assemble.py
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

from tools.resume._yaml_utils import (
    OrderedDumper,
    PresentLiteral,
    dump_yaml as base_dump_yaml,
    load_yaml,
)
from tools.resume.sync import (
    slugify,
    generate_role_key,
    generate_project_key,
    generate_bullet_key,
    generate_achievement_key,
    sync_experience,
    sync_achievements,
)
from tools.resume.assemble import (
    clean_bullet_tags,
    resolve_bullet,
    AssemblyError,
    assemble_variant,
)


# ============================================================================
# 1. YAML Utils Tests
# ============================================================================

class TestYamlUtils:
    def test_ordered_dumper_preserves_key_order(self, tmp_path):
        data = {
            "zebra": 1,
            "apple": 2,
            "mango": 3,
            "banana": 4,
        }
        test_file = tmp_path / "order_test.yaml"
        base_dump_yaml(data, test_file)

        content = test_file.read_text(encoding="utf-8")
        lines = [line.split(":")[0].strip() for line in content.strip().splitlines() if ":" in line]
        assert lines == ["zebra", "apple", "mango", "banana"]

    def test_present_literal_representation(self, tmp_path):
        data = {
            "end_date": PresentLiteral("present")
        }
        test_file = tmp_path / "literal_test.yaml"
        base_dump_yaml(data, test_file)

        content = test_file.read_text(encoding="utf-8")
        assert "end_date: present" in content

    def test_multiline_string_representation(self, tmp_path):
        data = {
            "description": "line 1\nline 2\nline 3"
        }
        test_file = tmp_path / "multiline_test.yaml"
        base_dump_yaml(data, test_file)

        content = test_file.read_text(encoding="utf-8")
        assert "description: |" in content
        assert "line 1" in content

    def test_load_yaml_missing_file_returns_empty_dict(self, tmp_path):
        missing_file = tmp_path / "does_not_exist.yaml"
        assert load_yaml(missing_file) == {}

    def test_load_and_dump_yaml_roundtrip(self, tmp_path):
        data = {"name": "Test User", "skills": ["Python", "Go"]}
        test_file = tmp_path / "roundtrip.yaml"
        base_dump_yaml(data, test_file, header="# Test Header")

        loaded = load_yaml(test_file)
        assert loaded == data
        assert "# Test Header" in test_file.read_text(encoding="utf-8")


# ============================================================================
# 2. Sync Engine Helper & Pruning Tests
# ============================================================================

class TestSyncHelpers:
    def test_slugify(self):
        assert slugify("Acme Cloud Platform") == "acme_cloud_platform"
        assert slugify("  Forward Deployed Engineer  ") == "forward_deployed_engineer"
        assert slugify("C++ & Python / Go!") == "c_python_go"
        assert slugify("") == ""
        assert slugify(None) == ""

    def test_generate_role_key_uniqueness(self):
        existing = set()
        key1 = generate_role_key("Acme Corporation", "Systems Engineer", existing)
        existing.add(key1)
        assert key1 == "acme_corporation_systems_engineer"

        key2 = generate_role_key("Acme Corporation", "Systems Engineer", existing)
        existing.add(key2)
        assert key2 == "acme_corporation_systems_engineer_2"

        key3 = generate_role_key("Acme Corporation", "Systems Engineer", existing)
        assert key3 == "acme_corporation_systems_engineer_3"

    def test_generate_project_key(self):
        existing = {"project_alpha"}
        key = generate_project_key("Project Alpha", existing)
        assert key == "project_alpha_2"

        key_new = generate_project_key("Telemetry Engine", existing)
        assert key_new == "telemetry_engine"

    def test_generate_bullet_key_filters_stopwords_and_tags(self):
        existing = set()
        text = "[measured] Engineered a high-throughput data pipeline with 99.9% uptime"
        key = generate_bullet_key(text, existing)
        assert key == "engineered_high_throughput"

    def test_generate_achievement_key_with_prefix(self):
        existing = {"hackathon_challenge_2023"}
        key = generate_achievement_key("Challenge 2023", existing, prefix="hackathon")
        assert key == "hackathon_challenge_2023_2"

        key_first = generate_achievement_key("Global Challenge", existing, prefix="hackathon")
        assert key_first == "hackathon_global_challenge"

    def test_sync_experience_prunes_example_role(self):
        id_data = {
            "experience": [
                {
                    "company": "Globex Corp",
                    "position": "Staff Platform Engineer",
                    "start_date": "2024-03",
                    "end_date": "present",
                    "projects": [
                        {
                            "name": "Event Bus Pipeline",
                            "deliverables": [
                                {"bullets": ["Engineered distributed event streaming broker"]}
                            ]
                        }
                    ]
                }
            ]
        }
        master_data = {
            "experience": {
                "_example_role_": {
                    "company": "Acme Corp",
                    "position": "Software Engineer",
                    "bullets": {"sample": "Did sample work"}
                }
            }
        }

        sync_experience(id_data, master_data, force=False)

        # _example_role_ must be pruned when real entries exist
        assert "_example_role_" not in master_data["experience"]
        # Real role must be present
        assert any("globex" in k for k in master_data["experience"].keys())

    def test_sync_experience_keeps_example_role_if_no_real_entries(self):
        id_data = {"experience": []}
        master_data = {
            "experience": {
                "_example_role_": {
                    "company": "Acme Corp",
                    "position": "Software Engineer"
                }
            }
        }

        sync_experience(id_data, master_data, force=False)
        assert "_example_role_" in master_data["experience"]

    def test_sync_achievements_speaking_and_volunteering(self):
        creds_data = {}
        community_data = {
            "speaking": [
                {
                    "title": "Scaling Distributed Systems",
                    "event": "PyCon",
                    "date": "2024-04",
                    "role": "Keynote Speaker"
                }
            ]
        }
        vol_data = {
            "volunteering": [
                {
                    "organization": "Open Source Initiative",
                    "role": "Maintainer",
                    "cause": "Open Source"
                }
            ]
        }
        master_data = {}
        stats = sync_achievements(creds_data, community_data, master_data, vol_data=vol_data)
        assert stats["added"] == 2
        assert "talk_scaling_distributed_systems" in master_data["achievements"]
        assert "Spoke at PyCon" in master_data["achievements"]["talk_scaling_distributed_systems"]["text"]
        assert "volunteer_open_source_initiative" in master_data["achievements"]
        assert "Maintainer at Open Source Initiative" in master_data["achievements"]["volunteer_open_source_initiative"]["text"]


# ============================================================================
# 3. Assembler Engine Tests
# ============================================================================

class TestAssembleHelpers:
    def test_clean_bullet_tags(self):
        # Verification bracketed tags
        assert clean_bullet_tags("[measured] Achieved 40% latency reduction.") == "Achieved 40% latency reduction."
        assert clean_bullet_tags("[estimated: 15%] Scaled data pipeline.") == "Scaled data pipeline."
        assert clean_bullet_tags("[to-verify] Verified throughput.") == "Verified throughput."
        assert clean_bullet_tags("[partially-verified] Migrated 10 services.") == "Migrated 10 services."

        # Verification emojis
        assert clean_bullet_tags("✅ Authored Go CLI tool.") == "Authored Go CLI tool."
        assert clean_bullet_tags("⚠️ Refactored legacy batch job.") == "Refactored legacy batch job."
        assert clean_bullet_tags("❌ Deprecated endpoint.") == "Deprecated endpoint."

        # Edge cases
        assert clean_bullet_tags("") == ""
        assert clean_bullet_tags(None) == ""

    def test_resolve_bullet_string_and_list_phrasings(self):
        master_exp = {
            "bullets": {
                "bullet_latency": "Reduced p95 latency from 450ms to 85ms across 12 services.",
                "bullet_pipeline": {
                    "default": "Built real-time streaming pipeline processing 2M events/sec.",
                    "concise": "Built streaming pipeline processing 2M events/sec.",
                    "metric_first": "Processed 2M events/sec by building real-time streaming pipeline."
                }
            }
        }

        # String reference
        text1 = resolve_bullet(master_exp, "test_exp", "bullet_latency", "VariantA")
        assert text1 == "Reduced p95 latency from 450ms to 85ms across 12 services."

        # Dot phrasing reference
        text2 = resolve_bullet(master_exp, "test_exp", "bullet_pipeline.concise", "VariantA")
        assert text2 == "Built streaming pipeline processing 2M events/sec."

        # List reference [key, phrasing]
        text3 = resolve_bullet(master_exp, "test_exp", ["bullet_pipeline", "metric_first"], "VariantA")
        assert text3 == "Processed 2M events/sec by building real-time streaming pipeline."

    def test_resolve_bullet_missing_key_raises_assembly_error(self):
        master_exp = {
            "bullets": {
                "bullet_one": "First bullet"
            }
        }
        with pytest.raises(AssemblyError) as exc_info:
            resolve_bullet(master_exp, "test_exp", "non_existent_bullet", "VariantA")
        assert "not found in experience" in str(exc_info.value)

    def test_section_order_whitelist_omission(self):
        master = {
            "header": {"name": "Test User"},
            "experience": {},
            "technologies": [{"label": "Languages", "details": "Python"}],
            "education": [{"institution": "Test Univ", "area": "CS", "degree": "BS", "start_date": "2020", "end_date": "2024"}]
        }
        design = {"theme": "classic"}
        assembled = assemble_variant(master, design, {"variant_name": "Test", "section_order": ["education"]})
        assert "education" in assembled["cv"]["sections"]
        assert "technologies" not in assembled["cv"]["sections"]

    def test_technologies_suppression_and_override(self):
        master = {
            "header": {"name": "Test User"},
            "experience": {},
            "technologies": [{"label": "Languages", "details": "Python"}],
            "education": [{"institution": "Test Univ", "area": "CS", "degree": "BS", "start_date": "2020", "end_date": "2024"}]
        }
        design = {"theme": "classic"}

        # Empty list suppresses technologies
        suppressed = assemble_variant(master, design, {"variant_name": "Test", "technologies": []})
        assert "technologies" not in suppressed["cv"]["sections"]
        assert "education" in suppressed["cv"]["sections"]

        # Custom list overrides master
        custom = assemble_variant(master, design, {
            "variant_name": "Test",
            "technologies": [{"label": "Cloud", "details": "GCP"}]
        })
        assert custom["cv"]["sections"]["technologies"] == [{"label": "Cloud", "details": "GCP"}]

        # Omission falls back to master
        fallback = assemble_variant(master, design, {"variant_name": "Test"})
        assert fallback["cv"]["sections"]["technologies"] == [{"label": "Languages", "details": "Python"}]


# ============================================================================
# 4. Validation Date Logic Tests
# ============================================================================

class TestValidationDateChronology:
    def test_parse_flexible_date_year_only_end_date(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("validate", REPO_ROOT / ".pramedha" / "validate.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        # Start date defaults to January
        assert mod.parse_flexible_date("2024", is_end_date=False) == (2024, 1)
        # End date year-only defaults to December
        assert mod.parse_flexible_date("2024", is_end_date=True) == (2024, 12)
        # Explicit month is preserved
        assert mod.parse_flexible_date("2024-05", is_end_date=True) == (2024, 5)
