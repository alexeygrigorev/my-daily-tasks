import { useState } from "react";
import { motion } from "framer-motion";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Trash2, Pencil, Calendar, Tag } from "lucide-react";
import { cn } from "@/lib/utils";
import { Todo } from "@/types/todo";
import { TodoEditDialog } from "./TodoEditDialog";
import { format, isPast, isToday } from "date-fns";

interface TodoItemProps {
  todo: Todo;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
  onUpdate: (id: string, updates: Partial<Omit<Todo, 'id'>>) => void;
}

export const TodoItem = ({ todo, onToggle, onDelete, onUpdate }: TodoItemProps) => {
  const [isEditOpen, setIsEditOpen] = useState(false);

  const getDueDateColor = () => {
    if (!todo.dueDate) return "";
    if (isPast(todo.dueDate) && !isToday(todo.dueDate)) return "text-destructive";
    if (isToday(todo.dueDate)) return "text-amber-500";
    return "text-muted-foreground";
  };

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, x: -100 }}
        transition={{ duration: 0.2 }}
        className="group flex items-start gap-3 p-4 bg-card rounded-lg border border-border shadow-sm hover:shadow-md transition-all"
      >
        <Checkbox
          id={todo.id}
          checked={todo.completed}
          onCheckedChange={() => onToggle(todo.id)}
          className="h-5 w-5 mt-0.5"
        />
        <div className="flex-1 min-w-0">
          <label
            htmlFor={todo.id}
            className={cn(
              "text-base cursor-pointer transition-all block",
              todo.completed && "line-through text-muted-foreground"
            )}
          >
            {todo.text}
          </label>
          
          <div className="flex flex-wrap gap-2 mt-2">
            {todo.dueDate && (
              <span className={cn("inline-flex items-center gap-1 text-xs", getDueDateColor())}>
                <Calendar className="h-3 w-3" />
                {format(todo.dueDate, "MMM d, yyyy")}
              </span>
            )}
            {todo.tags.length > 0 && (
              <div className="inline-flex items-center gap-1 flex-wrap">
                <Tag className="h-3 w-3 text-muted-foreground" />
                {todo.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-0.5 bg-accent text-accent-foreground rounded-full text-xs"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
        
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsEditOpen(true)}
            className="hover:bg-primary/10 hover:text-primary"
          >
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => onDelete(todo.id)}
            className="text-destructive hover:text-destructive hover:bg-destructive/10"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </motion.div>

      <TodoEditDialog
        todo={todo}
        open={isEditOpen}
        onOpenChange={setIsEditOpen}
        onSave={(updates) => onUpdate(todo.id, updates)}
      />
    </>
  );
};
