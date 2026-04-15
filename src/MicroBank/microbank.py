import argparse
from datetime import datetime


# read the input data from the file and parse each line
def read_data(file_name):
    records = []
    with open(file_name, 'r') as file:
        for raw in file:
            line = raw.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 3:
                continue
            date = parts[0]
            typ = parts[1].lower()
            amount_str = parts[2]
            try:
                amount = float(amount_str)
            except ValueError:
                continue
            records.append((date, typ, amount))
    return records

# process the parsed records to calculate the balance
def calculate_balance(records: list):
    balance = 0.0
    for rec in records:
        date, typ, amount = rec
        if typ == 'deposit':
            balance += amount
        elif typ == 'withdrawal':
            balance -= amount
    return balance


def save_transaction(file_name, date, typ, amount):
    """Append a transaction to the data file"""
    with open(file_name, 'a') as file:
        file.write(f"{date}, {typ}, {amount:.2f}\n")


def show_ledger(file_name):
    """Display all transactions from the ledger"""
    records = read_data(file_name)
    if not records:
        print("No transactions found.")
        return
    
    print("\n" + "="*60)
    print(f"{'Date':<12} {'Type':<12} {'Amount':<12} {'Balance':<12}")
    print("="*60)
    balance = 0.0
    for date, typ, amount in records:
        if typ == 'deposit':
            balance += amount
        elif typ == 'withdrawal':
            balance -= amount
        print(f"{date:<12} {typ:<12} ${amount:>10.2f} ${balance:>10.2f}")
    print("="*60)

# Allow user to interactively perform transactions
def interactive_mode(balance, file_name): 
    """Allow user to interactively perform transactions"""
    while True:
        print(f"\nCurrent Balance: ${balance:.2f}")
        print("\n--- Menu ---")
        print("1. Deposit")
        print("2. Withdrawal")
        print("3. Show Ledger")
        print("4. Quit")
        
        choice = input("\nSelect an option (1-4): ").strip()
        
        if choice == '4':
            print(f"Final Balance: ${balance:.2f}")
            break
        elif choice == '3':
            show_ledger(file_name)
        elif choice == '1':
            try:
                date_input = input("Enter date (MM/DD/YYYY) or press Enter for today: ").strip()
                if not date_input:
                    date_input = datetime.now().strftime("%m/%d/%Y")
                amount = float(input("Enter deposit amount: $"))
                if amount > 0:
                    balance += amount
                    save_transaction(file_name, date_input, "deposit", amount)
                    print(f"Deposited ${amount:.2f} on {date_input}. New balance: ${balance:.2f}")
                else:
                    print("Amount must be positive!")
            except ValueError:
                print("Invalid amount or date entered!")
        elif choice == '2':
            try:
                date_input = input("Enter date (MM/DD/YYYY) or press Enter for today: ").strip()
                if not date_input:
                    date_input = datetime.now().strftime("%m/%d/%Y")
                amount = float(input("Enter withdrawal amount: $"))
                if amount > 0 and amount <= balance:
                    balance -= amount
                    save_transaction(file_name, date_input, "withdrawal", amount)
                    print(f"Withdrew ${amount:.2f} on {date_input}. New balance: ${balance:.2f}")
                elif amount > balance:
                    print("Insufficient funds!")
                else:
                    print("Amount must be positive!")
            except ValueError:
                print("Invalid amount or date entered!")
        else:
            print("Invalid choice! Please select 1-4.")
    
    return balance

# Main function to run the program
def main():
    parser = argparse.ArgumentParser(description='Process a transactions file')
    parser.add_argument('input_file', nargs='?', default='input.data',
                        help='Path to the input data file (default: input.data)')
    args = parser.parse_args()

    records = read_data(args.input_file)
    balance = calculate_balance(records)
    print(f"Starting Balance: ${balance:.2f}")
    
    # Enter interactive mode
    interactive_mode(balance, args.input_file)

if __name__ == '__main__':
    main()