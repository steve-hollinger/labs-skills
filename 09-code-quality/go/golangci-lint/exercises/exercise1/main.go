// Exercise 1: Configure Basic Linting
//
// This file contains clean code that should pass linting.
// Your task is to create a .golangci.yml configuration file.
package main

import (
	"errors"
	"fmt"
	"os"
)

func main() {
	if err := run(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}

func run() error {
	// Process some data
	result, err := processData("hello")
	if err != nil {
		return fmt.Errorf("processing data: %w", err)
	}

	fmt.Printf("Result: %s\n", result)
	return nil
}

func processData(input string) (string, error) {
	if input == "" {
		return "", errors.New("input cannot be empty")
	}

	// Do some processing
	output := fmt.Sprintf("Processed: %s", input)
	return output, nil
}
