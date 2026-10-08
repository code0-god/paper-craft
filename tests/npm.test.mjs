import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { after, before, test } from 'node:test';
import {
  appendFileSync, existsSync, mkdirSync, mkdtempSync, readFileSync,
  readdirSync, rmSync, symlinkSync, writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const repository = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const manifest = JSON.parse(readFileSync(join(repository, 'package.json')));
const cli = join(repository, 'bin/paper-craft.mjs');
const temporary = mkdtempSync(join(tmpdir(), 'paper-craft npm '));
const home = join(temporary, 'isolated home');
const environment = {
  ...Object.fromEntries(Object.entries(process.env).filter(([key]) => !/^npm_config_/i.test(key))),
  HOME: home, USERPROFILE: home, PYTHONDONTWRITEBYTECODE: '1',
  npm_config_cache: join(temporary, 'npm cache'), npm_config_offline: 'true',
  npm_config_ignore_scripts: 'true', npm_config_audit: 'false', npm_config_fund: 'false',
};
delete environment.PAPER_CRAFT_PYTHON;
let tarball;
let packed;
let python;

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    cwd: temporary, env: environment, encoding: 'utf8', timeout: 60_000, ...options,
  });
  if (process.env.PAPER_CRAFT_TEST_LOG) {
    appendFileSync(process.env.PAPER_CRAFT_TEST_LOG, JSON.stringify({
      command, args, cwd: options.cwd ?? temporary, status: result.status,
      stdout: result.stdout, stderr: result.stderr, error: result.error?.message,
    }) + '\n');
  }
  assert.ifError(result.error);
  return result;
}

function successful(result) {
  assert.equal(result.status, 0, result.stdout + result.stderr);
  return result.stdout;
}

function npm(args) {
  return process.env.npm_execpath
    ? run(process.execPath, [process.env.npm_execpath, ...args])
    : run(process.platform === 'win32' ? 'npm.cmd' : 'npm', args,
      { shell: process.platform === 'win32' });
}

function tree(directory) {
  return Object.fromEntries(readdirSync(directory, { withFileTypes: true }).flatMap(entry => {
    const path = join(directory, entry.name);
    return entry.isDirectory()
      ? Object.entries(tree(path)).map(([name, data]) => [entry.name + '/' + name, data])
      : [[entry.name, readFileSync(path).toString('base64')]];
  }));
}

before(() => {
  mkdirSync(home);
  python = successful(run(process.platform === 'win32' ? 'python' : 'python3',
    ['-c', 'import sys; print(sys.executable)'])).trim();
  packed = Object.values(JSON.parse(successful(npm([
    'pack', repository, '--json', '--ignore-scripts', '--pack-destination', temporary,
  ]))))[0];
  tarball = join(temporary, packed.filename);
});
after(() => rmSync(temporary, { recursive: true, force: true }));

test('tarball contains the complete skill and only public runtime files', () => {
  const paths = packed.files.map(file => file.path).sort();
  const skill = '.agents/skills/paper-craft/';
  const sourceFiles = Object.keys(tree(join(repository, skill)))
    .filter(path => !path.split('/').includes('__pycache__') && !path.endsWith('.pyc'));
  for (const path of sourceFiles) assert.ok(paths.includes(skill + path), path);
  for (const path of paths) {
    assert.ok(path === 'package.json' || path === 'README.md' || path === 'LICENSE'
      || path === 'bin/paper-craft.mjs' || path.startsWith(skill), path);
    assert.doesNotMatch(path, /(?:__pycache__|\.pyc$|source-materials|(?:^|\/)tests\/)/);
  }
  assert.equal(manifest.name, '@code0-god/paper-craft');
  assert.equal(manifest.license, 'MIT');
  assert.ok(paths.includes('LICENSE'));
  assert.ok(paths.includes(skill + 'LICENSE'));
  assert.equal(readFileSync(join(repository, 'LICENSE'), 'utf8'),
    readFileSync(join(repository, skill, 'LICENSE'), 'utf8'));
  assert.equal(packed.version, manifest.version);
  assert.equal(manifest.bin['paper-craft'], 'bin/paper-craft.mjs');
  assert.deepEqual(manifest.dependencies ?? {}, {});
  assert.equal(manifest.scripts?.postinstall, undefined);
});

test('help and version run without Python and do not install anything', () => {
  const snapshot = tree(home);
  const env = { ...environment, PAPER_CRAFT_PYTHON: join(temporary, 'missing python') };
  assert.match(successful(run(process.execPath, [cli, '--help'], { env })), /paper-craft/);
  assert.equal(successful(run(process.execPath, [cli, '--version'], { env })).trim(), manifest.version);
  assert.deepEqual(tree(home), snapshot);
});

test('default user, explicit user, project and relative destination route correctly', () => {
  successful(run(process.execPath, [cli]));
  const destination = join(home, '.agents/skills/paper-craft');
  assert.ok(existsSync(join(destination, 'SKILL.md')));
  writeFileSync(join(destination, 'local-note.txt'), 'keep user note');
  const report = JSON.parse(successful(run(process.execPath, [cli, 'update', '--user'])));
  assert.equal(readFileSync(join(report.backup, 'local-note.txt'), 'utf8'), 'keep user note');
  assert.ok(!report.backup.startsWith(join(home, '.agents/skills') + '/'));
  successful(run(process.execPath, [cli, 'install', '--project']));
  assert.ok(existsSync(join(temporary, '.agents/skills/paper-craft/SKILL.md')));
  successful(run(process.execPath, [cli, '--destination', 'relative space/paper-craft']));
  assert.ok(existsSync(join(temporary, 'relative space/paper-craft/SKILL.md')));
});

test('argument and Python failures preserve an existing destination byte for byte', () => {
  const parent = join(temporary, 'failure targets');
  const destination = join(parent, 'paper-craft');
  mkdirSync(destination, { recursive: true });
  writeFileSync(join(destination, 'local.txt'), 'irreplaceable');
  const snapshot = tree(parent);
  for (const args of [
    ['explode'], ['--unknown'], ['--destination'], ['--python'], ['--python', '--project'],
    ['--user', '--project'], ['--project', '--destination', destination],
    ['--user', '--destination', destination],
  ]) {
    const result = run(process.execPath, [cli, ...args]);
    assert.equal(result.status, 2, JSON.stringify(args) + result.stdout + result.stderr);
    assert.deepEqual(tree(parent), snapshot);
  }
  const result = run(process.execPath, [cli, 'update', '--destination', destination,
    '--python', join(temporary, 'missing python')]);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /python/i);
  assert.doesNotMatch(result.stderr, /\n\s+at |Traceback/);
  assert.deepEqual(tree(parent), snapshot);
  const incompatible = run(process.execPath, [cli, 'update', '--destination', destination,
    '--python', process.execPath]);
  assert.notEqual(incompatible.status, 0);
  assert.match(incompatible.stderr, /python/i);
  assert.deepEqual(tree(parent), snapshot);
  const oldPython = join(temporary, 'python39');
  writeFileSync(oldPython, '#!/usr/bin/env python3\nimport sys\nsys.version_info = (3, 9, 0)\nexec(sys.argv[2])\n', { mode: 0o755 });
  const outdated = run(process.execPath, [cli, 'update', '--destination', destination, '--python', oldPython]);
  assert.equal(outdated.status, 2);
  assert.match(outdated.stderr, /3\.10/);
  assert.deepEqual(tree(parent), snapshot);
});

test('Python environment override and explicit executable paths with spaces work', () => {
  const executable = join(temporary, process.platform === 'win32' ? 'python space.exe' : 'python space');
  symlinkSync(python, executable);
  const env = { ...environment, PAPER_CRAFT_PYTHON: executable };
  successful(run(process.execPath, [cli, '--destination', join(temporary, 'env/paper-craft')], { env }));
  successful(run(process.execPath, [cli, '--python', executable,
    '--destination', join(temporary, 'override/paper-craft')],
  { env: { ...environment, PAPER_CRAFT_PYTHON: 'missing-python' } }));
});

test('local npm install ships independently usable Python resources without auto-installing', () => {
  const prefix = join(temporary, 'local npm');
  const snapshot = tree(home);
  successful(npm(['install', '--prefix', prefix, '--ignore-scripts', '--no-audit', '--no-fund', tarball]));
  assert.deepEqual(tree(home), snapshot);
  const installed = join(prefix, 'node_modules/@code0-god/paper-craft');
  const payload = join(installed, '.agents/skills/paper-craft');
  writeFileSync(join(payload, 'assets/npm-origin.txt'), 'from the installed npm package');
  const destination = join(temporary, 'independent/paper-craft');
  successful(run(process.execPath, [join(installed, 'bin/paper-craft.mjs'), '--destination', destination]));
  assert.equal(readFileSync(join(destination, 'assets/npm-origin.txt'), 'utf8'), 'from the installed npm package');
  for (const script of ['validate_skill.py', 'validate_profiles.py']) {
    const report = JSON.parse(successful(run(python, [join(destination, 'scripts', script), '--json'])));
    assert.equal(report.status, 'PASS');
  }
  const manuscript = join(temporary, 'paper.tex');
  writeFileSync(manuscript, '\\documentclass{article}\n\\begin{document}\nText.\n\\end{document}\n');
  const report = JSON.parse(successful(run(python, [join(destination, 'scripts/venue_preflight.py'),
    manuscript, '--venue', 'ISCA', '--year', '2026', '--track', 'research',
    '--stage', 'submission', '--offline', '--json'])));
  assert.ok(report.profile);
  assert.equal(report.current_rules_verified, false);
});

test('global npm executable installs and updates with the full old tree in a backup', () => {
  const prefix = join(temporary, 'global npm');
  successful(npm(['install', '--global', '--prefix', prefix, '--ignore-scripts', '--no-audit', '--no-fund', tarball]));
  const executable = process.platform === 'win32' ? process.execPath : join(prefix, 'bin/paper-craft');
  const leading = process.platform === 'win32'
    ? [join(prefix, 'node_modules/@code0-god/paper-craft/bin/paper-craft.mjs')] : [];
  const destination = join(temporary, 'global target/paper-craft');
  successful(run(executable, [...leading, 'install', '--destination', destination]));
  writeFileSync(join(destination, 'SKILL.md'), 'user-edited skill');
  writeFileSync(join(destination, 'notes.txt'), 'preserve notes');
  const snapshot = tree(destination);
  const refused = run(executable, [...leading, 'install', '--destination', destination]);
  assert.notEqual(refused.status, 0);
  assert.deepEqual(tree(destination), snapshot);
  const report = JSON.parse(successful(run(executable, [...leading, 'update', '--destination', destination])));
  assert.deepEqual(tree(report.backup), snapshot);
  assert.match(readFileSync(join(destination, 'SKILL.md'), 'utf8'), /name: paper-craft/);
  assert.equal(existsSync(join(destination, 'notes.txt')), false);
});

test('npm exec uses the local tarball without registry access', () => {
  const destination = join(temporary, 'npx target/paper-craft');
  successful(npm(['exec', '--yes', '--offline', '--ignore-scripts', '--no-audit', '--no-fund',
    '--package', tarball, '--', 'paper-craft', 'install', '--destination', destination]));
  assert.ok(existsSync(join(destination, 'SKILL.md')));
  assert.ok(existsSync(join(destination, 'scripts/install_skill.py')));
});

test('npx updates from a local tarball and preserves existing files in a backup', () => {
  const destination = join(temporary, 'real npx target/paper-craft');
  const command = process.platform === 'win32' ? 'npx.cmd' : 'npx';
  const args = ['--yes', '--offline', '--ignore-scripts', '--no-audit', '--no-fund',
    '--package', tarball, 'paper-craft', 'update', '--destination', destination];
  successful(run(command, args, { shell: process.platform === 'win32' }));
  writeFileSync(join(destination, 'npx-notes.txt'), 'preserve npx research');
  const snapshot = tree(destination);
  const report = JSON.parse(successful(run(command, args, { shell: process.platform === 'win32' })));
  assert.deepEqual(tree(report.backup), snapshot);
  assert.ok(existsSync(join(destination, 'SKILL.md')));
  assert.equal(existsSync(join(destination, 'npx-notes.txt')), false);
});
