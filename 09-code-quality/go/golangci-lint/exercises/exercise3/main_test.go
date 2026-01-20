package main

import (
	"context"
	"testing"
	"time"
)

func TestNewService(t *testing.T) {
	svc, err := NewService()
	if err != nil {
		t.Fatalf("NewService() error = %v", err)
	}
	if svc == nil {
		t.Fatal("NewService() returned nil")
	}
	// Test files often don't check Close errors
	svc.Close()
}

func TestService_Process(t *testing.T) {
	svc, _ := NewService() // Test files can skip error checks

	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()

	err := svc.Process(ctx)
	if err != nil {
		t.Errorf("Process() error = %v", err)
	}
}

func TestService_Process_Cancelled(t *testing.T) {
	svc, _ := NewService()

	ctx, cancel := context.WithCancel(context.Background())
	cancel() // Cancel immediately

	err := svc.Process(ctx)
	if err != context.Canceled {
		t.Errorf("Process() error = %v, want context.Canceled", err)
	}
}
