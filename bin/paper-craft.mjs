#!/usr/bin/env node
import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';

const packageRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const help = `Usage: paper-craft [install|update] [options]

Install the bundled Skill into ~/.agents/skills/paper-craft by default.
Update copies this package version and preserves the previous directory.

  --user                Install for the current user (default)
  --project             Install into cwd/.agents/skills/paper-craft
  --destination PATH    Full target directory, named paper-craft
  --python EXECUTABLE   Python 3.10+ (or PAPER_CRAFT_PYTHON environment variable)
  -h, --help            Show help without installing
  -v, --version         Show package version

Use npx @code0-god/paper-craft@latest update for the latest published payload.
No installation lifecycle hooks or manuscript uploads are used.`;

function main() {
  const { values, positionals } = parseArgs({
    allowPositionals: true,
    options: {
      user: { type: 'boolean' },
      project: { type: 'boolean' },
      destination: { type: 'string' },
      python: { type: 'string' },
      help: { type: 'boolean', short: 'h' },
      version: { type: 'boolean', short: 'v' },
    },
  });
  if (values.help) {
    console.log(help);
    return 0;
  }
  if (values.version) {
    console.log(JSON.parse(readFileSync(join(packageRoot, 'package.json'), 'utf8')).version);
    return 0;
  }
  const command = positionals[0] ?? 'install';
  if (positionals.length > 1 || !['install', 'update'].includes(command)) {
    throw new Error('Expected install or update; use --help for usage.');
  }
  if ([values.user, values.project, values.destination !== undefined].filter(Boolean).length > 1) {
    throw new Error('Choose only one of --user, --project, or --destination.');
  }
  if (values.destination === '' || values.python === '') {
    throw new Error('--destination and --python must not be empty.');
  }
  const destination = values.destination ?? join(
    values.project ? process.cwd() : homedir(), '.agents', 'skills', 'paper-craft',
  );
  const python = values.python ?? process.env.PAPER_CRAFT_PYTHON ?? (
    process.platform === 'win32' ? 'python' : 'python3'
  );
  const probe = spawnSync(python, ['-c', 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 2)'], {
    encoding: 'utf8',
  });
  if (probe.error) {
    throw new Error(`Cannot run ${python}: ${probe.error.message}. Python 3.10+ is required.`);
  }
  if (probe.status !== 0) {
    throw new Error('Python 3.10+ is required; set --python or PAPER_CRAFT_PYTHON.');
  }
  const args = [join(packageRoot, '.agents', 'skills', 'paper-craft', 'scripts', 'install_skill.py'),
    '--destination', destination];
  if (command === 'update') args.push('--update');
  const result = spawnSync(python, args, { stdio: 'inherit' });
  if (result.error) throw result.error;
  if (result.signal) throw new Error(`Installer interrupted by ${result.signal}.`);
  return result.status ?? 2;
}

try {
  process.exitCode = main();
} catch (error) {
  if (!(error instanceof Error)) throw error;
  console.error(`paper-craft: ${error.message}`);
  process.exitCode = 2;
}
