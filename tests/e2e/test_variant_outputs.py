"""HIGH-02: every variant gets its own output file inside generated/, and template placeholders never ship."""
from _profile import dump, load, make_repo, out, run

PLACEHOLDER = ('Write a 2-3 line summary tailored to this specific role. '
               'Reference skills and experience most relevant to this variant.')


def set_field(repo, filename, key, value):
    path = repo / 'tools/resume/variants' / filename
    variant = load(path)
    variant[key] = value
    dump(variant, path)


def test_two_variants_copied_from_the_template_get_two_files(tmp_path):
    repo = make_repo(tmp_path, keep_template_output_name=True)
    proc = run(repo, 'tools/resume/assemble.py')
    assert proc.returncode == 0, out(proc)
    files = sorted(p.name for p in (repo / 'tools/resume/generated').glob('*.yaml'))
    assert files == ['Alex_Chen_Backend_CV.yaml', 'Alex_Chen_Platform_CV.yaml'], files


def test_colliding_output_names_are_refused_before_writing(tmp_path):
    repo = make_repo(tmp_path)
    for filename in ('A_Backend.yaml', 'B_Platform.yaml'):
        set_field(repo, filename, 'output_filename', 'Same_CV')
    proc = run(repo, 'tools/resume/assemble.py')
    assert proc.returncode == 1, out(proc)
    assert 'Same_CV' in out(proc)
    assert not (repo / 'tools/resume/generated/Same_CV.yaml').exists()


def test_output_name_cannot_leave_generated(tmp_path):
    repo = make_repo(tmp_path)
    before = (repo / 'identity/experience.yaml').read_bytes()
    set_field(repo, 'A_Backend.yaml', 'output_filename', '../../../identity/experience')
    proc = run(repo, 'tools/resume/assemble.py', '--variant', 'A')
    assert proc.returncode == 1, out(proc)
    assert (repo / 'identity/experience.yaml').read_bytes() == before


def test_template_placeholder_summary_is_refused(tmp_path):
    repo = make_repo(tmp_path)
    set_field(repo, 'A_Backend.yaml', 'summary', PLACEHOLDER)
    proc = run(repo, 'tools/resume/assemble.py', '--variant', 'A', '--validate')
    assert proc.returncode == 1, out(proc)
    assert 'placeholder' in out(proc).lower()


def test_name_with_an_apostrophe_gives_a_safe_default_file_name(tmp_path):
    repo = make_repo(tmp_path, keep_template_output_name=True)
    config = load(repo / 'config.yaml')
    config['user']['name'] = "Dana O'Brien"
    dump(config, repo / 'config.yaml')
    ident = repo / 'identity/identity.yaml'
    ident.write_text(ident.read_text(encoding='utf-8').replace('name: "Alex Chen"', 'name: "Dana O\'Brien"'),
                     encoding='utf-8')
    proc = run(repo, 'tools/resume/assemble.py', '--variant', 'A')
    assert proc.returncode == 0, out(proc)
    assert (repo / 'tools/resume/generated/Dana_O_Brien_Backend_CV.yaml').exists(), out(proc)


def test_variant_section_order_omits_unlisted_sections_in_generated_file(tmp_path):
    repo = make_repo(tmp_path)
    set_field(repo, 'A_Backend.yaml', 'section_order', ['summary', 'experience'])
    proc = run(repo, 'tools/resume/assemble.py', '--variant', 'A')
    assert proc.returncode == 0, out(proc)
    generated = load(repo / 'tools/resume/generated/Alex_Chen_Backend_CV.yaml')
    sections = generated['cv']['sections']
    assert 'summary' in sections
    assert 'experience' in sections
    assert 'projects' not in sections
    assert 'technologies' not in sections
    assert 'education' not in sections


def test_variant_technologies_empty_list_suppresses_technologies(tmp_path):
    repo = make_repo(tmp_path)
    set_field(repo, 'A_Backend.yaml', 'technologies', [])
    proc = run(repo, 'tools/resume/assemble.py', '--variant', 'A')
    assert proc.returncode == 0, out(proc)
    generated = load(repo / 'tools/resume/generated/Alex_Chen_Backend_CV.yaml')
    sections = generated['cv']['sections']
    assert 'technologies' not in sections
    assert 'education' in sections

