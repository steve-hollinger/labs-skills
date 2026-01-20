#!/usr/bin/env node

/**
 * Example 2: Scoped Commit Messages
 *
 * This demo shows how to use scopes and commit bodies effectively.
 */

const load = require('@commitlint/load').default;
const lint = require('@commitlint/lint').default;

// Example scoped commits
const scopedCommits = [
  {
    message: 'feat(auth): add two-factor authentication',
    description: 'Feature with auth scope',
  },
  {
    message: 'fix(api): handle timeout errors gracefully',
    description: 'Bug fix with api scope',
  },
  {
    message: 'docs(readme): add deployment instructions',
    description: 'Docs with readme scope',
  },
  {
    message: 'refactor(db): optimize user lookup queries',
    description: 'Refactor with db scope',
  },
  {
    message: 'test(payments): add integration tests for refunds',
    description: 'Tests with payments scope',
  },
];

// Example commits with bodies
const commitsWithBodies = [
  {
    message: `feat(search): implement fuzzy matching

Added Levenshtein distance algorithm for typo-tolerant search.
Users can now find products even with minor spelling mistakes.`,
    description: 'Feature with explanatory body',
  },
  {
    message: `fix(cart): prevent race condition on quantity update

Multiple rapid clicks could cause incorrect totals due to
async state updates. Added debouncing and optimistic locking.`,
    description: 'Bug fix explaining root cause and solution',
  },
  {
    message: `refactor(api): migrate from callbacks to async/await

Replaced all callback-based database queries with async/await.
Improves readability and makes error handling more consistent.

No functional changes - all existing tests pass.`,
    description: 'Refactor with multi-paragraph body',
  },
];

// Invalid scoped commits
const invalidScoped = [
  {
    message: 'feat(AUTH): add feature',
    error: 'Scope must be lowercase',
  },
  {
    message: 'feat(): add feature',
    error: 'Empty scope',
  },
  {
    message: 'feat( api ): add feature',
    error: 'Scope has extra spaces',
  },
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

function displayCommit(message) {
  const lines = message.split('\n');
  const header = lines[0];
  const body = lines.slice(1).join('\n').trim();

  console.log(`  Header: ${header}`);
  if (body) {
    console.log('  Body:');
    body.split('\n').forEach(line => {
      console.log(`    ${line}`);
    });
  }
}

async function main() {
  console.log('='.repeat(60));
  console.log('Example 2: Scoped Commit Messages');
  console.log('='.repeat(60));
  console.log();

  const config = await load({ extends: ['@commitlint/config-conventional'] });

  // Section 1: Basic scoped commits
  console.log('SCOPED COMMITS');
  console.log('-'.repeat(60));

  for (const commit of scopedCommits) {
    const result = await validateCommit(commit.message, config);
    const icon = result.valid ? '[OK]' : '[X]';
    console.log(`${icon} ${commit.description}`);
    console.log(`    ${commit.message}`);
    console.log();
  }

  // Section 2: Commits with bodies
  console.log('COMMITS WITH BODIES');
  console.log('-'.repeat(60));

  for (const commit of commitsWithBodies) {
    const result = await validateCommit(commit.message, config);
    const icon = result.valid ? '[OK]' : '[X]';
    console.log(`${icon} ${commit.description}`);
    displayCommit(commit.message);
    console.log();
  }

  // Section 3: Invalid examples
  console.log('INVALID SCOPED COMMITS');
  console.log('-'.repeat(60));

  for (const commit of invalidScoped) {
    const result = await validateCommit(commit.message, config);
    const icon = result.valid ? '[OK]' : '[X]';
    console.log(`${icon} ${commit.error}`);
    console.log(`    ${commit.message}`);
    if (!result.valid && result.errors.length > 0) {
      console.log(`    Reason: ${result.errors[0]}`);
    }
    console.log();
  }

  // Key takeaways
  console.log('='.repeat(60));
  console.log('KEY TAKEAWAYS');
  console.log('='.repeat(60));
  console.log();
  console.log('1. Scopes go in parentheses: feat(scope): description');
  console.log('2. Scopes should be lowercase');
  console.log('3. Common scopes: api, ui, auth, db, config, deps');
  console.log('4. Bodies are separated by a blank line');
  console.log('5. Bodies explain WHY, not just WHAT');
  console.log('6. Keep each body line under 100 characters');
  console.log();
}

main().catch(console.error);
