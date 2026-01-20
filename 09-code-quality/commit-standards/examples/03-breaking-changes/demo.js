#!/usr/bin/env node

/**
 * Example 3: Breaking Changes
 *
 * This demo shows how to properly indicate breaking changes in commits.
 */

const load = require('@commitlint/load').default;
const lint = require('@commitlint/lint').default;

// Breaking changes using ! notation
const bangNotation = [
  {
    message: 'feat!: remove deprecated user endpoints',
    description: 'Breaking change without scope',
  },
  {
    message: 'feat(api)!: change authentication flow',
    description: 'Breaking change with scope',
  },
  {
    message: 'fix(db)!: require explicit connection string',
    description: 'Breaking fix (rare but valid)',
  },
  {
    message: 'refactor(core)!: change module export format',
    description: 'Breaking refactor',
  },
];

// Breaking changes using BREAKING CHANGE footer
const footerNotation = [
  {
    message: `refactor(api): change response format

BREAKING CHANGE: All responses now use JSON:API format.`,
    description: 'Breaking change via footer',
  },
  {
    message: `feat(config): require explicit environment

BREAKING CHANGE: NODE_ENV must now be explicitly set.
Previously defaulted to development which caused production issues.`,
    description: 'Multi-line breaking change',
  },
];

// Using both methods (recommended for major changes)
const bothMethods = [
  {
    message: `feat(api)!: replace REST with GraphQL

Migrated all endpoints to GraphQL API.

BREAKING CHANGE: REST endpoints have been removed.
Use GraphQL queries and mutations instead.

Migration guide: docs/graphql-migration.md`,
    description: 'Both ! and footer (maximum visibility)',
  },
];

// Comprehensive breaking change example
const comprehensiveExample = {
  message: `feat(api)!: change pagination to cursor-based

Implemented cursor-based pagination for better performance
with large datasets.

BREAKING CHANGE: Pagination parameters have changed.

Before:
  GET /users?page=2&per_page=20
  Response: { data: [], page: 2, total_pages: 10 }

After:
  GET /users?cursor=abc123&limit=20
  Response: { data: [], next_cursor: "xyz", has_more: true }

Migration steps:
1. Replace page/per_page with cursor/limit
2. Store next_cursor from responses
3. Use next_cursor for subsequent requests

See docs/pagination-migration.md for examples.`,
  description: 'Complete breaking change with migration guide',
};

async function validateCommit(message, config) {
  const result = await lint(message, config.rules, config);
  return {
    valid: result.valid,
    errors: result.errors.map(e => e.message),
    warnings: result.warnings.map(w => w.message),
  };
}

function displayMultilineCommit(message, indent = '    ') {
  const lines = message.split('\n');
  lines.forEach(line => {
    console.log(`${indent}${line}`);
  });
}

async function main() {
  console.log('='.repeat(60));
  console.log('Example 3: Breaking Changes');
  console.log('='.repeat(60));
  console.log();

  const config = await load({ extends: ['@commitlint/config-conventional'] });

  // Section 1: ! notation
  console.log('METHOD 1: Using ! Notation');
  console.log('-'.repeat(60));

  for (const commit of bangNotation) {
    const result = await validateCommit(commit.message, config);
    const icon = result.valid ? '[OK]' : '[X]';
    console.log(`${icon} ${commit.description}`);
    console.log(`    ${commit.message}`);
    console.log();
  }

  // Section 2: Footer notation
  console.log('METHOD 2: Using BREAKING CHANGE Footer');
  console.log('-'.repeat(60));

  for (const commit of footerNotation) {
    const result = await validateCommit(commit.message, config);
    const icon = result.valid ? '[OK]' : '[X]';
    console.log(`${icon} ${commit.description}`);
    displayMultilineCommit(commit.message);
    console.log();
  }

  // Section 3: Both methods
  console.log('METHOD 3: Both Methods (Recommended)');
  console.log('-'.repeat(60));

  for (const commit of bothMethods) {
    const result = await validateCommit(commit.message, config);
    const icon = result.valid ? '[OK]' : '[X]';
    console.log(`${icon} ${commit.description}`);
    displayMultilineCommit(commit.message);
    console.log();
  }

  // Section 4: Comprehensive example
  console.log('COMPREHENSIVE EXAMPLE');
  console.log('-'.repeat(60));
  console.log('[OK] ' + comprehensiveExample.description);
  console.log();
  displayMultilineCommit(comprehensiveExample.message, '  ');
  console.log();

  // Semantic versioning impact
  console.log('SEMANTIC VERSIONING IMPACT');
  console.log('-'.repeat(60));
  console.log('Breaking changes trigger MAJOR version bumps:');
  console.log();
  console.log('  Current Version  ->  After Breaking Change');
  console.log('  1.2.3           ->  2.0.0');
  console.log('  0.5.2           ->  1.0.0');
  console.log('  2.0.0           ->  3.0.0');
  console.log();

  // Key takeaways
  console.log('='.repeat(60));
  console.log('KEY TAKEAWAYS');
  console.log('='.repeat(60));
  console.log();
  console.log('1. Use ! after type/scope: feat(api)!: description');
  console.log('2. Or use BREAKING CHANGE footer in body');
  console.log('3. For major changes, use BOTH for visibility');
  console.log('4. Always include migration guide');
  console.log('5. Show before/after examples');
  console.log('6. Breaking changes = MAJOR version bump');
  console.log();
}

main().catch(console.error);
