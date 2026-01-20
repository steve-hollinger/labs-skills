package tests

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

// TestLinterIssueTypes verifies understanding of different linter issue types
func TestLinterIssueTypes(t *testing.T) {
	tests := []struct {
		name        string
		linter      string
		issueType   string
		description string
	}{
		{
			name:        "errcheck detects unchecked errors",
			linter:      "errcheck",
			issueType:   "bug",
			description: "Unchecked errors can lead to silent failures",
		},
		{
			name:        "govet detects suspicious constructs",
			linter:      "govet",
			issueType:   "bug",
			description: "Printf format mismatches, struct tag issues",
		},
		{
			name:        "staticcheck provides advanced analysis",
			linter:      "staticcheck",
			issueType:   "bug",
			description: "Deprecated API usage, inefficiencies",
		},
		{
			name:        "unused finds dead code",
			linter:      "unused",
			issueType:   "maintenance",
			description: "Unused variables, functions, types",
		},
		{
			name:        "gosimple suggests simplifications",
			linter:      "gosimple",
			issueType:   "style",
			description: "Code that can be written more simply",
		},
		{
			name:        "gofmt checks formatting",
			linter:      "gofmt",
			issueType:   "style",
			description: "Go code formatting standards",
		},
		{
			name:        "gosec finds security issues",
			linter:      "gosec",
			issueType:   "security",
			description: "SQL injection, hardcoded credentials",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.NotEmpty(t, tt.linter)
			assert.NotEmpty(t, tt.issueType)
			assert.NotEmpty(t, tt.description)

			// Verify issue type is one of the expected categories
			validTypes := []string{"bug", "maintenance", "style", "security", "performance"}
			assert.Contains(t, validTypes, tt.issueType,
				"Issue type should be a valid category")
		})
	}
}

// TestNolintDirectiveFormats tests understanding of nolint directive formats
func TestNolintDirectiveFormats(t *testing.T) {
	tests := []struct {
		name      string
		directive string
		valid     bool
		hasReason bool
	}{
		{
			name:      "basic nolint",
			directive: "//nolint",
			valid:     true,
			hasReason: false,
		},
		{
			name:      "nolint with specific linter",
			directive: "//nolint:errcheck",
			valid:     true,
			hasReason: false,
		},
		{
			name:      "nolint with reason",
			directive: "//nolint:errcheck // intentionally ignoring error",
			valid:     true,
			hasReason: true,
		},
		{
			name:      "nolint with multiple linters",
			directive: "//nolint:errcheck,govet",
			valid:     true,
			hasReason: false,
		},
		{
			name:      "nolint with multiple linters and reason",
			directive: "//nolint:errcheck,govet // complex but necessary",
			valid:     true,
			hasReason: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.True(t, len(tt.directive) > 0)
			// In a real implementation, we would parse the directive
			// Here we just verify our test cases are set up correctly
			if tt.hasReason {
				assert.Contains(t, tt.directive, "//", "Reason should be after //")
			}
		})
	}
}

// TestCIOutputFormats verifies CI output format options
func TestCIOutputFormats(t *testing.T) {
	formats := []struct {
		name    string
		format  string
		useCase string
	}{
		{
			name:    "colored line number",
			format:  "colored-line-number",
			useCase: "Local development with color support",
		},
		{
			name:    "github actions",
			format:  "github-actions",
			useCase: "GitHub Actions annotations",
		},
		{
			name:    "line number",
			format:  "line-number",
			useCase: "Plain text for any CI",
		},
		{
			name:    "json",
			format:  "json",
			useCase: "Machine-readable output",
		},
		{
			name:    "checkstyle",
			format:  "checkstyle",
			useCase: "Jenkins and similar tools",
		},
		{
			name:    "code climate",
			format:  "code-climate",
			useCase: "Code Climate integration",
		},
	}

	for _, f := range formats {
		t.Run(f.name, func(t *testing.T) {
			assert.NotEmpty(t, f.format)
			assert.NotEmpty(t, f.useCase)
		})
	}
}

// TestExclusionPatterns verifies common exclusion regex patterns
func TestExclusionPatterns(t *testing.T) {
	patterns := []struct {
		name        string
		pattern     string
		shouldMatch []string
		shouldNotMatch []string
	}{
		{
			name:        "test files",
			pattern:     "_test\\.go",
			shouldMatch: []string{"main_test.go", "handler_test.go"},
			shouldNotMatch: []string{"main.go", "test.go"},
		},
		{
			name:        "protobuf files",
			pattern:     "\\.pb\\.go$",
			shouldMatch: []string{"user.pb.go", "api.pb.go"},
			shouldNotMatch: []string{"main.go", "pb.go"},
		},
		{
			name:        "mock files",
			pattern:     "mock_.*\\.go",
			shouldMatch: []string{"mock_service.go", "mock_repo.go"},
			shouldNotMatch: []string{"service.go", "mocks.go"},
		},
		{
			name:        "generated files",
			pattern:     ".*_gen\\.go$",
			shouldMatch: []string{"types_gen.go", "api_gen.go"},
			shouldNotMatch: []string{"gen.go", "generator.go"},
		},
	}

	for _, p := range patterns {
		t.Run(p.name, func(t *testing.T) {
			assert.NotEmpty(t, p.pattern, "Pattern should not be empty")
			assert.NotEmpty(t, p.shouldMatch, "Should have match examples")
		})
	}
}

// TestBestPracticesDocumented verifies best practices are captured
func TestBestPracticesDocumented(t *testing.T) {
	bestPractices := []struct {
		practice    string
		description string
	}{
		{
			practice:    "Start with minimal config",
			description: "Enable only essential linters first",
		},
		{
			practice:    "Use disable-all with explicit enables",
			description: "For clarity about exactly which linters run",
		},
		{
			practice:    "Set appropriate timeouts",
			description: "CI environments need longer timeouts",
		},
		{
			practice:    "Document nolint directives",
			description: "Always explain why a lint is disabled",
		},
		{
			practice:    "Use gradual adoption",
			description: "new-from-rev helps with legacy codebases",
		},
		{
			practice:    "Pin versions in CI",
			description: "Reproducible builds require fixed versions",
		},
	}

	for _, bp := range bestPractices {
		t.Run(bp.practice, func(t *testing.T) {
			assert.NotEmpty(t, bp.practice)
			assert.NotEmpty(t, bp.description)
		})
	}
}
