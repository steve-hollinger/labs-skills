// Exercise 2: Fix Linting Issues
//
// This file contains intentional linting issues.
// Your task is to fix them all while maintaining functionality.
//
//nolint:all // Remove this line after fixing the issues!
package main

import (
	"fmt"
	"os"
	"strconv"
)

func main() {
	// Issue 1: Unchecked error
	file, _ := os.Open("config.txt")
	fmt.Println(file)

	// Issue 2: Unused variable
	unusedValue := "this is never used"

	// Issue 3: Ineffectual assignment
	result := "initial"
	result = "replaced immediately"
	fmt.Println(result)

	// Issue 4: Shadow variable
	err := processItems()
	if err != nil {
		// This shadows the outer err
		err := handleError(err)
		fmt.Println(err)
	}

	// Issue 5: Can be simplified
	isEnabled := true
	if isEnabled == true {
		fmt.Println("Enabled")
	}

	// Issue 6: Unchecked type assertion
	var data interface{} = "hello"
	str := data.(string)
	fmt.Println(str)

	// Issue 7: Printf format issue
	count := 42
	fmt.Printf("Count: %s\n", count)

	// Keep the unused variable reference to avoid compile error
	_ = unusedValue
}

func processItems() error {
	// Issue 8: Unchecked error from strconv
	num, _ := strconv.Atoi("not a number")
	fmt.Printf("Converted: %d\n", num)
	return nil
}

func handleError(err error) error {
	return fmt.Errorf("handled: %w", err)
}
