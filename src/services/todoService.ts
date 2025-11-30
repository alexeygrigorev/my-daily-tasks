import { Todo } from "@/types/todo";

// Mock backend service - all backend interactions centralized here
// Easy to swap with real API calls later

class TodoService {
  private todos: Todo[] = [];

  async getAllTodos(): Promise<Todo[]> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 100));
    return [...this.todos];
  }

  async createTodo(text: string, dueDate?: Date, tags?: string[]): Promise<Todo> {
    await new Promise(resolve => setTimeout(resolve, 100));
    const newTodo: Todo = {
      id: Date.now().toString(),
      text,
      completed: false,
      dueDate,
      tags: tags || [],
      createdAt: new Date(),
    };
    this.todos = [newTodo, ...this.todos];
    return newTodo;
  }

  async updateTodo(id: string, updates: Partial<Omit<Todo, 'id'>>): Promise<Todo> {
    await new Promise(resolve => setTimeout(resolve, 100));
    const index = this.todos.findIndex(todo => todo.id === id);
    if (index === -1) throw new Error('Todo not found');
    
    this.todos[index] = { ...this.todos[index], ...updates };
    return this.todos[index];
  }

  async toggleTodo(id: string): Promise<Todo> {
    await new Promise(resolve => setTimeout(resolve, 100));
    const todo = this.todos.find(t => t.id === id);
    if (!todo) throw new Error('Todo not found');
    
    return this.updateTodo(id, { completed: !todo.completed });
  }

  async deleteTodo(id: string): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, 100));
    this.todos = this.todos.filter(todo => todo.id !== id);
  }
}

// Export singleton instance
export const todoService = new TodoService();
