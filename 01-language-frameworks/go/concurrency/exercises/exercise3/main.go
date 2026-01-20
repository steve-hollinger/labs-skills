// Exercise 3: File Processing Pipeline
//
// Build a concurrent pipeline that processes files through multiple stages:
// 1. Discovery: Find all files matching a pattern
// 2. Reading: Read file contents
// 3. Processing: Transform the content
// 4. Aggregation: Combine results
//
// Requirements:
// 1. Pipeline stages:
//    - Discover: Scan directory for files matching pattern
//    - Read: Read file contents concurrently
//    - Process: Count words/lines/characters
//    - Aggregate: Sum up statistics
//
// 2. Features:
//    - Support context cancellation
//    - Fan-out for parallel file reading
//    - Fan-in for result collection
//    - Error handling at each stage
//
// 3. Statistics to track:
//    - File count
//    - Total bytes
//    - Total lines
//    - Total words
//    - Processing time per file
//
// Hints:
// - Use filepath.Walk or os.ReadDir for discovery
// - Use io.ReadAll for reading
// - Use strings.Fields for word counting
// - Use sync.WaitGroup for fan-out coordination

package main

import (
	"context"
	"fmt"
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
		// TODO: Implement file discovery
		// 1. Walk the directory tree
		// 2. Match files against pattern
		// 3. Send FileInfo to channel
		// 4. Respect context cancellation

		fmt.Println("  Discovery: not implemented")
	}()

	return out
}

// Read reads file contents concurrently
func (p *Pipeline) Read(files <-chan FileInfo) <-chan FileContent {
	out := make(chan FileContent)

	go func() {
		defer close(out)
		// TODO: Implement concurrent file reading
		// 1. Fan-out to p.workers goroutines
		// 2. Each worker reads files from input channel
		// 3. Send FileContent to output channel
		// 4. Handle errors gracefully

		fmt.Println("  Read: not implemented")
	}()

	return out
}

// Process analyzes file contents
func (p *Pipeline) Process(contents <-chan FileContent) <-chan FileStats {
	out := make(chan FileStats)

	go func() {
		defer close(out)
		// TODO: Implement content processing
		// 1. For each file, calculate:
		//    - Byte count
		//    - Line count
		//    - Word count
		// 2. Track processing duration
		// 3. Handle errors

		fmt.Println("  Process: not implemented")
	}()

	return out
}

// Aggregate combines all statistics
func (p *Pipeline) Aggregate(stats <-chan FileStats) AggregateStats {
	// TODO: Implement aggregation
	// 1. Sum up all statistics
	// 2. Count errors
	// 3. Return aggregate

	return AggregateStats{}
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
	fmt.Println("Exercise 3: File Processing Pipeline")
	fmt.Println("=====================================")
	fmt.Println()

	// Process Go files in current directory
	pipeline := NewPipeline(".", "*.go", 4)

	fmt.Println("Running pipeline with 4 workers...")
	fmt.Println()

	start := time.Now()
	stats := pipeline.Run()
	elapsed := time.Since(start)

	fmt.Println()
	fmt.Println("Results:")
	fmt.Printf("  Files processed: %d\n", stats.FileCount)
	fmt.Printf("  Files skipped:   %d\n", stats.FilesSkipped)
	fmt.Printf("  Errors:          %d\n", stats.ErrorCount)
	fmt.Printf("  Total bytes:     %d\n", stats.TotalBytes)
	fmt.Printf("  Total lines:     %d\n", stats.TotalLines)
	fmt.Printf("  Total words:     %d\n", stats.TotalWords)
	fmt.Printf("  Pipeline time:   %v\n", elapsed)

	// Bonus: Test cancellation
	fmt.Println()
	fmt.Println("Testing cancellation...")

	pipeline2 := NewPipeline(".", "*.go", 4)
	go func() {
		time.Sleep(10 * time.Millisecond)
		pipeline2.Cancel()
	}()

	stats2 := pipeline2.Run()
	fmt.Printf("  Processed before cancel: %d files\n", stats2.FileCount)
}
