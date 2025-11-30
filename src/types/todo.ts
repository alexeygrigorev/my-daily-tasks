export interface Todo {
  id: string;
  text: string;
  completed: boolean;
  dueDate?: Date;
  tags: string[];
  createdAt: Date;
}
