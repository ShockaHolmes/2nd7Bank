import csv
import random

# First names and last names for realistic employee generation
first_names = [
    "John", "Jane", "Bob", "Alice", "Michael", "Sarah", "David", "Emily", "James", "Jessica",
    "Robert", "Mary", "William", "Patricia", "Richard", "Jennifer", "Joseph", "Linda", "Thomas", "Barbara",
    "Charles", "Susan", "Christopher", "Carol", "Daniel", "Margaret", "Matthew", "Dorothy", "Anthony", "Lisa",
    "Mark", "Nancy", "Donald", "Karen", "Steven", "Donna", "Paul", "Cynthia", "Andrew", "Sandra",
    "Joshua", "Kathleen", "Kenneth", "Christine", "Kevin", "Deborah", "Brian", "Rachael", "George", "Catherine",
    "Edward", "Carolyn", "Ronald", "Janet", "Timothy", "Maria", "Jason", "Heather", "Jeffrey", "Diane",
    "Ryan", "Virginia", "Jacob", "Julie", "Gary", "Olivia", "Nicholas", "Joyce", "Eric", "Victoria"
]

last_names = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Ruiz", "Alexander", "Nelson", "Carter", "Salazar", "Murphy", "Ortiz", "Gibbons", "Kennedy", "Bennett",
    "Costa", "Henderson", "Matthews", "Cromwell", "Hendrix", "Pritchard", "Hunter", "Collier", "Graham", "Blanchard"
]

# Generate CSV file
csv_filename = "employees.csv"

print("Generating 500,000 employee records...")

with open(csv_filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    
    # Write header
    writer.writerow(["Name", "Hours-worked", "Hourly-rate"])
    
    # Generate 500,000 employee records
    for i in range(500000):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        name = f"{first_name} {last_name}"
        
        hours_worked = round(random.uniform(20, 50), 2)
        hourly_rate = round(random.uniform(10.0, 35.0), 2)
        
        writer.writerow([name, hours_worked, hourly_rate])
        
        # Print progress every 50,000 records
        if (i + 1) % 50000 == 0:
            print(f"Generated {i + 1:,} records...")

print(f"✓ CSV file '{csv_filename}' created successfully with 500,000 employees!")
