import { homedir } from 'node:os';
import { join } from 'node:path';

// Each pair is the documented project and user skill discovery directory.
export const agentTargets = {
  codex: ['.agents/skills', '.agents/skills'],
  claude: ['.claude/skills', '.claude/skills'],
  gemini: ['.gemini/skills', '.gemini/skills'],
  cursor: ['.cursor/skills', '.cursor/skills'],
  copilot: ['.github/skills', '.copilot/skills'],
  opencode: ['.opencode/skills', '.config/opencode/skills'],
  windsurf: ['.windsurf/skills', '.codeium/windsurf/skills'],
  devin: ['.devin/skills', '.config/devin/skills'],
  generic: ['.agents/skills', '.agents/skills'],
};

export function destinations(agent, project) {
  if (agent !== 'all' && !Object.hasOwn(agentTargets, agent)) {
    throw new Error(`Unknown agent: ${agent}. Choose ${Object.keys(agentTargets).join(', ')}, or all.`);
  }
  const selected = agent === 'all' ? Object.keys(agentTargets).filter(name => name !== 'generic') : [agent];
  return [...new Set(selected.map(name => join(
    project ? process.cwd() : homedir(), agentTargets[name][project ? 0 : 1], 'paper-craft',
  )))];
}
