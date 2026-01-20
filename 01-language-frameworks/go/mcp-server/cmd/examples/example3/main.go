// Example 3: Full-Featured MCP Server
//
// This example demonstrates a complete MCP server with tools, resources,
// and proper error handling. It simulates a note-taking application.
//
// Key concepts:
// - Combining tools and resources in one server
// - Proper input validation and error handling
// - Stateful operations (CRUD for notes)
// - Context-aware operations
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
)

// Note represents a note in our system
type Note struct {
	ID        string    `json:"id"`
	Title     string    `json:"title"`
	Content   string    `json:"content"`
	Tags      []string  `json:"tags"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// NoteStore manages notes with thread-safe operations
type NoteStore struct {
	mu     sync.RWMutex
	notes  map[string]*Note
	nextID int
}

func NewNoteStore() *NoteStore {
	store := &NoteStore{
		notes:  make(map[string]*Note),
		nextID: 1,
	}

	// Add some sample notes
	store.Create("Welcome Note", "Welcome to the MCP Notes server!", []string{"welcome", "intro"})
	store.Create("Meeting Notes", "Discuss MCP implementation details", []string{"meeting", "work"})
	store.Create("Ideas", "Build more MCP examples", []string{"ideas", "dev"})

	return store
}

func (s *NoteStore) Create(title, content string, tags []string) *Note {
	s.mu.Lock()
	defer s.mu.Unlock()

	id := fmt.Sprintf("note-%d", s.nextID)
	s.nextID++

	note := &Note{
		ID:        id,
		Title:     title,
		Content:   content,
		Tags:      tags,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	s.notes[id] = note
	return note
}

func (s *NoteStore) Get(id string) (*Note, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	note, ok := s.notes[id]
	return note, ok
}

func (s *NoteStore) Update(id, title, content string) (*Note, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	note, ok := s.notes[id]
	if !ok {
		return nil, fmt.Errorf("note not found: %s", id)
	}

	if title != "" {
		note.Title = title
	}
	if content != "" {
		note.Content = content
	}
	note.UpdatedAt = time.Now()

	return note, nil
}

func (s *NoteStore) Delete(id string) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	if _, ok := s.notes[id]; !ok {
		return fmt.Errorf("note not found: %s", id)
	}

	delete(s.notes, id)
	return nil
}

func (s *NoteStore) List() []*Note {
	s.mu.RLock()
	defer s.mu.RUnlock()

	notes := make([]*Note, 0, len(s.notes))
	for _, note := range s.notes {
		notes = append(notes, note)
	}
	return notes
}

func (s *NoteStore) Search(query string) []*Note {
	s.mu.RLock()
	defer s.mu.RUnlock()

	query = strings.ToLower(query)
	var results []*Note

	for _, note := range s.notes {
		if strings.Contains(strings.ToLower(note.Title), query) ||
			strings.Contains(strings.ToLower(note.Content), query) {
			results = append(results, note)
		}
	}

	return results
}

var store = NewNoteStore()

func main() {
	if len(os.Args) > 1 && os.Args[1] == "--demo" {
		runDemo()
		return
	}

	// Create server with both tool and resource capabilities
	s := server.NewMCPServer(
		"notes-server",
		"1.0.0",
		server.WithToolCapabilities(true),
		server.WithResourceCapabilities(true, false),
	)

	// Add tools for note operations
	addCreateNoteTool(s)
	addUpdateNoteTool(s)
	addDeleteNoteTool(s)
	addSearchNotesTool(s)

	// Add resources for reading notes
	addNotesListResource(s)
	addNoteResourceTemplate(s)

	fmt.Fprintln(os.Stderr, "Notes MCP Server starting...")
	fmt.Fprintln(os.Stderr, "Tools: create_note, update_note, delete_note, search_notes")
	fmt.Fprintln(os.Stderr, "Resources: notes://list, notes://{id}")
	fmt.Fprintln(os.Stderr, "Listening on stdio...")

	if err := s.ServeStdio(); err != nil {
		log.Fatalf("Server error: %v", err)
	}
}

// Tools

func addCreateNoteTool(s *server.MCPServer) {
	tool := mcp.NewTool("create_note",
		mcp.WithDescription("Create a new note"),
		mcp.WithString("title",
			mcp.Required(),
			mcp.Description("The title of the note"),
		),
		mcp.WithString("content",
			mcp.Required(),
			mcp.Description("The content of the note"),
		),
		mcp.WithArray("tags",
			mcp.Description("Tags for the note"),
		),
	)

	s.AddTool(tool, func(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		title, ok := req.Params.Arguments["title"].(string)
		if !ok || title == "" {
			return mcp.NewToolResultError("title is required"), nil
		}

		content, ok := req.Params.Arguments["content"].(string)
		if !ok {
			content = ""
		}

		var tags []string
		if tagsRaw, ok := req.Params.Arguments["tags"].([]interface{}); ok {
			for _, t := range tagsRaw {
				if tag, ok := t.(string); ok {
					tags = append(tags, tag)
				}
			}
		}

		note := store.Create(title, content, tags)

		data, _ := json.MarshalIndent(note, "", "  ")
		return mcp.NewToolResultText(fmt.Sprintf("Note created:\n%s", string(data))), nil
	})
}

func addUpdateNoteTool(s *server.MCPServer) {
	tool := mcp.NewTool("update_note",
		mcp.WithDescription("Update an existing note"),
		mcp.WithString("id",
			mcp.Required(),
			mcp.Description("The ID of the note to update"),
		),
		mcp.WithString("title",
			mcp.Description("New title (optional)"),
		),
		mcp.WithString("content",
			mcp.Description("New content (optional)"),
		),
	)

	s.AddTool(tool, func(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		id, ok := req.Params.Arguments["id"].(string)
		if !ok || id == "" {
			return mcp.NewToolResultError("id is required"), nil
		}

		title, _ := req.Params.Arguments["title"].(string)
		content, _ := req.Params.Arguments["content"].(string)

		if title == "" && content == "" {
			return mcp.NewToolResultError("at least one of title or content must be provided"), nil
		}

		note, err := store.Update(id, title, content)
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}

		data, _ := json.MarshalIndent(note, "", "  ")
		return mcp.NewToolResultText(fmt.Sprintf("Note updated:\n%s", string(data))), nil
	})
}

func addDeleteNoteTool(s *server.MCPServer) {
	tool := mcp.NewTool("delete_note",
		mcp.WithDescription("Delete a note"),
		mcp.WithString("id",
			mcp.Required(),
			mcp.Description("The ID of the note to delete"),
		),
	)

	s.AddTool(tool, func(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		id, ok := req.Params.Arguments["id"].(string)
		if !ok || id == "" {
			return mcp.NewToolResultError("id is required"), nil
		}

		if err := store.Delete(id); err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}

		return mcp.NewToolResultText(fmt.Sprintf("Note %s deleted successfully", id)), nil
	})
}

func addSearchNotesTool(s *server.MCPServer) {
	tool := mcp.NewTool("search_notes",
		mcp.WithDescription("Search notes by title or content"),
		mcp.WithString("query",
			mcp.Required(),
			mcp.Description("Search query"),
		),
	)

	s.AddTool(tool, func(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		query, ok := req.Params.Arguments["query"].(string)
		if !ok || query == "" {
			return mcp.NewToolResultError("query is required"), nil
		}

		results := store.Search(query)

		if len(results) == 0 {
			return mcp.NewToolResultText("No notes found matching your query."), nil
		}

		response := map[string]interface{}{
			"count":   len(results),
			"results": results,
		}

		data, _ := json.MarshalIndent(response, "", "  ")
		return mcp.NewToolResultText(string(data)), nil
	})
}

// Resources

func addNotesListResource(s *server.MCPServer) {
	resource := mcp.NewResource(
		"notes://list",
		"List of all notes",
		mcp.WithResourceDescription("Get all notes in the system"),
		mcp.WithMIMEType("application/json"),
	)

	s.AddResource(resource, func(ctx context.Context, req mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
		notes := store.List()

		response := map[string]interface{}{
			"total": len(notes),
			"notes": notes,
		}

		data, err := json.MarshalIndent(response, "", "  ")
		if err != nil {
			return nil, fmt.Errorf("failed to serialize notes: %w", err)
		}

		return []mcp.ResourceContents{
			mcp.TextResourceContents(req.Params.URI, string(data), "application/json"),
		}, nil
	})
}

func addNoteResourceTemplate(s *server.MCPServer) {
	template := mcp.NewResourceTemplate(
		"notes://{id}",
		"Individual note by ID",
		mcp.WithTemplateDescription("Retrieve a specific note by its ID"),
		mcp.WithTemplateMIMEType("application/json"),
	)

	s.AddResourceTemplate(template, func(ctx context.Context, req mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
		// Extract ID from URI: notes://note-1
		uri := req.Params.URI
		parts := strings.Split(uri, "://")
		if len(parts) != 2 {
			return nil, fmt.Errorf("invalid URI format: %s", uri)
		}

		id := parts[1]

		note, ok := store.Get(id)
		if !ok {
			return nil, fmt.Errorf("note not found: %s", id)
		}

		data, err := json.MarshalIndent(note, "", "  ")
		if err != nil {
			return nil, fmt.Errorf("failed to serialize note: %w", err)
		}

		return []mcp.ResourceContents{
			mcp.TextResourceContents(req.Params.URI, string(data), "application/json"),
		}, nil
	})
}

func runDemo() {
	fmt.Println("Example 3: Full-Featured Notes Server")
	fmt.Println("=" + strings.Repeat("=", 49))
	fmt.Println()
	fmt.Println("This example demonstrates a complete MCP server with tools and resources.")
	fmt.Println()
	fmt.Println("Tools (for modifying data):")
	fmt.Println("----------------------------")
	fmt.Println("1. create_note")
	fmt.Println("   Create a new note with title, content, and tags")
	fmt.Println()
	fmt.Println("2. update_note")
	fmt.Println("   Update an existing note's title or content")
	fmt.Println()
	fmt.Println("3. delete_note")
	fmt.Println("   Delete a note by ID")
	fmt.Println()
	fmt.Println("4. search_notes")
	fmt.Println("   Search notes by title or content")
	fmt.Println()
	fmt.Println("Resources (for reading data):")
	fmt.Println("------------------------------")
	fmt.Println("1. notes://list")
	fmt.Println("   Get all notes")
	fmt.Println()
	fmt.Println("2. notes://{id}")
	fmt.Println("   Get a specific note by ID")
	fmt.Println()
	fmt.Println("Sample Notes:")
	for _, note := range store.List() {
		fmt.Printf("   - %s: %s\n", note.ID, note.Title)
	}
	fmt.Println()
	fmt.Println("Run without --demo flag to start the actual server.")
}
