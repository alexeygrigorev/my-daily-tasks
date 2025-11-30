import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { TodoItem } from "@/components/TodoItem";
import { Todo } from "@/types/todo";
import { Plus, CheckCircle2, CalendarIcon, X } from "lucide-react";
import { toast } from "sonner";
import { todoService } from "@/services/todoService";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

const Index = () => {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [dueDate, setDueDate] = useState<Date | undefined>();
  const [tagInput, setTagInput] = useState("");
  const [tags, setTags] = useState<string[]>([]);

  useEffect(() => {
    loadTodos();
  }, []);

  const loadTodos = async () => {
    const allTodos = await todoService.getAllTodos();
    setTodos(allTodos);
  };

  const handleAddTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) {
      toast.error("Please enter a task");
      return;
    }

    const newTodo = await todoService.createTodo(inputValue.trim(), dueDate, tags);
    setTodos([newTodo, ...todos]);
    setInputValue("");
    setDueDate(undefined);
    setTags([]);
    toast.success("Task added!");
  };

  const handleToggleTodo = async (id: string) => {
    await todoService.toggleTodo(id);
    setTodos(
      todos.map((todo) =>
        todo.id === id ? { ...todo, completed: !todo.completed } : todo
      )
    );
  };

  const handleDeleteTodo = async (id: string) => {
    await todoService.deleteTodo(id);
    setTodos(todos.filter((todo) => todo.id !== id));
    toast.success("Task deleted");
  };

  const handleUpdateTodo = async (id: string, updates: Partial<Omit<Todo, 'id'>>) => {
    await todoService.updateTodo(id, updates);
    setTodos(
      todos.map((todo) =>
        todo.id === id ? { ...todo, ...updates } : todo
      )
    );
    toast.success("Task updated!");
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setTags([...tags, tagInput.trim()]);
      setTagInput("");
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
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

        <form onSubmit={handleAddTodo} className="mb-8 space-y-3">
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
          
          <div className="flex flex-wrap gap-2">
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  size="sm"
                  className={cn(
                    "gap-2",
                    dueDate && "bg-secondary"
                  )}
                >
                  <CalendarIcon className="h-4 w-4" />
                  {dueDate ? format(dueDate, "MMM d") : "Due date"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  mode="single"
                  selected={dueDate}
                  onSelect={setDueDate}
                  initialFocus
                  className="pointer-events-auto"
                />
              </PopoverContent>
            </Popover>

            {dueDate && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setDueDate(undefined)}
              >
                Clear date
              </Button>
            )}

            <div className="flex gap-2 items-center">
              <Input
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddTag())}
                placeholder="Add tag"
                className="h-9 w-32"
              />
              <Button type="button" size="sm" onClick={handleAddTag}>
                Add Tag
              </Button>
            </div>
          </div>

          {tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {tags.map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center gap-1 px-2 py-1 bg-accent text-accent-foreground rounded-full text-xs"
                >
                  {tag}
                  <button
                    onClick={() => handleRemoveTag(tag)}
                    className="hover:text-destructive"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </span>
              ))}
            </div>
          )}
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
                  onUpdate={handleUpdateTodo}
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
