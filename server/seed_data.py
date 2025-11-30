"""
Script to insert 100 fake todo records with due dates anchored to today.
"""
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import DBTodo

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Sample task templates for different tags
TASK_TEMPLATES = {
    "personal": [
        "Call {} about plans",
        "Buy birthday gift for {}",
        "Schedule dentist appointment",
        "Organize photos from {}",
        "Update personal blog",
        "Read {} book chapter",
        "Plan weekend trip to {}",
        "Clean out {}",
        "Reply to {}'s email",
        "Renew {} subscription",
        "Fix broken {} at home",
        "Sort through old {}",
        "Make appointment with {}",
        "Update resume",
        "Practice {} hobby",
    ],
    "groceries": [
        "Buy {} for dinner",
        "Get fresh {}",
        "Stock up on {}",
        "Buy {} from farmer's market",
        "Get {} for recipe",
        "Purchase {} in bulk",
        "Buy organic {}",
        "Get {} and {}",
        "Restock {}",
        "Buy {} for the week",
        "Get {} on sale",
        "Purchase {} for pantry",
        "Buy {} for breakfast",
        "Get {} and snacks",
        "Buy {} before they run out",
    ],
    "course": [
        "Complete {} module",
        "Watch lecture on {}",
        "Submit {} assignment",
        "Study {} chapter",
        "Review {} notes",
        "Practice {} exercises",
        "Attend {} session",
        "Prepare for {} exam",
        "Read {} materials",
        "Complete {} quiz",
        "Work on {} project",
        "Research {} topic",
        "Write {} essay",
        "Study for {} test",
        "Complete {} homework",
    ],
    "work": [
        "Review {} document",
        "Send email to {} team",
        "Update {} spreadsheet",
        "Attend {} meeting",
        "Complete {} report",
        "Follow up on {} project",
        "Prepare {} presentation",
        "Review {} code",
        "Update {} documentation",
        "Schedule {} call",
        "Fix {} bug",
        "Test {} feature",
        "Deploy {} to production",
        "Review {} proposal",
        "Plan {} sprint",
    ],
}

# Filler words for templates
FILLERS = {
    "personal": ["mom", "friend", "summer vacation", "favorite", "the garage", "closet", 
                 "doctor", "gym", "Netflix", "the basement", "guitar", "clothes"],
    "groceries": ["milk", "bread", "eggs", "vegetables", "chicken", "pasta", "rice", 
                  "fruits", "cheese", "yogurt", "coffee", "tomatoes", "lettuce", 
                  "potatoes", "bananas"],
    "course": ["Python", "algorithms", "database", "machine learning", "calculus", 
               "statistics", "web development", "data structures", "networking", 
               "security", "final", "midterm", "JavaScript", "SQL", "React"],
    "work": ["quarterly", "client", "budget", "API", "dashboard", "weekly", "status", 
             "pull request", "deployment", "architecture", "stakeholder", "Q4", 
             "customer feedback", "design", "next"],
}


def generate_task_text(tag: str) -> str:
    """Generate a realistic task text for the given tag."""
    template = random.choice(TASK_TEMPLATES[tag])
    if "{}" in template:
        # Replace placeholders with appropriate fillers
        num_placeholders = template.count("{}")
        fillers = random.sample(FILLERS[tag], min(num_placeholders, len(FILLERS[tag])))
        return template.format(*fillers)
    return template


def generate_due_date(today: datetime) -> datetime:
    """Generate a due date relative to today (between -30 and +30 days)."""
    # 30% past due, 40% today/this week, 30% future
    rand = random.random()
    if rand < 0.3:
        # Past due: -30 to -1 days
        days_offset = random.randint(-30, -1)
    elif rand < 0.7:
        # Current/upcoming: 0 to 7 days
        days_offset = random.randint(0, 7)
    else:
        # Future: 8 to 30 days
        days_offset = random.randint(8, 30)
    
    # Add some random hours to make it more realistic
    hours_offset = random.randint(0, 23)
    due_date = today + timedelta(days=days_offset, hours=hours_offset)
    return due_date


def seed_database(num_records: int = 100):
    """Insert fake todo records into the database."""
    db: Session = SessionLocal()
    
    try:
        # Get today's date
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Available tags
        available_tags = ["personal", "groceries", "course", "work"]
        
        print(f"Inserting {num_records} fake todo records...")
        
        for i in range(num_records):
            # Randomly select 1-2 tags for each todo
            num_tags = random.choices([1, 2], weights=[0.7, 0.3])[0]
            selected_tags = random.sample(available_tags, num_tags)
            
            # Generate task text based on primary tag
            primary_tag = selected_tags[0]
            task_text = generate_task_text(primary_tag)
            
            # Generate due date anchored to today
            due_date = generate_due_date(today)
            
            # Randomly set some todos as completed (20% chance)
            completed = random.random() < 0.2
            
            # Create timestamp-like ID
            todo_id = f"{int(today.timestamp() * 1000) + i}"
            
            # Create the todo
            new_todo = DBTodo(
                id=todo_id,
                text=task_text,
                completed=completed,
                dueDate=due_date,
                tags=selected_tags,
                createdAt=datetime.now(),
            )
            
            db.add(new_todo)
            
            if (i + 1) % 10 == 0:
                print(f"  Inserted {i + 1}/{num_records} records...")
        
        # Commit all records
        db.commit()
        print(f"✓ Successfully inserted {num_records} fake todo records!")
        
        # Print some statistics
        print("\nStatistics:")
        print(f"  - Records with 'personal' tag: {db.query(DBTodo).filter(DBTodo.tags.contains(['personal'])).count()}")
        print(f"  - Records with 'groceries' tag: {db.query(DBTodo).filter(DBTodo.tags.contains(['groceries'])).count()}")
        print(f"  - Records with 'course' tag: {db.query(DBTodo).filter(DBTodo.tags.contains(['course'])).count()}")
        print(f"  - Records with 'work' tag: {db.query(DBTodo).filter(DBTodo.tags.contains(['work'])).count()}")
        print(f"  - Completed todos: {db.query(DBTodo).filter(DBTodo.completed).count()}")
        print(f"  - Past due todos: {db.query(DBTodo).filter(DBTodo.dueDate < today).count()}")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error inserting records: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database(100)
