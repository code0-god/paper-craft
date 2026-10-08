import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { appendFileSync, existsSync, mkdirSync, mkdtempSync, readFileSync, realpathSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';

const repository = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const cli = join(repository, 'bin/paper-craft.mjs');
const native = {
  codex: ['.agents/skills', '.agents/skills'], claude: ['.claude/skills', '.claude/skills'],
  gemini: ['.gemini/skills', '.gemini/skills'], cursor: ['.cursor/skills', '.cursor/skills'],
  copilot: ['.github/skills', '.copilot/skills'], opencode: ['.opencode/skills', '.config/opencode/skills'],
  windsurf: ['.windsurf/skills', '.codeium/windsurf/skills'], devin: ['.devin/skills', '.config/devin/skills'],
  generic: ['.agents/skills', '.agents/skills'],
};

function sandbox(t) {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'paper-craft agents ')));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  return root;
}

function run(root, args) {
  const env = { ...process.env, HOME: root, USERPROFILE: root, PYTHONDONTWRITEBYTECODE: '1' };
  delete env.PAPER_CRAFT_PYTHON;
  const result = spawnSync(process.execPath, [cli, ...args], {
    cwd: root, env,
    encoding: 'utf8', timeout: 60_000,
  });
  if (process.env.PAPER_CRAFT_TEST_LOG) appendFileSync(process.env.PAPER_CRAFT_TEST_LOG,
    JSON.stringify({ command: process.execPath, args: [cli, ...args], cwd: root,
      status: result.status, stdout: result.stdout, stderr: result.stderr }) + '\n');
  assert.ifError(result.error);
  return result;
}

for (const [agent, paths] of Object.entries(native)) {
  for (const [index, scope] of ['--project', '--user'].entries()) {
    test(`${agent} ${scope} installs canonical payload with the legacy report`, t => {
      const root = sandbox(t);
      const result = run(root, ['install', '--agent', agent, scope]);
      assert.equal(result.status, 0, result.stdout + result.stderr);
      const report = JSON.parse(result.stdout);
      const destination = join(root, paths[index], 'paper-craft');
      assert.equal(report.destination, destination);
      assert.equal(report.backup, null);
      assert.equal(report.status, 'PASS');
      assert.equal(readFileSync(join(destination, 'SKILL.md'), 'utf8'),
        readFileSync(join(repository, '.agents/skills/paper-craft/SKILL.md'), 'utf8'));
    });
  }
}

test('agent input errors fail before Python or filesystem mutation', t => {
  const root = sandbox(t);
  for (const args of [
    ['--agent', 'unknown'], ['--agent', 'constructor'], ['--agent', ''], ['--agent'],
    ['--agent', 'all', '--destination', join(root, 'paper-craft')],
    ['--agent', 'claude', '--user', '--project'],
  ]) {
    const result = run(root, [...args, '--python', 'missing-python']);
    assert.equal(result.status, 2);
    assert.doesNotMatch(result.stderr, /Cannot run/);
    for (const [project, user] of Object.values(native)) {
      assert.equal(existsSync(join(root, project)), false);
      assert.equal(existsSync(join(root, user)), false);
    }
  }
});

for (const agent of ['generic', 'claude']) {
  test(`${agent} accepts a manual full destination instead of its discovery path`, t => {
    const root = sandbox(t);
    const destination = join(root, 'manual location/paper-craft');
    const result = run(root, ['--agent', agent, '--destination', destination]);
    assert.equal(result.status, 0, result.stdout + result.stderr);
    assert.equal(JSON.parse(result.stdout).destination, destination);
    assert.equal(existsSync(join(destination, 'SKILL.md')), true);
    assert.equal(existsSync(join(root, native[agent][1])), false);
  });
}

test('all targets update preserves every original file outside discovery directories', t => {
  const root = sandbox(t);
  const first = run(root, ['--agent', 'all', '--user']);
  assert.equal(first.status, 0, first.stdout + first.stderr);
  const targets = JSON.parse(first.stdout).targets;
  assert.equal(targets.length, 8);
  for (const target of targets) writeFileSync(join(target.destination, 'local.txt'), target.destination);
  const updated = run(root, ['update', '--agent', 'all', '--user']);
  assert.equal(updated.status, 0, updated.stdout + updated.stderr);
  const report = JSON.parse(updated.stdout);
  assert.equal(report.targets.length, 8);
  for (const target of report.targets) {
    assert.equal(readFileSync(join(target.backup, 'local.txt'), 'utf8'), target.destination);
    assert.equal(target.backup.startsWith(dirname(target.destination) + sep), false);
    assert.equal(existsSync(join(target.destination, 'SKILL.md')), true);
  }
});

for (const conflict of ['existing', 'file', 'symlink', 'parent-file', 'backup-file']) {
  test(`all preflights ${conflict} before touching any earlier target`, t => {
    const root = sandbox(t);
    const lateParent = join(root, '.devin/skills');
    const late = join(lateParent, 'paper-craft');
    mkdirSync(lateParent, { recursive: true });
    if (conflict === 'existing' || conflict === 'backup-file') {
      mkdirSync(late);
      writeFileSync(join(late, 'local.txt'), 'irreplaceable');
    } else if (conflict === 'file') writeFileSync(late, 'irreplaceable');
    else if (conflict === 'symlink') {
      try {
        symlinkSync(join(root, 'absent'), late);
      } catch (error) {
        if (process.platform !== 'win32' || error.code !== 'EPERM') throw error;
        t.skip('Windows does not grant this process symbolic-link privileges');
        return;
      }
    }
    else {
      rmSync(lateParent, { recursive: true });
      writeFileSync(lateParent, 'irreplaceable');
    }
    if (conflict === 'backup-file') writeFileSync(join(root, '.devin/paper-craft-backups'), 'blocked');
    const result = run(root, [conflict === 'existing' ? 'install' : 'update', '--agent', 'all', '--project']);
    assert.equal(result.status, 2, result.stdout + result.stderr);
    const report = JSON.parse(result.stdout);
    assert.equal(report.status, 'FAIL');
    assert.deepEqual(report.completed, []);
    assert.equal(existsSync(join(root, '.agents')), false);
    if (conflict === 'existing' || conflict === 'backup-file') {
      assert.equal(readFileSync(join(late, 'local.txt'), 'utf8'), 'irreplaceable');
    }
  });
}

test('all deduplicates physical paths reached through an existing parent alias', t => {
  const root = sandbox(t);
  mkdirSync(join(root, '.agents'));
  symlinkSync(join(root, '.agents'), join(root, '.claude'), 'junction');
  const result = run(root, ['--agent', 'all', '--project']);
  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.equal(JSON.parse(result.stdout).targets.length, 7);
  assert.equal(existsSync(join(root, '.claude/skills/paper-craft/SKILL.md')), true);
});
