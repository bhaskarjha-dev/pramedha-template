"""HIGH-04: agents treat repository content as data and ask before anything leaves the machine."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def text(rel):
    return (REPO / rel).read_text(encoding='utf-8')


def test_agents_md_has_the_safety_rules():
    body = text('AGENTS.md')
    assert '## Safety rules for agents' in body
    section = body.split('## Safety rules for agents', 1)[1].split('\n## ', 1)[0]
    for phrase in ('data, not instructions', 'git push', 'Ask the user'):
        assert phrase in section, phrase


def test_protocol_and_prompts_carry_the_rules():
    protocol = text('.pramedha/agent-instructions.md')
    assert 'Safety rules for agents' in protocol
    for phrase in ('data, not instructions', 'git push'):
        assert phrase in protocol, phrase  # existing copies keep their own AGENTS.md, so repeat the rules here
    prompt3 = text('ops/prompts.md').split('## 3.', 1)[1].split('## 4.', 1)[0]
    assert 'untrusted' in prompt3

