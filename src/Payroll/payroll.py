import csv
import argparse
import os

def read_data(file_name):
    with open(file_name, 'r') as file:
        csv_reader = csv.reader(file)
        data = [row for row in csv_reader]
    return data
    # data is a list of lists, where each inner list represents a row from the CSV file

def calculate_payroll(data):
    payroll = []
    for row in data[1:]:  # Skip header
        name, hours_worked, hourly_rate = row
        hours_worked = float(hours_worked)
        hourly_rate = float(hourly_rate)
        total_pay = hours_worked * hourly_rate
        taxes = total_pay * 0.2  # Assuming a flat tax rate of 20%
        net_pay = total_pay - taxes
        payroll.append((name, total_pay, taxes, net_pay))
    return payroll


def process_input_file(file_name, tax_rate=0.2):
    """Read a CSV file and return payroll list of (name, total_pay, taxes, net_pay).

    Supported input formats (case-insensitive headers):
    - Name, Gross (or Total Pay): use Gross directly
    - Name, Hours Worked, Hourly Rate: compute total = hours * rate
    """
    payroll = []
    with open(file_name, 'r', newline='') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return payroll
        for row in reader:
            # normalize keys
            row_norm = {k.strip().lower(): (v or '').strip() for k, v in row.items()}
            name = row_norm.get('name', '')
            try:
                # look for gross/total pay
                gross_key = None
                for k in ('gross', 'total pay', 'total', 'gross pay', 'total_pay', 'gross_pay'):
                    if k in row_norm and row_norm[k] != '':
                        gross_key = k
                        break
                if gross_key:
                    gross = float(row_norm[gross_key])
                    taxes = gross * tax_rate
                    net = gross - taxes
                    payroll.append((name, gross, taxes, net))
                    continue

                # otherwise look for hours and rate
                hours = None
                rate = None
                for hk in ('hours_worked', 'hours worked', 'hours'):
                    if hk in row_norm and row_norm[hk] != '':
                        hours = float(row_norm[hk])
                        break
                for rk in ('hourly_rate', 'hourly rate', 'rate', 'hourlyrate'):
                    if rk in row_norm and row_norm[rk] != '':
                        rate = float(row_norm[rk])
                        break
                if hours is not None and rate is not None:
                    total = hours * rate
                    taxes = total * tax_rate
                    net = total - taxes
                    payroll.append((name, total, taxes, net))
                    continue

                # fallback: try to parse first two numeric values in row
                nums = []
                for v in row.values():
                    try:
                        nums.append(float((v or '').strip()))
                    except Exception:
                        continue
                if len(nums) >= 1:
                    gross = nums[0]
                    taxes = gross * tax_rate
                    net = gross - taxes
                    payroll.append((name, gross, taxes, net))
            except Exception as e:
                print(f"Skipping row due to parse error: {row} -> {e}")
    return payroll

def print_payroll(payroll):
    print(f"{'Name':<20} {'Total Pay':<15} {'Taxes':<10} {'Net Pay':<10}")
    for name, total_pay, taxes, net_pay in payroll:
        print(f"{name:<20} {total_pay:<15.2f} {taxes:<10.2f} {net_pay:<10.2f}")

def write_output(file_name, payroll):
    with open(file_name, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['Name', 'Total Pay', 'Taxes', 'Net Pay'])
        for name, total_pay, taxes, net_pay in payroll:
            csv_writer.writerow([name, f"{total_pay:.2f}", f"{taxes:.2f}", f"{net_pay:.2f}"])


def interactive_input(tax_rate=0.2):
    """Prompt the user to enter payroll rows interactively.

    The user may enter any combination of Gross, Taxes, Net-pay. Missing
    numeric fields are computed where possible using `tax_rate`.

    Computation rules:
    - If only Gross provided -> Taxes = Gross * tax_rate, Net = Gross - Taxes
    - If Gross + Taxes provided -> Net = Gross - Taxes
    - If Gross + Net provided -> Taxes = Gross - Net
    - If Taxes + Net provided -> Gross = Taxes + Net
    - If only Taxes provided -> Gross = Taxes / tax_rate (if tax_rate > 0)
    """
    payroll = []
    while True:
        name = input("Name (leave blank to finish): ").strip()
        if not name:
            break

        def read_optional(prompt):
            s = input(prompt).strip()
            return None if s == '' else s

        gross_s = read_optional("Gross pay (blank to skip): ")
        taxes_s = read_optional("Taxes (blank to skip): ")
        net_s = read_optional("Net pay (blank to skip): ")

        # parse numbers
        try:
            gross = float(gross_s) if gross_s is not None else None
            taxes = float(taxes_s) if taxes_s is not None else None
            net = float(net_s) if net_s is not None else None
        except ValueError:
            print("Invalid number entered — please try this row again.")
            continue

        # compute missing values
        if gross is not None and taxes is not None and net is None:
            net = gross - taxes
        elif gross is not None and net is not None and taxes is None:
            taxes = gross - net
        elif taxes is not None and net is not None and gross is None:
            gross = taxes + net
        elif gross is not None and taxes is None and net is None:
            taxes = gross * tax_rate
            net = gross - taxes
        elif taxes is not None and gross is None and net is None:
            if tax_rate <= 0:
                print("Cannot compute gross from taxes with non-positive tax rate.")
                continue
            gross = taxes / tax_rate
            net = gross - taxes

        # if still missing necessary fields, skip
        if gross is None or taxes is None or net is None:
            print("Insufficient numeric data to compute row — please provide at least two values or gross alone.")
            continue

        # sanity checks
        if gross < 0 or taxes < 0 or net < 0:
            print("Numeric values must be non-negative — try again.")
            continue

        payroll.append((name, gross, taxes, net))
    return payroll

# run the payroll processing
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Payroll processor')
    parser.add_argument('-i', '--input', help='Input CSV file to import')
    parser.add_argument('-o', '--output', help='Output CSV file to write results')
    parser.add_argument('-t', '--tax-rate', type=float, default=0.2, help='Tax rate as decimal (default 0.2)')
    parser.add_argument('--interactive', action='store_true', help='Force interactive input mode')
    args = parser.parse_args()

    payroll = []
    if args.input:
        if os.path.exists(args.input):
            payroll = process_input_file(args.input, tax_rate=args.tax_rate)
            if not payroll:
                print(f'No valid rows parsed from {args.input}')
            else:
                print_payroll(payroll)
                if args.output:
                    write_output(args.output, payroll)
        else:
            print(f'Input file not found: {args.input}')
    elif args.interactive:
        payroll = interactive_input(tax_rate=args.tax_rate)
        if payroll:
            print_payroll(payroll)
            if args.output:
                write_output(args.output, payroll)
            else:
                save = input('Save interactive entries to CSV? (y/N): ').strip().lower()
                if save == 'y':
                    fname = input('Enter output filename (e.g. output.data): ').strip()
                    if fname:
                        write_output(fname, payroll)
                        print(f'Wrote {len(payroll)} rows to {fname}')
    else:
        # default behavior: show a small menu to enter payroll or read saved payroll
        def run_menu(tax_rate=0.2):
            while True:
                print('\nPayroll Menu:')
                print('1) Enter payroll (interactive)')
                print('2) Read payroll from file')
                print('3) Quit')
                choice = input('Select an option: ').strip()
                if choice == '1':
                    payroll = interactive_input(tax_rate=tax_rate)
                    if payroll:
                        print_payroll(payroll)
                        save = input('Save interactive entries to CSV? (y/N): ').strip().lower()
                        if save == 'y':
                            fname = input('Enter output filename (e.g. output.data): ').strip()
                            if fname:
                                write_output(fname, payroll)
                                print(f'Wrote {len(payroll)} rows to {fname}')
                elif choice == '2':
                    fname = input('Enter filename to read (default input.data): ').strip()
                    if not fname:
                        fname = 'input.data'
                    if os.path.exists(fname):
                        payroll = process_input_file(fname, tax_rate=args.tax_rate)
                        if payroll:
                            print_payroll(payroll)
                        else:
                            print(f'No valid rows parsed from {fname}')
                    else:
                        print(f'File not found: {fname}')
                elif choice in ('3', 'q', 'quit', 'exit'):
                    print('Exiting.')
                    break
                else:
                    print('Invalid option — choose 1, 2, or 3.')

        run_menu(tax_rate=args.tax_rate)

