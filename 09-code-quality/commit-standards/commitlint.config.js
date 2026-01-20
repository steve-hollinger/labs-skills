/**
 * commitlint configuration for Conventional Commits
 *
 * This configuration enforces the Conventional Commits specification
 * with some customizations for common project needs.
 *
 * @see https://commitlint.js.org/
 * @see https://www.conventionalcommits.org/
 */
module.exports = {
  // Extend the conventional commits config as our base
  extends: ['@commitlint/config-conventional'],

  // Custom rules to enforce team standards
  rules: {
    // Allowed commit types
    // [severity, applicability, value]
    // Severity: 0 = disabled, 1 = warning, 2 = error
    // Applicability: 'always' | 'never'
    'type-enum': [
      2,
      'always',
      [
        'feat',     // New feature
        'fix',      // Bug fix
        'docs',     // Documentation only changes
        'style',    // Code style (formatting, semicolons, etc.)
        'refactor', // Code change that neither fixes nor adds
        'perf',     // Performance improvement
        'test',     // Adding or correcting tests
        'build',    // Build system or external dependencies
        'ci',       // CI configuration
        'chore',    // Other changes that don't modify src/test
        'revert',   // Reverts a previous commit
      ],
    ],

    // Type must be lowercase
    'type-case': [2, 'always', 'lower-case'],

    // Type cannot be empty
    'type-empty': [2, 'never'],

    // Scope rules (optional but when used, follow these)
    'scope-case': [2, 'always', 'lower-case'],

    // Subject (description) rules
    'subject-case': [
      2,
      'always',
      'lower-case', // subject must be lowercase
    ],
    'subject-empty': [2, 'never'],      // subject is required
    'subject-full-stop': [2, 'never'],  // no period at end

    // Header (type + scope + subject) max length
    'header-max-length': [2, 'always', 72],

    // Body rules
    'body-leading-blank': [2, 'always'], // blank line before body
    'body-max-line-length': [2, 'always', 100],

    // Footer rules
    'footer-leading-blank': [2, 'always'], // blank line before footer
    'footer-max-line-length': [2, 'always', 100],
  },

  // Optional: Define allowed scopes for your project
  // Uncomment and customize for your team
  // rules: {
  //   'scope-enum': [
  //     2,
  //     'always',
  //     [
  //       'api',
  //       'ui',
  //       'auth',
  //       'db',
  //       'config',
  //       'deps',
  //       'core',
  //     ],
  //   ],
  // },

  // Prompt configuration for interactive commit tools
  prompt: {
    questions: {
      type: {
        description: "Select the type of change you're committing",
        enum: {
          feat: {
            description: 'A new feature',
            title: 'Features',
            emoji: '✨',
          },
          fix: {
            description: 'A bug fix',
            title: 'Bug Fixes',
            emoji: '🐛',
          },
          docs: {
            description: 'Documentation only changes',
            title: 'Documentation',
            emoji: '📚',
          },
          style: {
            description: 'Changes that do not affect the meaning of the code',
            title: 'Styles',
            emoji: '💎',
          },
          refactor: {
            description: 'A code change that neither fixes a bug nor adds a feature',
            title: 'Code Refactoring',
            emoji: '📦',
          },
          perf: {
            description: 'A code change that improves performance',
            title: 'Performance Improvements',
            emoji: '🚀',
          },
          test: {
            description: 'Adding missing tests or correcting existing tests',
            title: 'Tests',
            emoji: '🚨',
          },
          build: {
            description: 'Changes that affect the build system or external dependencies',
            title: 'Builds',
            emoji: '🛠',
          },
          ci: {
            description: 'Changes to CI configuration files and scripts',
            title: 'Continuous Integrations',
            emoji: '⚙️',
          },
          chore: {
            description: "Other changes that don't modify src or test files",
            title: 'Chores',
            emoji: '♻️',
          },
          revert: {
            description: 'Reverts a previous commit',
            title: 'Reverts',
            emoji: '🗑',
          },
        },
      },
      scope: {
        description: 'What is the scope of this change (e.g. component or file name)',
      },
      subject: {
        description: 'Write a short, imperative tense description of the change',
      },
      body: {
        description: 'Provide a longer description of the change',
      },
      isBreaking: {
        description: 'Are there any breaking changes?',
      },
      breakingBody: {
        description: 'A BREAKING CHANGE commit requires a body. Please enter a longer description',
      },
      breaking: {
        description: 'Describe the breaking changes',
      },
      isIssueAffected: {
        description: 'Does this change affect any open issues?',
      },
      issuesBody: {
        description: 'If issues are closed, the commit requires a body. Please enter a longer description',
      },
      issues: {
        description: 'Add issue references (e.g. "fix #123", "re #123".)',
      },
    },
  },
};
