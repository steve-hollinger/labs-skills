// Solution 2: Fixed Linting Issues
//
// This file shows the corrected code with explanations.
package main

import (
	"fmt"
	"os"
	"strconv"
)

func main() {
	// FIXED Issue 1: Now checking error from os.Open
	file, err := os.Open("config.txt")
	if err != nil {
		// Handle the error appropriately
		fmt.Printf("Could not open config.txt: %v\n", err)
	} else {
		fmt.Printf("Opened file: %v\n", file.Name())
		// Don't forget to close the file
		if closeErr := file.Close(); closeErr != nil {
			fmt.Printf("Error closing file: %v\n", closeErr)
		}
	}

	// FIXED Issue 2: Removed unused variable
	// The variable unusedValue was removed entirely since it served no purpose

	// FIXED Issue 3: Removed ineffectual assignment
	// Only assign the value that will actually be used
	result := "replaced immediately"
	fmt.Println(result)

	// FIXED Issue 4: Eliminated shadow variable
	if processErr := processItems(); processErr != nil {
		// Use a different variable name to avoid shadowing
		handledErr := handleError(processErr)
		fmt.Println(handledErr)
	}

	// FIXED Issue 5: Simplified boolean comparison
	isEnabled := true
	if isEnabled { // Removed "== true" as it's redundant
		fmt.Println("Enabled")
	}

	// FIXED Issue 6: Check type assertion result
	var data interface{} = "hello"
	str, ok := data.(string)
	if !ok {
		fmt.Println("Type assertion failed")
		return
	}
	fmt.Println(str)

	// FIXED Issue 7: Corrected Printf format
	count := 42
	fmt.Printf("Count: %d\n", count) // Changed %s to %d for integer
}

func processItems() error {
	// FIXED Issue 8: Now checking error from strconv.Atoi
	num, err := strconv.Atoi("not a number")
	if err != nil {
		// Handle the conversion error
		fmt.Printf("Warning: could not convert string to int: %v\n", err)
		num = 0 // Use a default value
	}
	fmt.Printf("Converted: %d\n", num)
	return nil
}

func handleError(err error) error {
	return fmt.Errorf("handled: %w", err)
}

/*
Summary of Fixes:

1. UNCHECKED ERROR (errcheck)
   - Before: file, _ := os.Open("config.txt")
   - After:  file, err := os.Open("config.txt"); if err != nil { ... }
   - Why: Ignoring errors can hide bugs and cause unexpected behavior

2. UNUSED VARIABLE (unused)
   - Before: unusedValue := "this is never used"
   - After:  (removed)
   - Why: Dead code adds maintenance burden and confusion

3. INEFFECTUAL ASSIGNMENT (ineffassign)
   - Before: result := "initial"; result = "replaced"
   - After:  result := "replaced immediately"
   - Why: The first assignment was wasted work

4. SHADOW VARIABLE (govet -shadow)
   - Before: err := ...; if err != nil { err := handleError(err) }
   - After:  processErr := ...; if processErr != nil { handledErr := ... }
   - Why: Shadowing can cause subtle bugs where you think you're
          using one variable but actually using another

5. SIMPLIFICATION (gosimple)
   - Before: if isEnabled == true
   - After:  if isEnabled
   - Why: Comparing a boolean to true is redundant

6. UNCHECKED TYPE ASSERTION (errcheck with check-type-assertions)
   - Before: str := data.(string)
   - After:  str, ok := data.(string); if !ok { ... }
   - Why: Type assertions can panic if the type doesn't match

7. PRINTF FORMAT (govet)
   - Before: fmt.Printf("Count: %s\n", count)  // count is int
   - After:  fmt.Printf("Count: %d\n", count)
   - Why: Wrong format specifier causes incorrect output

8. UNCHECKED ERROR IN STRCONV (errcheck)
   - Before: num, _ := strconv.Atoi("not a number")
   - After:  num, err := strconv.Atoi(...); if err != nil { ... }
   - Why: Conversion errors should be handled appropriately
*/
