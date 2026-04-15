import argparse


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


def main():
    parser = argparse.ArgumentParser(description='Process a transactions file')
    parser.add_argument('input_file', nargs='?', default='input.data',
                        help='Path to the input data file (default: input.data)')
    args = parser.parse_args()

    records = read_data(args.input_file)
    balance = calculate_balance(records)
    print(f"Final Balance: ${balance:.2f}")

if __name__ == '__main__':
    main()