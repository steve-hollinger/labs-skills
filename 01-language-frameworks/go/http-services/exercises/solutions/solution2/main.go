// Solution for Exercise 2: Todo CRUD API
//
// This solution demonstrates a complete RESTful API with proper
// error handling, status codes, and thread-safe storage.

package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"sync"
	"time"
)

// Todo represents a todo item
type Todo struct {
	ID        string    `json:"id"`
	Title     string    `json:"title"`
	Completed bool      `json:"completed"`
	CreatedAt time.Time `json:"created_at"`
}

// CreateTodoRequest is the request for creating a todo
type CreateTodoRequest struct {
	Title string `json:"title"`
}

// UpdateTodoRequest is the request for updating a todo
type UpdateTodoRequest struct {
	Title     *string `json:"title,omitempty"`
	Completed *bool   `json:"completed,omitempty"`
}

// TodoStore is the in-memory storage
type TodoStore struct {
	mu     sync.RWMutex
	todos  map[string]*Todo
	nextID int
}

func NewTodoStore() *TodoStore {
	return &TodoStore{
		todos:  make(map[string]*Todo),
		nextID: 1,
	}
}

func (s *TodoStore) Create(title string) *Todo {
	s.mu.Lock()
	defer s.mu.Unlock()

	todo := &Todo{
		ID:        fmt.Sprintf("todo_%d", s.nextID),
		Title:     title,
		Completed: false,
		CreatedAt: time.Now(),
	}
	s.nextID++
	s.todos[todo.ID] = todo
	return todo
}

func (s *TodoStore) Get(id string) (*Todo, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	todo, ok := s.todos[id]
	return todo, ok
}

func (s *TodoStore) List() []*Todo {
	s.mu.RLock()
	defer s.mu.RUnlock()

	todos := make([]*Todo, 0, len(s.todos))
	for _, t := range s.todos {
		todos = append(todos, t)
	}
	return todos
}

func (s *TodoStore) Update(id string, title *string, completed *bool) (*Todo, bool) {
	s.mu.Lock()
	defer s.mu.Unlock()

	todo, ok := s.todos[id]
	if !ok {
		return nil, false
	}

	if title != nil {
		todo.Title = *title
	}
	if completed != nil {
		todo.Completed = *completed
	}

	return todo, true
}

func (s *TodoStore) Delete(id string) bool {
	s.mu.Lock()
	defer s.mu.Unlock()

	if _, ok := s.todos[id]; !ok {
		return false
	}
	delete(s.todos, id)
	return true
}

// Response helpers
func writeJSON(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(data)
}

func writeError(w http.ResponseWriter, status int, message string) {
	writeJSON(w, status, map[string]string{"error": message})
}

// TodoHandler handles todo-related requests
type TodoHandler struct {
	store *TodoStore
}

func (h *TodoHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	path := r.URL.Path

	// Check if accessing collection (/todos) or single resource (/todos/{id})
	if path == "/todos" || path == "/todos/" {
		h.handleCollection(w, r)
		return
	}

	// Extract ID from path
	id := strings.TrimPrefix(path, "/todos/")
	if id == "" {
		writeError(w, http.StatusBadRequest, "Todo ID required")
		return
	}

	h.handleSingle(w, r, id)
}

func (h *TodoHandler) handleCollection(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		h.listTodos(w, r)
	case http.MethodPost:
		h.createTodo(w, r)
	default:
		writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
	}
}

func (h *TodoHandler) handleSingle(w http.ResponseWriter, r *http.Request, id string) {
	switch r.Method {
	case http.MethodGet:
		h.getTodo(w, r, id)
	case http.MethodPut:
		h.updateTodo(w, r, id)
	case http.MethodDelete:
		h.deleteTodo(w, r, id)
	default:
		writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
	}
}

func (h *TodoHandler) listTodos(w http.ResponseWriter, r *http.Request) {
	todos := h.store.List()
	writeJSON(w, http.StatusOK, map[string]interface{}{
		"todos": todos,
		"count": len(todos),
	})
}

func (h *TodoHandler) createTodo(w http.ResponseWriter, r *http.Request) {
	var req CreateTodoRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "Invalid JSON")
		return
	}
	defer r.Body.Close()

	// Validate required fields
	if strings.TrimSpace(req.Title) == "" {
		writeJSON(w, http.StatusUnprocessableEntity, map[string]interface{}{
			"error": "Validation failed",
			"details": []map[string]string{
				{"field": "title", "message": "is required"},
			},
		})
		return
	}

	todo := h.store.Create(req.Title)
	writeJSON(w, http.StatusCreated, todo)
}

func (h *TodoHandler) getTodo(w http.ResponseWriter, r *http.Request, id string) {
	todo, ok := h.store.Get(id)
	if !ok {
		writeError(w, http.StatusNotFound, "Todo not found")
		return
	}
	writeJSON(w, http.StatusOK, todo)
}

func (h *TodoHandler) updateTodo(w http.ResponseWriter, r *http.Request, id string) {
	var req UpdateTodoRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "Invalid JSON")
		return
	}
	defer r.Body.Close()

	// Validate title if provided
	if req.Title != nil && strings.TrimSpace(*req.Title) == "" {
		writeJSON(w, http.StatusUnprocessableEntity, map[string]interface{}{
			"error": "Validation failed",
			"details": []map[string]string{
				{"field": "title", "message": "cannot be empty"},
			},
		})
		return
	}

	todo, ok := h.store.Update(id, req.Title, req.Completed)
	if !ok {
		writeError(w, http.StatusNotFound, "Todo not found")
		return
	}
	writeJSON(w, http.StatusOK, todo)
}

func (h *TodoHandler) deleteTodo(w http.ResponseWriter, r *http.Request, id string) {
	if !h.store.Delete(id) {
		writeError(w, http.StatusNotFound, "Todo not found")
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

func main() {
	store := NewTodoStore()
	handler := &TodoHandler{store: store}

	http.Handle("/todos", handler)
	http.Handle("/todos/", handler)

	fmt.Println("Solution 2: Todo CRUD API")
	fmt.Println("Starting server on http://localhost:8080")
	fmt.Println()
	fmt.Println("Test commands:")
	fmt.Println("  # List all todos")
	fmt.Println("  curl http://localhost:8080/todos")
	fmt.Println()
	fmt.Println("  # Create a todo")
	fmt.Println(`  curl -X POST http://localhost:8080/todos -H "Content-Type: application/json" -d '{"title":"Learn Go"}'`)
	fmt.Println()
	fmt.Println("  # Get a specific todo (replace {id} with actual ID)")
	fmt.Println("  curl http://localhost:8080/todos/todo_1")
	fmt.Println()
	fmt.Println("  # Update a todo")
	fmt.Println(`  curl -X PUT http://localhost:8080/todos/todo_1 -H "Content-Type: application/json" -d '{"completed":true}'`)
	fmt.Println()
	fmt.Println("  # Delete a todo")
	fmt.Println("  curl -X DELETE http://localhost:8080/todos/todo_1")
	fmt.Println()

	if err := http.ListenAndServe(":8080", nil); err != nil {
		fmt.Printf("Server error: %v\n", err)
	}
}
