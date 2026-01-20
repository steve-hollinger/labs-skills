// Solution for Exercise 3: File Processing Pipeline
//
// This solution implements a concurrent pipeline for file processing.

package main

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

// FileInfo represents a discovered file
type FileInfo struct {
	Path string
	Size int64
}

// FileContent represents a file's content
type FileContent struct {
	Path    string
	Content []byte
	Error   error
}

// FileStats represents statistics about a file
type FileStats struct {
	Path     string
	Bytes    int
	Lines    int
	Words    int
	Duration time.Duration
	Error    error
}

// AggregateStats represents combined statistics
type AggregateStats struct {
	FileCount    int
	TotalBytes   int
	TotalLines   int
	TotalWords   int
	TotalTime    time.Duration
	ErrorCount   int
	FilesSkipped int
}

// Pipeline orchestrates the file processing
type Pipeline struct {
	workers    int
	rootDir    string
	pattern    string
	ctx        context.Context
	cancelFunc context.CancelFunc
}

// NewPipeline creates a new file processing pipeline
func NewPipeline(rootDir, pattern string, workers int) *Pipeline {
	ctx, cancel := context.WithCancel(context.Background())
	return &Pipeline{
		workers:    workers,
		rootDir:    rootDir,
		pattern:    pattern,
		ctx:        ctx,
		cancelFunc: cancel,
	}
}

// Discover finds files matching the pattern
func (p *Pipeline) Discover() <-chan FileInfo {
	out := make(chan FileInfo)

	go func() {
		defer close(out)

		err := filepath.Walk(p.rootDir, func(path string, info os.FileInfo, err error) error {
			// Check for cancellation
			select {
			case <-p.ctx.Done():
				return p.ctx.Err()
			default:
			}

			if err != nil {
				return nil // Skip files with errors
			}

			// Skip directories
			if info.IsDir() {
				return nil
			}

			// Match against pattern
			matched, err := filepath.Match(p.pattern, info.Name())
			if err != nil {
				return nil
			}

			if matched {
				select {
				case <-p.ctx.Done():
					return p.ctx.Err()
				case out <- FileInfo{Path: path, Size: info.Size()}:
				}
			}

			return nil
		})

		if err != nil && err != context.Canceled {
			fmt.Printf("Discovery error: %v\n", err)
		}
	}()

	return out
}

// Read reads file contents concurrently (fan-out)
func (p *Pipeline) Read(files <-chan FileInfo) <-chan FileContent {
	out := make(chan FileContent)
	var wg sync.WaitGroup

	// Start workers
	for i := 0; i < p.workers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for {
				select {
				case <-p.ctx.Done():
					return
				case file, ok := <-files:
					if !ok {
						return
					}

					content, err := os.ReadFile(file.Path)
					result := FileContent{
						Path:    file.Path,
						Content: content,
						Error:   err,
					}

					select {
					case <-p.ctx.Done():
						return
					case out <- result:
					}
				}
			}
		}()
	}

	// Close output when all workers done
	go func() {
		wg.Wait()
		close(out)
	}()

	return out
}

// Process analyzes file contents
func (p *Pipeline) Process(contents <-chan FileContent) <-chan FileStats {
	out := make(chan FileStats)

	go func() {
		defer close(out)

		for {
			select {
			case <-p.ctx.Done():
				return
			case content, ok := <-contents:
				if !ok {
					return
				}

				start := time.Now()

				// Handle read errors
				if content.Error != nil {
					select {
					case <-p.ctx.Done():
						return
					case out <- FileStats{Path: content.Path, Error: content.Error}:
					}
					continue
				}

				// Calculate statistics
				text := string(content.Content)
				stats := FileStats{
					Path:     content.Path,
					Bytes:    len(content.Content),
					Lines:    strings.Count(text, "\n") + 1,
					Words:    len(strings.Fields(text)),
					Duration: time.Since(start),
				}

				select {
				case <-p.ctx.Done():
					return
				case out <- stats:
				}
			}
		}
	}()

	return out
}

// Aggregate combines all statistics
func (p *Pipeline) Aggregate(stats <-chan FileStats) AggregateStats {
	var agg AggregateStats
	start := time.Now()

	for {
		select {
		case <-p.ctx.Done():
			agg.TotalTime = time.Since(start)
			return agg
		case stat, ok := <-stats:
			if !ok {
				agg.TotalTime = time.Since(start)
				return agg
			}

			if stat.Error != nil {
				agg.ErrorCount++
				continue
			}

			agg.FileCount++
			agg.TotalBytes += stat.Bytes
			agg.TotalLines += stat.Lines
			agg.TotalWords += stat.Words
		}
	}
}

// Run executes the full pipeline
func (p *Pipeline) Run() AggregateStats {
	// Connect pipeline stages
	files := p.Discover()
	contents := p.Read(files)
	stats := p.Process(contents)
	return p.Aggregate(stats)
}

// Cancel stops the pipeline
func (p *Pipeline) Cancel() {
	p.cancelFunc()
}

func main() {
	fmt.Println("Solution 3: File Processing Pipeline")
	fmt.Println("=====================================")
	fmt.Println()

	// Process Go files in current directory tree
	pipeline := NewPipeline(".", "*.go", 4)

	fmt.Println("Running pipeline with 4 workers...")
	fmt.Printf("Scanning for %s files in %s\n", pipeline.pattern, pipeline.rootDir)
	fmt.Println()

	start := time.Now()
	stats := pipeline.Run()
	elapsed := time.Since(start)

	fmt.Println("Results:")
	fmt.Printf("  Files processed: %d\n", stats.FileCount)
	fmt.Printf("  Errors:          %d\n", stats.ErrorCount)
	fmt.Printf("  Total bytes:     %d (%d KB)\n", stats.TotalBytes, stats.TotalBytes/1024)
	fmt.Printf("  Total lines:     %d\n", stats.TotalLines)
	fmt.Printf("  Total words:     %d\n", stats.TotalWords)
	fmt.Printf("  Pipeline time:   %v\n", elapsed.Round(time.Millisecond))

	if stats.FileCount > 0 {
		fmt.Printf("  Avg lines/file:  %d\n", stats.TotalLines/stats.FileCount)
		fmt.Printf("  Avg words/file:  %d\n", stats.TotalWords/stats.FileCount)
	}

	// Test cancellation
	fmt.Println()
	fmt.Println("Testing early cancellation...")

	pipeline2 := NewPipeline(".", "*.go", 4)

	go func() {
		time.Sleep(5 * time.Millisecond)
		fmt.Println("  Cancelling pipeline...")
		pipeline2.Cancel()
	}()

	stats2 := pipeline2.Run()
	fmt.Printf("  Processed before cancel: %d files\n", stats2.FileCount)
	fmt.Printf("  Time until cancel: %v\n", stats2.TotalTime.Round(time.Millisecond))
}
