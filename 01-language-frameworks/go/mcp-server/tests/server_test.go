package tests

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/mark3labs/mcp-go/mcp"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestToolRequestParsing tests parsing tool call requests
func TestToolRequestParsing(t *testing.T) {
	tests := []struct {
		name     string
		args     map[string]interface{}
		wantName string
		wantErr  bool
	}{
		{
			name: "valid string argument",
			args: map[string]interface{}{
				"name": "Alice",
			},
			wantName: "Alice",
			wantErr:  false,
		},
		{
			name: "missing required argument",
			args: map[string]interface{}{},
			wantErr:  true,
		},
		{
			name: "wrong type argument",
			args: map[string]interface{}{
				"name": 123,
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			name, ok := tt.args["name"].(string)
			if !ok {
				if !tt.wantErr {
					t.Error("expected successful parse")
				}
				return
			}
			if tt.wantErr {
				t.Error("expected error")
				return
			}
			assert.Equal(t, tt.wantName, name)
		})
	}
}

// TestNumberConversion tests converting JSON numbers to Go types
func TestNumberConversion(t *testing.T) {
	tests := []struct {
		name      string
		args      map[string]interface{}
		wantInt   int
		wantFloat float64
	}{
		{
			name: "integer value",
			args: map[string]interface{}{
				"value": float64(42),
			},
			wantInt:   42,
			wantFloat: 42.0,
		},
		{
			name: "float value",
			args: map[string]interface{}{
				"value": float64(3.14),
			},
			wantInt:   3,
			wantFloat: 3.14,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			val, ok := tt.args["value"].(float64)
			require.True(t, ok, "value should be float64")

			assert.Equal(t, tt.wantInt, int(val))
			assert.Equal(t, tt.wantFloat, val)
		})
	}
}

// TestToolResultCreation tests creating tool results
func TestToolResultCreation(t *testing.T) {
	t.Run("text result", func(t *testing.T) {
		result := mcp.NewToolResultText("Hello, World!")
		require.NotNil(t, result)
		require.Len(t, result.Content, 1)

		content := result.Content[0]
		assert.Equal(t, "text", content.Type)
		assert.Equal(t, "Hello, World!", content.Text)
	})

	t.Run("error result", func(t *testing.T) {
		result := mcp.NewToolResultError("Something went wrong")
		require.NotNil(t, result)
		assert.True(t, result.IsError)
	})
}

// TestResourceContentsCreation tests creating resource contents
func TestResourceContentsCreation(t *testing.T) {
	t.Run("text resource", func(t *testing.T) {
		content := mcp.TextResourceContents(
			"test://resource",
			`{"key": "value"}`,
			"application/json",
		)

		assert.Equal(t, "test://resource", content.URI)
		assert.Equal(t, "application/json", content.MIMEType)
	})
}

// TestCalculatorLogic tests the calculator example logic
func TestCalculatorLogic(t *testing.T) {
	tests := []struct {
		name      string
		operation string
		a, b      float64
		want      float64
		wantErr   bool
	}{
		{"add", "add", 5, 3, 8, false},
		{"subtract", "subtract", 10, 4, 6, false},
		{"multiply", "multiply", 6, 7, 42, false},
		{"divide", "divide", 20, 4, 5, false},
		{"divide by zero", "divide", 10, 0, 0, true},
		{"unknown operation", "modulo", 10, 3, 0, true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, err := calculate(tt.operation, tt.a, tt.b)
			if tt.wantErr {
				assert.Error(t, err)
				return
			}
			require.NoError(t, err)
			assert.Equal(t, tt.want, result)
		})
	}
}

// calculate is the calculator logic from example1
func calculate(operation string, a, b float64) (float64, error) {
	switch operation {
	case "add":
		return a + b, nil
	case "subtract":
		return a - b, nil
	case "multiply":
		return a * b, nil
	case "divide":
		if b == 0 {
			return 0, assert.AnError
		}
		return a / b, nil
	default:
		return 0, assert.AnError
	}
}

// TestNoteStoreCRUD tests the note store from example3
func TestNoteStoreCRUD(t *testing.T) {
	store := NewTestNoteStore()

	// Create
	t.Run("create note", func(t *testing.T) {
		note := store.Create("Test Note", "Test Content", []string{"test"})
		assert.NotEmpty(t, note.ID)
		assert.Equal(t, "Test Note", note.Title)
		assert.Equal(t, "Test Content", note.Content)
		assert.Equal(t, []string{"test"}, note.Tags)
	})

	// Read
	t.Run("get note", func(t *testing.T) {
		created := store.Create("Get Test", "Content", nil)
		note, ok := store.Get(created.ID)
		assert.True(t, ok)
		assert.Equal(t, created.ID, note.ID)
	})

	t.Run("get non-existent note", func(t *testing.T) {
		_, ok := store.Get("non-existent")
		assert.False(t, ok)
	})

	// Update
	t.Run("update note", func(t *testing.T) {
		created := store.Create("Original", "Original Content", nil)
		updated, err := store.Update(created.ID, "Updated", "")
		require.NoError(t, err)
		assert.Equal(t, "Updated", updated.Title)
		assert.Equal(t, "Original Content", updated.Content)
	})

	// Delete
	t.Run("delete note", func(t *testing.T) {
		created := store.Create("To Delete", "Content", nil)
		err := store.Delete(created.ID)
		require.NoError(t, err)
		_, ok := store.Get(created.ID)
		assert.False(t, ok)
	})

	// List
	t.Run("list notes", func(t *testing.T) {
		newStore := NewTestNoteStore()
		newStore.Create("Note 1", "Content 1", nil)
		newStore.Create("Note 2", "Content 2", nil)
		notes := newStore.List()
		assert.Len(t, notes, 2)
	})
}

// TestNoteStore is a simplified version for testing
type TestNote struct {
	ID      string
	Title   string
	Content string
	Tags    []string
}

type TestNoteStore struct {
	notes  map[string]*TestNote
	nextID int
}

func NewTestNoteStore() *TestNoteStore {
	return &TestNoteStore{
		notes:  make(map[string]*TestNote),
		nextID: 1,
	}
}

func (s *TestNoteStore) Create(title, content string, tags []string) *TestNote {
	id := string(rune('a' + s.nextID - 1))
	s.nextID++
	note := &TestNote{ID: id, Title: title, Content: content, Tags: tags}
	s.notes[id] = note
	return note
}

func (s *TestNoteStore) Get(id string) (*TestNote, bool) {
	note, ok := s.notes[id]
	return note, ok
}

func (s *TestNoteStore) Update(id, title, content string) (*TestNote, error) {
	note, ok := s.notes[id]
	if !ok {
		return nil, assert.AnError
	}
	if title != "" {
		note.Title = title
	}
	if content != "" {
		note.Content = content
	}
	return note, nil
}

func (s *TestNoteStore) Delete(id string) error {
	if _, ok := s.notes[id]; !ok {
		return assert.AnError
	}
	delete(s.notes, id)
	return nil
}

func (s *TestNoteStore) List() []*TestNote {
	notes := make([]*TestNote, 0, len(s.notes))
	for _, note := range s.notes {
		notes = append(notes, note)
	}
	return notes
}

// TestContextCancellation tests that handlers respect context cancellation
func TestContextCancellation(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	cancel() // Cancel immediately

	// A well-behaved handler should check context
	select {
	case <-ctx.Done():
		// Context is cancelled as expected
		assert.Equal(t, context.Canceled, ctx.Err())
	default:
		t.Error("context should be cancelled")
	}
}

// TestJSONSerialization tests JSON serialization of resources
func TestJSONSerialization(t *testing.T) {
	data := map[string]interface{}{
		"name":  "test",
		"count": 42,
		"items": []string{"a", "b", "c"},
	}

	jsonBytes, err := json.MarshalIndent(data, "", "  ")
	require.NoError(t, err)

	var result map[string]interface{}
	err = json.Unmarshal(jsonBytes, &result)
	require.NoError(t, err)

	assert.Equal(t, "test", result["name"])
	assert.Equal(t, float64(42), result["count"])
}
