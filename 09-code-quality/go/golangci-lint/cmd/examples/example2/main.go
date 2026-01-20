// Example 2: Custom Linter Configuration
//
// This example demonstrates how to configure golangci-lint with custom
// settings, linter selection, and exclusion rules.
package main

import (
	"fmt"

	"gopkg.in/yaml.v3"
)

func main() {
	fmt.Println("Example 2: Custom Linter Configuration")
	fmt.Println("========================================")
	fmt.Println()

	// Show minimal configuration
	showMinimalConfig()

	// Show intermediate configuration
	showIntermediateConfig()

	// Show production configuration
	showProductionConfig()

	// Show exclusion patterns
	showExclusionPatterns()

	fmt.Println("\nExample completed successfully!")
}

// GolangciConfig represents the structure of .golangci.yml
type GolangciConfig struct {
	Run            RunConfig            `yaml:"run"`
	Linters        LintersConfig        `yaml:"linters"`
	LintersSettings LintersSettings     `yaml:"linters-settings,omitempty"`
	Issues         IssuesConfig         `yaml:"issues,omitempty"`
}

// RunConfig holds run-time configuration
type RunConfig struct {
	Timeout  string   `yaml:"timeout"`
	Tests    bool     `yaml:"tests"`
	SkipDirs []string `yaml:"skip-dirs,omitempty"`
}

// LintersConfig holds linter enable/disable settings
type LintersConfig struct {
	DisableAll bool     `yaml:"disable-all,omitempty"`
	Enable     []string `yaml:"enable"`
}

// LintersSettings holds individual linter configurations
type LintersSettings struct {
	Errcheck  *ErrcheckSettings  `yaml:"errcheck,omitempty"`
	Govet     *GovetSettings     `yaml:"govet,omitempty"`
	Goimports *GoimportsSettings `yaml:"goimports,omitempty"`
}

// ErrcheckSettings configures errcheck linter
type ErrcheckSettings struct {
	CheckTypeAssertions bool `yaml:"check-type-assertions"`
	CheckBlank          bool `yaml:"check-blank"`
}

// GovetSettings configures govet linter
type GovetSettings struct {
	Shadow bool `yaml:"shadow"`
}

// GoimportsSettings configures goimports linter
type GoimportsSettings struct {
	LocalPrefixes string `yaml:"local-prefixes"`
}

// IssuesConfig holds issue filtering configuration
type IssuesConfig struct {
	ExcludeRules []ExcludeRule `yaml:"exclude-rules,omitempty"`
}

// ExcludeRule defines an exclusion pattern
type ExcludeRule struct {
	Path    string   `yaml:"path,omitempty"`
	Linters []string `yaml:"linters"`
}

func showMinimalConfig() {
	fmt.Println("=== Minimal Configuration ===")
	fmt.Println()
	fmt.Println("Best for: New projects, learning golangci-lint")
	fmt.Println()

	config := GolangciConfig{
		Run: RunConfig{
			Timeout: "5m",
			Tests:   true,
		},
		Linters: LintersConfig{
			Enable: []string{
				"errcheck",
				"govet",
				"staticcheck",
				"unused",
			},
		},
	}

	printConfig(config)
}

func showIntermediateConfig() {
	fmt.Println("=== Intermediate Configuration ===")
	fmt.Println()
	fmt.Println("Best for: Growing projects, team development")
	fmt.Println()

	config := GolangciConfig{
		Run: RunConfig{
			Timeout:  "5m",
			Tests:    true,
			SkipDirs: []string{"vendor", "generated"},
		},
		Linters: LintersConfig{
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
			},
		},
		LintersSettings: LintersSettings{
			Errcheck: &ErrcheckSettings{
				CheckTypeAssertions: true,
			},
			Goimports: &GoimportsSettings{
				LocalPrefixes: "github.com/myorg",
			},
		},
	}

	printConfig(config)
}

func showProductionConfig() {
	fmt.Println("=== Production Configuration ===")
	fmt.Println()
	fmt.Println("Best for: Production applications, CI pipelines")
	fmt.Println()

	config := GolangciConfig{
		Run: RunConfig{
			Timeout:  "10m",
			Tests:    true,
			SkipDirs: []string{"vendor", "generated", "third_party"},
		},
		Linters: LintersConfig{
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
				"revive",
			},
		},
		LintersSettings: LintersSettings{
			Errcheck: &ErrcheckSettings{
				CheckTypeAssertions: true,
				CheckBlank:          true,
			},
			Govet: &GovetSettings{
				Shadow: true,
			},
			Goimports: &GoimportsSettings{
				LocalPrefixes: "github.com/myorg",
			},
		},
	}

	printConfig(config)
}

func showExclusionPatterns() {
	fmt.Println("=== Exclusion Patterns ===")
	fmt.Println()
	fmt.Println("Control where linters run with exclude-rules:")
	fmt.Println()

	issues := IssuesConfig{
		ExcludeRules: []ExcludeRule{
			{
				Path:    "_test\\.go",
				Linters: []string{"errcheck", "gocritic"},
			},
			{
				Path:    "examples/",
				Linters: []string{"unused"},
			},
			{
				Path:    "\\.pb\\.go$",
				Linters: []string{"all"},
			},
		},
	}

	fmt.Println("issues:")
	data, err := yaml.Marshal(issues)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}
	fmt.Println("  " + string(data))

	fmt.Println("Common patterns:")
	fmt.Println("  - _test\\.go    : Test files")
	fmt.Println("  - \\.pb\\.go$    : Protobuf generated files")
	fmt.Println("  - mock_.*\\.go  : Mock files")
	fmt.Println("  - cmd/.*/main  : CLI entry points")
	fmt.Println()
}

func printConfig(config GolangciConfig) {
	data, err := yaml.Marshal(config)
	if err != nil {
		fmt.Printf("Error marshaling config: %v\n", err)
		return
	}
	fmt.Println("```yaml")
	fmt.Print(string(data))
	fmt.Println("```")
	fmt.Println()
}
