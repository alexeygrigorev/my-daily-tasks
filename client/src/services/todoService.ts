import { Todo } from "@/types/todo";

// API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:3000";

class TodoService {
  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        error: "HTTP_ERROR",
        message: `Request failed with status ${response.status}`,
      }));
      throw new Error(error.message || "Request failed");
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return undefined as T;
    }

    return response.json();
  }

  async getAllTodos(filters?: {
    dueBefore?: Date;
    tags?: string[];
  }): Promise<Todo[]> {
    const params = new URLSearchParams();

    if (filters?.dueBefore) {
      params.append("dueBefore", filters.dueBefore.toISOString());
    }

    if (filters?.tags && filters.tags.length > 0) {
      params.append("tags", filters.tags.join(","));
    }

    const queryString = params.toString();
    const endpoint = `/api/todos${queryString ? `?${queryString}` : ""}`;

    const todos = await this.request<Todo[]>(endpoint);

    // Convert date strings back to Date objects
    return todos.map((todo) => ({
      ...todo,
      dueDate: todo.dueDate ? new Date(todo.dueDate) : undefined,
      createdAt: new Date(todo.createdAt),
    }));
  }

  async createTodo(
    text: string,
    dueDate?: Date,
    tags?: string[]
  ): Promise<Todo> {
    const todo = await this.request<Todo>("/api/todos", {
      method: "POST",
      body: JSON.stringify({
        text,
        dueDate: dueDate?.toISOString(),
        tags: tags || [],
      }),
    });

    // Convert date strings back to Date objects
    return {
      ...todo,
      dueDate: todo.dueDate ? new Date(todo.dueDate) : undefined,
      createdAt: new Date(todo.createdAt),
    };
  }

  async updateTodo(
    id: string,
    updates: Partial<Omit<Todo, "id">>
  ): Promise<Todo> {
    const body: any = { ...updates };

    // Convert Date objects to ISO strings
    if (updates.dueDate !== undefined) {
      body.dueDate = updates.dueDate?.toISOString();
    }

    const todo = await this.request<Todo>(`/api/todos/${id}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    });

    // Convert date strings back to Date objects
    return {
      ...todo,
      dueDate: todo.dueDate ? new Date(todo.dueDate) : undefined,
      createdAt: new Date(todo.createdAt),
    };
  }

  async toggleTodo(id: string): Promise<Todo> {
    const todo = await this.request<Todo>(`/api/todos/${id}/toggle`, {
      method: "POST",
    });

    // Convert date strings back to Date objects
    return {
      ...todo,
      dueDate: todo.dueDate ? new Date(todo.dueDate) : undefined,
      createdAt: new Date(todo.createdAt),
    };
  }

  async deleteTodo(id: string): Promise<void> {
    await this.request<void>(`/api/todos/${id}`, {
      method: "DELETE",
    });
  }
}

// Export singleton instance
export const todoService = new TodoService();
