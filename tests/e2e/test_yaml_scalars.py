"""
Harness H5: test_yaml_scalars.py
Verifies that unquoted YAML scalars (integers, floats, dates, booleans)
in identity files and config files do not crash validate.py or sync.py,
and are cleanly coerced into strings.
"""

import sys
import datetime
from pathlib import Path
import pytest
import yaml

from tests.e2e._profile import make_repo, run, load, dump


def test_validate_and_sync_with_non_string_scalars(tmp_path: Path):
    repo = make_repo(tmp_path, variants=False)

    # 1. Write non-string scalars to config.yaml
    config_path = repo / "config.yaml"
    config_data = {
        "schema_version": "0.1.0",
        "profession_type": "engineering",
        "career_type": "employed",
        "target_role_level": "senior",
        "user": {
            "name": 12345,  # integer name
            "email": "dev@example.com",
        }
    }
    dump(config_data, config_path)

    # 2. Write non-string scalars into identity/experience.yaml
    exp_path = repo / "identity" / "experience.yaml"
    exp_data = {
        "last_updated": datetime.date(2025, 1, 1),
        "experience": [
            {
                "company": 9999,  # integer company
                "position": "Senior Engineer",
                "start_date": datetime.date(2022, 1, 1),
                "end_date": datetime.date(2024, 1, 1),
                "location": 10001,  # zip as int
                "employment_type": "full-time",
                "location_type": "remote",
                "verification": True,  # boolean verification
                "projects": [
                    {
                        "name": "Project Alpha",
                        "deliverables": [
                            {
                                "description": "Shipped system",
                                "skills": ["python", 42],
                            }
                        ]
                    }
                ]
            }
        ],
        "career_breaks": [
            {
                "title": 404,
                "type": "transition",
                "start_date": datetime.date(2021, 6, 1),
                "end_date": datetime.date(2021, 12, 1),
            }
        ]
    }
    dump(exp_data, exp_path)

    # 3. Write credentials with int/float/date/bool scalars
    creds_path = repo / "identity" / "credentials.yaml"
    creds_data = {
        "education": [
            {
                "institution": 777,
                "degree": "B.S.",
                "field": "CS",
                "start_date": datetime.date(2018, 9, 1),
                "end_date": datetime.date(2022, 6, 1),
                "gpa": 3.9,  # float
                "score": 95,  # int
                "honors": ["Summa Cum Laude", 1],
                "courses": ["Algorithms", 101],
            }
        ],
        "awards": [
            {
                "title": "Top Performer",
                "awarder": "Tech Corp",
                "year": 2023,  # integer year
                "details": 100,
            }
        ],
        "certifications": [
            {
                "name": "AWS Certified",
                "issuer": "Amazon",
                "year": 2024,
            }
        ],
        "licenses": [
            {
                "name": "PE License",
                "jurisdiction": "CA",
                "license_number": 123456,
                "status": "Active",
            }
        ],
        "clearances": [
            {
                "level": "Secret",
                "agency": "DoD",
                "status": "Active",
                "polygraph": False,
            }
        ],
        "patents": [
            {
                "title": "Distributed Caching System",
                "patent_number": 9876543,
                "filing_date": datetime.date(2023, 5, 1),
                "status": "Granted",
            }
        ],
        "grants": [
            {
                "title": "Quantum Research",
                "funder": "NSF",
                "amount": 50000,
                "year": 2022,
            }
        ],
        "publications": [
            {
                "title": "Distributed State Synchronization",
                "authors": ["Author One", 2],
                "year": 2023,
                "venue": "IEEE",
                "doi": 10.1000,
            }
        ]
    }
    dump(creds_data, creds_path)

    # 4. Write projects with non-string scalars
    proj_path = repo / "identity" / "projects.yaml"
    proj_data = {
        "public": [
            {
                "name": 10101,  # int project name
                "start_date": datetime.date(2023, 1, 1),
                "end_date": datetime.date(2023, 6, 1),
                "highlights": [
                    "First highlight",
                    12345,  # integer highlight
                ],
                "tech": ["python", 3.12],
            }
        ]
    }
    dump(proj_data, proj_path)

    # 5. Run validate.py --status via python CLI
    val_res = run(repo, ".pramedha/validate.py", "--status")
    assert val_res.returncode == 0, f"validate.py failed: {val_res.stderr}\n{val_res.stdout}"

    # 6. Run sync.py via python CLI
    sync_res = run(repo, "tools/resume/sync.py", "--force")
    assert sync_res.returncode == 0, f"sync.py failed: {sync_res.stderr}\n{sync_res.stdout}"

    # 7. Check that master.yaml parses and contains string keys/values
    master_path = repo / "tools" / "resume" / "master.yaml"
    master = load(master_path)

    assert isinstance(master, dict)
    assert "experience" in master
    assert "projects" in master
    assert "education" in master
    assert "achievements" in master
