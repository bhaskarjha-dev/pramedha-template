"""
Shared YAML utilities for resume cascade engine (assemble.py, sync.py).
Provides order-preserving YAML dumping, multiline string formatting,
and RenderCV-compatible representations.
"""

from pathlib import Path
import yaml


class OrderedDumper(yaml.SafeDumper):
    """Dump YAML preserving insertion order."""
    pass


def _dict_representer(dumper, data):
    return dumper.represent_mapping(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, data.items())


def _str_representer(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    if len(data) > 80:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)


class PresentLiteral(str):
    """Marker class for the bare word 'present' in RenderCV YAML output."""
    pass


def _present_literal_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', str(data), style='')


OrderedDumper.add_representer(dict, _dict_representer)
OrderedDumper.add_representer(str, _str_representer)
OrderedDumper.add_representer(PresentLiteral, _present_literal_representer)


def load_yaml(path: Path) -> dict:
    """Load a YAML file, returning its contents as a dict (or empty dict if missing/empty)."""
    if not path.exists():
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def dump_yaml(data: dict, path: Path, header: str | None = None):
    """Write a dict to a YAML file with clean formatting and optional header."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        if header:
            f.write(header)
            if not header.endswith('\n'):
                f.write('\n')
        yaml.dump(data, f, Dumper=OrderedDumper, default_flow_style=False,
                  allow_unicode=True, width=200, sort_keys=False)
