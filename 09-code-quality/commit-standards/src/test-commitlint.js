#!/usr/bin/env node

/**
 * Test Suite for Commitlint Configuration
 *
 * This script tests both valid and invalid commit messages
 * to verify the commitlint configuration is working correctly.
 */

const load = require('@commitlint/load').default;
const lint = require('@commitlint/lint').default;

// ANSI colors
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  dim: '\x1b[2m',
};

// Test cases: messages that SHOULD pass
const validMessages = [
  // Basic types
  { message: 'feat: add new feature', description: 'Basic feature' },
  { message: 'fix: resolve bug', description: 'Basic fix' },
  { message: 'docs: update readme', description: 'Documentation' },
  { message: 'style: format code', description: 'Style changes' },
  { message: 'refactor: simplify logic', description: 'Refactoring' },
  { message: 'perf: optimize query', description: 'Performance' },
  { message: 'test: add unit tests', description: 'Tests' },
  { message: 'build: update dependencies', description: 'Build' },
  { message: 'ci: add github workflow', description: 'CI' },
  { message: 'chore: clean up files', description: 'Chore' },
  { message: 'revert: revert previous commit', description: 'Revert' },

  // With scopes
  { message: 'feat(api): add endpoint', description: 'Feature with scope' },
  { message: 'fix(auth): resolve token issue', description: 'Fix with scope' },
  { message: 'docs(readme): add examples', description: 'Docs with scope' },

  // Breaking changes
  { message: 'feat!: remove deprecated api', description: 'Breaking change (!)' },
  { message: 'feat(api)!: change response format', description: 'Breaking with scope' },

  // With body
  {
    message: 'feat: add user registration\n\nImplemented user signup flow.',
    description: 'Feature with body',
  },

  // With footer
  {
    message: 'fix: resolve login bug\n\nFixed redirect loop.\n\nCloses #123',
    description: 'Fix with footer',
  },

  // Breaking change footer
  {
    message: 'refactor: change api format\n\nBREAKING CHANGE: Response format changed.',
    description: 'Breaking change footer',
  },
];

// Test cases: messages that SHOULD fail
const invalidMessages = [
  { message: 'add feature', reason: 'Missing type' },
  { message: 'feat add feature', reason: 'Missing colon' },
  { message: 'Feat: add feature', reason: 'Capitalized type' },
  { message: 'feat: Add feature', reason: 'Capitalized description' },
  { message: 'feat: add feature.', reason: 'Trailing period' },
  { message: 'feat:', reason: 'Empty description' },
  { message: 'feat:add feature', reason: 'Missing space after colon' },
  { message: 'feature: add feature', reason: 'Invalid type' },
  { message: 'FEAT: add feature', reason: 'Uppercase type' },
  { message: 'feat(API): add feature', reason: 'Uppercase scope' },
  {
    message: 'feat: ' + 'x'.repeat(100),
    reason: 'Header too long (>72 chars)',
  },
];

/**
 * Run validation on a commit message
 */
async function validateMessage(message, config) {
  const result = await lint(message, config.rules, config);
  return {
    valid: result.valid,
    errors: result.errors.map((e) => e.message),
    warnings: result.warnings.map((w) => w.message),
  };
}

/**
 * Run all tests
 */
async function runTests() {
  console.log('');
  console.log('='.repeat(60));
  console.log('Commitlint Configuration Test Suite');
  console.log('='.repeat(60));
  console.log('');

  // Load config
  let config;
  try {
    config = await load({}, { cwd: process.cwd() });
    console.log(`${colors.green}✓ Loaded local commitlint.config.js${colors.reset}`);
  } catch (err) {
    config = await load({ extends: ['@commitlint/config-conventional'] });
    console.log(`${colors.yellow}⚠ Using default conventional config${colors.reset}`);
  }
  console.log('');

  let passed = 0;
  let failed = 0;

  // Parse command line args
  const args = process.argv.slice(2);
  const runValidOnly = args.includes('--valid');
  const runInvalidOnly = args.includes('--invalid');

  // Test valid messages
  if (!runInvalidOnly) {
    console.log(`${colors.blue}Testing Valid Messages (should PASS)${colors.reset}`);
    console.log('-'.repeat(60));

    for (const test of validMessages) {
      const result = await validateMessage(test.message, config);
      const header = test.message.split('\n')[0];

      if (result.valid) {
        console.log(`${colors.green}✓ PASS${colors.reset} ${test.description}`);
        console.log(`  ${colors.dim}${header}${colors.reset}`);
        passed++;
      } else {
        console.log(`${colors.red}✗ FAIL${colors.reset} ${test.description}`);
        console.log(`  ${colors.dim}${header}${colors.reset}`);
        console.log(`  ${colors.red}Error: ${result.errors[0]}${colors.reset}`);
        failed++;
      }
    }
    console.log('');
  }

  // Test invalid messages
  if (!runValidOnly) {
    console.log(`${colors.blue}Testing Invalid Messages (should FAIL)${colors.reset}`);
    console.log('-'.repeat(60));

    for (const test of invalidMessages) {
      const result = await validateMessage(test.message, config);
      const header = test.message.split('\n')[0].substring(0, 50);

      if (!result.valid) {
        console.log(`${colors.green}✓ PASS${colors.reset} Rejected: ${test.reason}`);
        console.log(`  ${colors.dim}${header}...${colors.reset}`);
        passed++;
      } else {
        console.log(`${colors.red}✗ FAIL${colors.reset} Should reject: ${test.reason}`);
        console.log(`  ${colors.dim}${header}...${colors.reset}`);
        console.log(`  ${colors.red}Message was accepted but should be rejected${colors.reset}`);
        failed++;
      }
    }
    console.log('');
  }

  // Summary
  console.log('='.repeat(60));
  console.log('Test Summary');
  console.log('='.repeat(60));
  console.log(`  ${colors.green}Passed: ${passed}${colors.reset}`);
  console.log(`  ${colors.red}Failed: ${failed}${colors.reset}`);
  console.log(`  Total:  ${passed + failed}`);
  console.log('');

  if (failed > 0) {
    console.log(`${colors.red}Some tests failed. Check your commitlint configuration.${colors.reset}`);
    process.exit(1);
  } else {
    console.log(`${colors.green}All tests passed! Configuration is correct.${colors.reset}`);
    process.exit(0);
  }
}

// Run tests
runTests().catch((err) => {
  console.error(`${colors.red}Error running tests: ${err.message}${colors.reset}`);
  process.exit(1);
});
