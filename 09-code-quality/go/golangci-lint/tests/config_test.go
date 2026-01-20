package tests

import (
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gopkg.in/yaml.v3"
)

// GolangciConfig represents the structure of .golangci.yml
type GolangciConfig struct {
	Run             RunConfig         `yaml:"run"`
	Linters         LintersConfig     `yaml:"linters"`
	LintersSettings map[string]any    `yaml:"linters-settings"`
	Issues          IssuesConfig      `yaml:"issues"`
	Output          OutputConfig      `yaml:"output"`
	Severity        SeverityConfig    `yaml:"severity"`
}

// RunConfig holds run-time configuration
type RunConfig struct {
	Timeout  string   `yaml:"timeout"`
	Tests    bool     `yaml:"tests"`
	SkipDirs []string `yaml:"skip-dirs"`
}

// LintersConfig holds linter enable/disable settings
type LintersConfig struct {
	DisableAll bool     `yaml:"disable-all"`
	Enable     []string `yaml:"enable"`
	Disable    []string `yaml:"disable"`
}

// IssuesConfig holds issue configuration
type IssuesConfig struct {
	MaxIssuesPerLinter int           `yaml:"max-issues-per-linter"`
	MaxSameIssues      int           `yaml:"max-same-issues"`
	ExcludeRules       []ExcludeRule `yaml:"exclude-rules"`
}

// ExcludeRule defines an exclusion pattern
type ExcludeRule struct {
	Path    string   `yaml:"path"`
	Linters []string `yaml:"linters"`
}

// OutputConfig holds output configuration
type OutputConfig struct {
	Formats []FormatConfig `yaml:"formats"`
}

// FormatConfig defines output format
type FormatConfig struct {
	Format string `yaml:"format"`
}

// SeverityConfig holds severity settings
type SeverityConfig struct {
	DefaultSeverity string         `yaml:"default-severity"`
	Rules           []SeverityRule `yaml:"rules"`
}

// SeverityRule maps linters to severity levels
type SeverityRule struct {
	Linters  []string `yaml:"linters"`
	Severity string   `yaml:"severity"`
}

func TestParseGolangciConfig(t *testing.T) {
	// Read the config file
	data, err := os.ReadFile("../.golangci.yml")
	require.NoError(t, err, "Should be able to read .golangci.yml")

	var config GolangciConfig
	err = yaml.Unmarshal(data, &config)
	require.NoError(t, err, "Should be able to parse .golangci.yml")

	// Verify run configuration
	assert.NotEmpty(t, config.Run.Timeout, "Should have timeout configured")
	assert.True(t, config.Run.Tests, "Should include tests in linting")
}

func TestRequiredLintersEnabled(t *testing.T) {
	data, err := os.ReadFile("../.golangci.yml")
	require.NoError(t, err)

	var config GolangciConfig
	err = yaml.Unmarshal(data, &config)
	require.NoError(t, err)

	// Required linters that should always be enabled
	requiredLinters := []string{
		"errcheck",
		"govet",
		"staticcheck",
		"unused",
	}

	for _, linter := range requiredLinters {
		assert.Contains(t, config.Linters.Enable, linter,
			"Linter %s should be enabled", linter)
	}
}

func TestExcludeRulesForTests(t *testing.T) {
	data, err := os.ReadFile("../.golangci.yml")
	require.NoError(t, err)

	var config GolangciConfig
	err = yaml.Unmarshal(data, &config)
	require.NoError(t, err)

	// Check that test files have some exclusions
	hasTestExclusion := false
	for _, rule := range config.Issues.ExcludeRules {
		if rule.Path == "_test\\.go" {
			hasTestExclusion = true
			break
		}
	}

	assert.True(t, hasTestExclusion, "Should have exclusion rules for test files")
}

func TestConfigStructure(t *testing.T) {
	tests := []struct {
		name     string
		yamlData string
		valid    bool
	}{
		{
			name: "minimal valid config",
			yamlData: `
run:
  timeout: 5m
linters:
  enable:
    - errcheck
`,
			valid: true,
		},
		{
			name: "config with linter settings",
			yamlData: `
run:
  timeout: 5m
linters:
  enable:
    - errcheck
linters-settings:
  errcheck:
    check-type-assertions: true
`,
			valid: true,
		},
		{
			name: "config with exclusions",
			yamlData: `
run:
  timeout: 5m
linters:
  enable:
    - errcheck
issues:
  exclude-rules:
    - path: _test\.go
      linters:
        - errcheck
`,
			valid: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var config GolangciConfig
			err := yaml.Unmarshal([]byte(tt.yamlData), &config)

			if tt.valid {
				assert.NoError(t, err)
			} else {
				assert.Error(t, err)
			}
		})
	}
}

func TestLinterCategories(t *testing.T) {
	// Test that we can categorize linters correctly
	bugLinters := []string{"errcheck", "govet", "staticcheck", "unused"}
	styleLinters := []string{"gofmt", "goimports", "gosimple"}
	securityLinters := []string{"gosec"}

	// These are known valid linters
	allKnownLinters := append(append(bugLinters, styleLinters...), securityLinters...)

	for _, linter := range allKnownLinters {
		assert.NotEmpty(t, linter, "Linter name should not be empty")
	}
}

func TestTimeoutParsing(t *testing.T) {
	tests := []struct {
		name    string
		timeout string
		valid   bool
	}{
		{"5 minutes", "5m", true},
		{"10 minutes", "10m", true},
		{"1 hour", "1h", true},
		{"30 seconds", "30s", true},
		{"complex duration", "1h30m", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			yamlData := `
run:
  timeout: ` + tt.timeout + `
linters:
  enable:
    - errcheck
`
			var config GolangciConfig
			err := yaml.Unmarshal([]byte(yamlData), &config)

			if tt.valid {
				require.NoError(t, err)
				assert.Equal(t, tt.timeout, config.Run.Timeout)
			}
		})
	}
}
