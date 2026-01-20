// Exercise 3: CI Configuration
//
// Sample production code to lint. This code follows best practices.
package main

import (
	"context"
	"errors"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"
)

func main() {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Handle graceful shutdown
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		<-sigCh
		log.Println("Received shutdown signal")
		cancel()
	}()

	if err := run(ctx); err != nil {
		log.Printf("Application error: %v", err)
		os.Exit(1)
	}
}

func run(ctx context.Context) error {
	// Initialize service
	svc, err := NewService()
	if err != nil {
		return fmt.Errorf("creating service: %w", err)
	}
	defer func() {
		if err := svc.Close(); err != nil {
			log.Printf("Error closing service: %v", err)
		}
	}()

	// Process with context
	return svc.Process(ctx)
}

// Service represents an application service
type Service struct {
	startTime time.Time
}

// NewService creates a new service instance
func NewService() (*Service, error) {
	return &Service{
		startTime: time.Now(),
	}, nil
}

// Process does the main work
func (s *Service) Process(ctx context.Context) error {
	log.Printf("Service started at %s", s.startTime.Format(time.RFC3339))

	select {
	case <-ctx.Done():
		return ctx.Err()
	case <-time.After(100 * time.Millisecond):
		return s.doWork()
	}
}

func (s *Service) doWork() error {
	// Simulate work
	if time.Since(s.startTime) < 0 {
		return errors.New("invalid start time")
	}
	log.Println("Work completed successfully")
	return nil
}

// Close cleans up service resources
func (s *Service) Close() error {
	log.Println("Service closed")
	return nil
}
