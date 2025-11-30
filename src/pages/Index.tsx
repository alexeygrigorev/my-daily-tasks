import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { TodoItem, type Todo } from "@/components/TodoItem";
import { Plus, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";

const Index = () => {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [inputValue, setInputValue] = useState("");

  const handleAddTodo = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) {
      toast.error("Please enter a task");
      return;
    }

    const newTodo: Todo = {
      id: Date.now().toString(),
      text: inputValue.trim(),
      completed: false,
    };

    setTodos([newTodo, ...todos]);
    setInputValue("");
    toast.success("Task added!");
  };

  const handleToggleTodo = (id: string) => {
    setTodos(
      todos.map((todo) =>
        todo.id === id ? { ...todo, completed: !todo.completed } : todo
      )
    );
  };

  const handleDeleteTodo = (id: string) => {
    setTodos(todos.filter((todo) => todo.id !== id));
    toast.success("Task deleted");
  };

  const completedCount = todos.filter((todo) => todo.completed).length;
  const totalCount = todos.length;

  return (
    <div className="min-h-screen bg-background py-8 px-4 sm:px-6 lg:px-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-2xl mx-auto"
      >
        <div className="text-center mb-8">
          <h1 className="text-5xl sm:text-6xl font-bold mb-3 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            My Tasks
          </h1>
          <p className="text-muted-foreground text-lg">
            Stay organized, get things done
          </p>
          {totalCount > 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-secondary rounded-full text-sm font-medium"
            >
              <CheckCircle2 className="h-4 w-4 text-primary" />
              {completedCount} of {totalCount} completed
            </motion.div>
          )}
        </div>

        <form onSubmit={handleAddTodo} className="mb-8">
          <div className="flex gap-2">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="What needs to be done?"
              className="h-12 text-base shadow-sm"
            />
            <Button type="submit" size="lg" className="gap-2 shadow-sm">
              <Plus className="h-5 w-5" />
              Add
            </Button>
          </div>
        </form>

        <div className="space-y-2">
          <AnimatePresence mode="popLayout">
            {todos.length === 0 ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-center py-16"
              >
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-secondary mb-4">
                  <CheckCircle2 className="h-10 w-10 text-muted-foreground" />
                </div>
                <h3 className="text-xl font-semibold mb-2">No tasks yet</h3>
                <p className="text-muted-foreground">
                  Add your first task to get started!
                </p>
              </motion.div>
            ) : (
              todos.map((todo) => (
                <TodoItem
                  key={todo.id}
                  todo={todo}
                  onToggle={handleToggleTodo}
                  onDelete={handleDeleteTodo}
                />
              ))
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  );
};

export default Index;
