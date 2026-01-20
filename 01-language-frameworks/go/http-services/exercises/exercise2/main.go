// Exercise 2: Todo CRUD API
//
// Build a complete CRUD API for managing Todo items with proper
// error handling and HTTP status codes.
//
// Requirements:
// 1. Implement these endpoints:
//    - GET    /todos      - List all todos
//    - POST   /todos      - Create a new todo
//    - GET    /todos/{id} - Get a single todo
//    - PUT    /todos/{id} - Update a todo
//    - DELETE /todos/{id} - Delete a todo
//
// 2. Todo structure:
//    - id: string (generated)
//    - title: string (required)
//    - completed: boolean (default: false)
//    - created_at: time.Time
//
// 3. Error handling:
//    - 400 for invalid JSON
//    - 404 for not found
//    - 405 for wrong method
//    - 422 for validation errors (missing title)
//
// 4. Proper status codes:
//    - 200 for successful GET
//    - 201 for successful POST
//    - 204 for successful DELETE
//
// Hints:
// - Use a map[string]*Todo as an in-memory store
// - Use sync.RWMutex for thread-safety
// - Extract ID from path using strings.TrimPrefix

package main

import (
	"fmt"
	"net/http"
)

// Todo represents a todo item
// TODO: Define the struct with proper JSON tags
type Todo struct {
	// Add fields here
}

// TodoStore is the in-memory storage
// TODO: Implement with map and mutex
type TodoStore struct {
	// Add fields here
}

func NewTodoStore() *TodoStore {
	// TODO: Initialize the store
	return &TodoStore{}
}

// TODO: Implement CRUD methods on TodoStore
// - Create(todo *Todo)
// - Get(id string) (*Todo, bool)
// - List() []*Todo
// - Update(id string, todo *Todo) bool
// - Delete(id string) bool

// TodoHandler handles todo-related requests
type TodoHandler struct {
	store *TodoStore
}

func (h *TodoHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	// TODO: Route to appropriate handler based on path and method
	// Hint: Check if path is exactly "/todos" or "/todos/{id}"

	fmt.Fprintln(w, "Implement your solution")
}

// TODO: Implement individual handlers
// - listTodos(w, r)
// - createTodo(w, r)
// - getTodo(w, r, id)
// - updateTodo(w, r, id)
// - deleteTodo(w, r, id)

func main() {
	store := NewTodoStore()
	handler := &TodoHandler{store: store}

	http.Handle("/todos", handler)
	http.Handle("/todos/", handler)

	fmt.Println("Exercise 2: Todo CRUD API")
	fmt.Println("Starting server on http://localhost:8080")
	fmt.Println()
	fmt.Println("Test commands:")
	fmt.Println(`  curl http://localhost:8080/todos`)
	fmt.Println(`  curl -X POST http://localhost:8080/todos -d '{"title":"Learn Go"}'`)
	fmt.Println(`  curl http://localhost:8080/todos/{id}`)
	fmt.Println(`  curl -X PUT http://localhost:8080/todos/{id} -d '{"completed":true}'`)
	fmt.Println(`  curl -X DELETE http://localhost:8080/todos/{id}`)

	http.ListenAndServe(":8080", nil)
}
