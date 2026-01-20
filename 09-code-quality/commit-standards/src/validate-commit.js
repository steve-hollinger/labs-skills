#!/usr/bin/env node

/**
 * Commit Message Validator
 *
 * A utility script to validate commit messages against conventional commit standards.
 * Can be used standalone or integrated into CI/CD pipelines.
 *
 * Usage:
 *   node validate-commit.js "feat: add new feature"
 *   echo "fix: bug fix" | node validate-commit.js
 *   node validate-commit.js --file .git/COMMIT_EDITMSG
 */

const load = require('@commitlint/load').default;
const lint = require('@commitlint/lint').default;
const fs = require('fs');

// ANSI color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  dim: '\x1b[2m',
};

/**
 * Read commit message from various sources
 */
async function getCommitMessage(args) {
  // From command line argument
  if (args.length > 0 && !args[0].startsWith('--')) {
    return args.join(' ');
  }

  // From file (--file flag)
  const fileIndex = args.indexOf('--file');
  if (fileIndex !== -1 && args[fileIndex + 1]) {
    const filePath = args[fileIndex + 1];
    try {
      return fs.readFileSync(filePath, 'utf8').trim();
    } catch (err) {
      console.error(`${colors.red}Error reading file: ${filePath}${colors.reset}`);
      process.exit(1);
    }
  }

  // From stdin
  return new Promise((resolve) => {
    let data = '';
    process.stdin.setEncoding('utf8');

    if (process.stdin.isTTY) {
      console.log('Enter commit message (Ctrl+D to finish):');
    }

    process.stdin.on('data', (chunk) => {
      data += chunk;
    });

    process.stdin.on('end', () => {
      resolve(data.trim());
    });
  });
}

/**
 * Format validation result for display
 */
function formatResult(result, message) {
  const { valid, errors, warnings } = result;

  console.log('');
  console.log('─'.repeat(60));
  console.log(`${colors.blue}Commit Message:${colors.reset}`);
  console.log(`  ${message.split('\n')[0]}`);
  if (message.includes('\n')) {
    console.log(`${colors.dim}  [+ ${message.split('\n').length - 1} more lines]${colors.reset}`);
  }
  console.log('─'.repeat(60));

  if (valid) {
    console.log(`${colors.green}✓ Valid commit message${colors.reset}`);
  } else {
    console.log(`${colors.red}✗ Invalid commit message${colors.reset}`);
  }

  if (errors.length > 0) {
    console.log('');
    console.log(`${colors.red}Errors:${colors.reset}`);
    errors.forEach((error) => {
      console.log(`  • ${error.message}`);
      if (error.name) {
        console.log(`    ${colors.dim}Rule: ${error.name}${colors.reset}`);
      }
    });
  }

  if (warnings.length > 0) {
    console.log('');
    console.log(`${colors.yellow}Warnings:${colors.reset}`);
    warnings.forEach((warning) => {
      console.log(`  • ${warning.message}`);
    });
  }

  console.log('─'.repeat(60));
  console.log('');

  return valid;
}

/**
 * Show help message
 */
function showHelp() {
  console.log(`
Commit Message Validator

Usage:
  node validate-commit.js "your commit message"
  echo "feat: add feature" | node validate-commit.js
  node validate-commit.js --file .git/COMMIT_EDITMSG

Options:
  --file <path>  Read commit message from file
  --help         Show this help message
  --quiet        Only output pass/fail (exit code)

Examples:
  # Validate a simple message
  node validate-commit.js "feat: add user login"

  # Validate from stdin
  echo "fix(auth): resolve token issue" | node validate-commit.js

  # Validate the last commit message
  git log -1 --format=%B | node validate-commit.js

  # Validate in CI pipeline
  node validate-commit.js --file .git/COMMIT_EDITMSG --quiet
`);
}

/**
 * Main function
 */
async function main() {
  const args = process.argv.slice(2);

  // Handle help flag
  if (args.includes('--help')) {
    showHelp();
    process.exit(0);
  }

  // Get commit message
  const message = await getCommitMessage(args);

  if (!message) {
    console.error(`${colors.red}Error: No commit message provided${colors.reset}`);
    showHelp();
    process.exit(1);
  }

  // Load commitlint configuration
  let config;
  try {
    config = await load({}, { cwd: process.cwd() });
  } catch (err) {
    // Fall back to conventional config if no local config
    config = await load({ extends: ['@commitlint/config-conventional'] });
  }

  // Lint the message
  const result = await lint(message, config.rules, config);

  // Format and display result
  const isQuiet = args.includes('--quiet');
  if (!isQuiet) {
    formatResult(result, message);
  }

  // Exit with appropriate code
  process.exit(result.valid ? 0 : 1);
}

main().catch((err) => {
  console.error(`${colors.red}Error: ${err.message}${colors.reset}`);
  process.exit(1);
});
