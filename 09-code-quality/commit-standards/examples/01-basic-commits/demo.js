#!/usr/bin/env node

/**
 * Example 1: Basic Commit Messages
 *
 * This demo shows how to validate basic commit messages using commitlint.
 */

const load = require('@commitlint/load').default;
const lint = require('@commitlint/lint').default;

// Example commit messages - basic types without scopes
const validCommits = [
  'feat: add user registration form',
  'fix: resolve login redirect issue',
  'docs: update readme with installation steps',
  'style: format code with prettier',
  'refactor: extract validation logic to helper',
  'test: add unit tests for user service',
  'chore: update .gitignore with ide files',
  'perf: optimize image loading',
  'build: upgrade webpack to version 5',
  'ci: add github actions workflow',
  'revert: revert "feat: add broken feature"',
];

const invalidCommits = [
  'Add new feature',           // Missing type
  'feat Add new feature',      // Missing colon
  'Feat: add new feature',     // Capitalized type
  'feat: Add new feature',     // Capitalized description
  'feat: add new feature.',    // Trailing period
  'FEAT: add new feature',     // Uppercase type
  'feature: add new feature',  // Wrong type
  'fix: ',                     // Empty description
];

async function validateCommit(message, config) {
  const result = await lint(message, config.rules, config);
  return {
    message,
    valid: result.valid,
    errors: result.errors.map(e => e.message),
    warnings: result.warnings.map(w => w.message),
  };
}

async function main() {
  console.log('='.repeat(60));
  console.log('Example 1: Basic Commit Messages');
  console.log('='.repeat(60));
  console.log();

  // Load commitlint configuration
  const config = await load({ extends: ['@commitlint/config-conventional'] });

  console.log('VALID COMMIT MESSAGES');
  console.log('-'.repeat(60));

  for (const commit of validCommits) {
    const result = await validateCommit(commit, config);
    const status = result.valid ? 'PASS' : 'FAIL';
    const icon = result.valid ? '[OK]' : '[X]';
    console.log(`${icon} ${commit}`);
    if (!result.valid) {
      result.errors.forEach(e => console.log(`    Error: ${e}`));
    }
  }

  console.log();
  console.log('INVALID COMMIT MESSAGES');
  console.log('-'.repeat(60));

  for (const commit of invalidCommits) {
    const result = await validateCommit(commit, config);
    const status = result.valid ? 'PASS' : 'FAIL';
    const icon = result.valid ? '[OK]' : '[X]';
    console.log(`${icon} ${commit || '(empty)'}`);
    if (!result.valid && result.errors.length > 0) {
      console.log(`    Reason: ${result.errors[0]}`);
    }
  }

  console.log();
  console.log('='.repeat(60));
  console.log('KEY TAKEAWAYS');
  console.log('='.repeat(60));
  console.log();
  console.log('1. Always start with a type (feat, fix, docs, etc.)');
  console.log('2. Follow the type with a colon and space');
  console.log('3. Keep the description lowercase');
  console.log('4. No period at the end');
  console.log('5. Use imperative mood (add, fix, update - not added, fixed)');
  console.log();
}

main().catch(console.error);
