// Package config provides utilities for working with golangci-lint configurations.
package config

import (
	"fmt"
	"os"

	"gopkg.in/yaml.v3"
)

// Config represents a golangci-lint configuration
type Config struct {
	Run             Run                    `yaml:"run"`
	Linters         Linters                `yaml:"linters"`
	LintersSettings map[string]interface{} `yaml:"linters-settings,omitempty"`
	Issues          Issues                 `yaml:"issues,omitempty"`
	Output          Output                 `yaml:"output,omitempty"`
	Severity        Severity               `yaml:"severity,omitempty"`
}

// Run contains run-time configuration
type Run struct {
	Timeout  string   `yaml:"timeout"`
	Tests    bool     `yaml:"tests"`
	SkipDirs []string `yaml:"skip-dirs,omitempty"`
	SkipFiles []string `yaml:"skip-files,omitempty"`
}

// Linters contains linter enable/disable configuration
type Linters struct {
	DisableAll bool     `yaml:"disable-all,omitempty"`
	EnableAll  bool     `yaml:"enable-all,omitempty"`
	Enable     []string `yaml:"enable,omitempty"`
	Disable    []string `yaml:"disable,omitempty"`
}

// Issues contains issue filtering configuration
type Issues struct {
	MaxIssuesPerLinter int           `yaml:"max-issues-per-linter,omitempty"`
	MaxSameIssues      int           `yaml:"max-same-issues,omitempty"`
	ExcludeRules       []ExcludeRule `yaml:"exclude-rules,omitempty"`
	New                bool          `yaml:"new,omitempty"`
	NewFromRev         string        `yaml:"new-from-rev,omitempty"`
}

// ExcludeRule defines an exclusion pattern
type ExcludeRule struct {
	Path    string   `yaml:"path,omitempty"`
	Text    string   `yaml:"text,omitempty"`
	Linters []string `yaml:"linters"`
}

// Output contains output configuration
type Output struct {
	Formats          []Format `yaml:"formats,omitempty"`
	PrintIssuedLines bool     `yaml:"print-issued-lines,omitempty"`
	PrintLinterName  bool     `yaml:"print-linter-name,omitempty"`
}

// Format defines an output format
type Format struct {
	Format string `yaml:"format"`
	Path   string `yaml:"path,omitempty"`
}

// Severity contains severity configuration
type Severity struct {
	DefaultSeverity string         `yaml:"default-severity,omitempty"`
	Rules           []SeverityRule `yaml:"rules,omitempty"`
}

// SeverityRule maps linters to severity levels
type SeverityRule struct {
	Linters  []string `yaml:"linters"`
	Severity string   `yaml:"severity"`
}

// DefaultConfig returns a sensible default configuration
func DefaultConfig() *Config {
	return &Config{
		Run: Run{
			Timeout: "5m",
			Tests:   true,
		},
		Linters: Linters{
			DisableAll: true,
			Enable: []string{
				"errcheck",
				"govet",
				"staticcheck",
				"unused",
			},
		},
	}
}

// ProductionConfig returns a production-ready configuration
func ProductionConfig() *Config {
	return &Config{
		Run: Run{
			Timeout:  "10m",
			Tests:    true,
			SkipDirs: []string{"vendor", "generated"},
		},
		Linters: Linters{
			DisableAll: true,
			Enable: []string{
				"errcheck",
				"govet",
				"staticcheck",
				"unused",
				"gosimple",
				"gofmt",
				"goimports",
				"ineffassign",
				"typecheck",
				"gocritic",
				"gosec",
			},
		},
		LintersSettings: map[string]interface{}{
			"errcheck": map[string]interface{}{
				"check-type-assertions": true,
				"check-blank":           true,
			},
			"govet": map[string]interface{}{
				"shadow": true,
			},
		},
		Issues: Issues{
			ExcludeRules: []ExcludeRule{
				{
					Path:    "_test\\.go",
					Linters: []string{"errcheck", "gocritic"},
				},
			},
		},
	}
}

// LoadFromFile loads a configuration from a YAML file
func LoadFromFile(path string) (*Config, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("reading config file: %w", err)
	}

	var config Config
	if err := yaml.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("parsing config file: %w", err)
	}

	return &config, nil
}

// SaveToFile saves a configuration to a YAML file
func (c *Config) SaveToFile(path string) error {
	data, err := yaml.Marshal(c)
	if err != nil {
		return fmt.Errorf("marshaling config: %w", err)
	}

	if err := os.WriteFile(path, data, 0644); err != nil {
		return fmt.Errorf("writing config file: %w", err)
	}

	return nil
}

// ToYAML converts the configuration to YAML string
func (c *Config) ToYAML() (string, error) {
	data, err := yaml.Marshal(c)
	if err != nil {
		return "", fmt.Errorf("marshaling config: %w", err)
	}
	return string(data), nil
}

// Validate checks if the configuration is valid
func (c *Config) Validate() error {
	if c.Run.Timeout == "" {
		return fmt.Errorf("timeout is required")
	}

	if len(c.Linters.Enable) == 0 && !c.Linters.EnableAll {
		return fmt.Errorf("at least one linter must be enabled")
	}

	return nil
}

// AddLinter adds a linter to the enabled list
func (c *Config) AddLinter(name string) {
	for _, l := range c.Linters.Enable {
		if l == name {
			return // Already enabled
		}
	}
	c.Linters.Enable = append(c.Linters.Enable, name)
}

// RemoveLinter removes a linter from the enabled list
func (c *Config) RemoveLinter(name string) {
	for i, l := range c.Linters.Enable {
		if l == name {
			c.Linters.Enable = append(c.Linters.Enable[:i], c.Linters.Enable[i+1:]...)
			return
		}
	}
}

// AddExcludeRule adds an exclusion rule
func (c *Config) AddExcludeRule(path string, linters []string) {
	c.Issues.ExcludeRules = append(c.Issues.ExcludeRules, ExcludeRule{
		Path:    path,
		Linters: linters,
	})
}
