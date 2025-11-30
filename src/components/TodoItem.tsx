import { motion } from "framer-motion";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";

export interface Todo {
  id: string;
  text: string;
  completed: boolean;
}

interface TodoItemProps {
  todo: Todo;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
}

export const TodoItem = ({ todo, onToggle, onDelete }: TodoItemProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -100 }}
      transition={{ duration: 0.2 }}
      className="group flex items-center gap-3 p-4 bg-card rounded-lg border border-border shadow-sm hover:shadow-md transition-all"
    >
      <Checkbox
        id={todo.id}
        checked={todo.completed}
        onCheckedChange={() => onToggle(todo.id)}
        className="h-5 w-5"
      />
      <label
        htmlFor={todo.id}
        className={cn(
          "flex-1 text-base cursor-pointer transition-all",
          todo.completed && "line-through text-muted-foreground"
        )}
      >
        {todo.text}
      </label>
      <Button
        variant="ghost"
        size="icon"
        onClick={() => onDelete(todo.id)}
        className="opacity-0 group-hover:opacity-100 transition-opacity text-destructive hover:text-destructive hover:bg-destructive/10"
      >
        <Trash2 className="h-4 w-4" />
      </Button>
    </motion.div>
  );
};
