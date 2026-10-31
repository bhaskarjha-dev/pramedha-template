"""HIGH-08: a variant whose `technologies: []` or `education: []` hides a section master.yaml has says so.
Variants copied from the v0.1.0 template carry `technologies: []`, which used to mean "use master's"."""
from _profile import BACKEND, load, make_repo, out, run, write_variant


def test_empty_override_that_hides_a_master_section_is_reported(tmp_path):
    repo = make_repo(tmp_path)
    assert load(repo / 'tools/resume/master.yaml').get('technologies')
    write_variant(repo, 'C_Old.yaml', 'Old', BACKEND, technologies=[])
    proc = run(repo, 'tools/resume/assemble.py', '--variant', 'C')
    assert proc.returncode == 0, out(proc)
    assert 'technologies: []' in out(proc), out(proc)


def test_inherited_sections_build_without_the_notice(tmp_path):
    repo = make_repo(tmp_path)
    proc = run(repo, 'tools/resume/assemble.py', '--variant', 'A')
    assert proc.returncode == 0 and 'technologies: []' not in out(proc), out(proc)
    generated = load(repo / 'tools/resume/generated/Alex_Chen_Backend_CV.yaml')
    assert 'technologies' in generated['cv']['sections'], generated['cv']['sections'].keys()


def test_empty_education_override_is_reported_too(tmp_path):
    repo = make_repo(tmp_path)
    write_variant(repo, 'C_NoEdu.yaml', 'NoEdu', BACKEND, education=[])
    proc = run(repo, 'tools/resume/assemble.py', '--variant', 'C')
    assert proc.returncode == 0 and 'education: []' in out(proc) and '[NoEdu]' in out(proc), out(proc)


def test_no_notice_when_section_order_already_leaves_the_section_out(tmp_path):
    repo = make_repo(tmp_path)
    write_variant(repo, 'C_Order.yaml', 'Order', BACKEND, technologies=[],
                  section_order=['summary', 'experience', 'education'])
    proc = run(repo, 'tools/resume/assemble.py', '--variant', 'C')
    assert proc.returncode == 0 and 'technologies: []' not in out(proc), out(proc)

