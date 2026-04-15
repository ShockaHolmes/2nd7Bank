import csv
import argparse
import os

def read_data(file_name):
    with open(file_name, 'r') as file:
        csv_reader = csv.reader(file)
        data = [row for row in csv_reader]
    return data

#input_data = read_data('input.data')
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
                for hk in ('hours_worked', 'hours worked', 'hours', 'hours-worked'):
                    if hk in row_norm and row_norm[hk] != '':
                        hours = float(row_norm[hk])
                        break
                for rk in ('hourly_rate', 'hourly rate', 'rate', 'hourlyrate', 'hourly-rate'):
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

    The user is prompted for Name, Hours-worked, and Hourly-rate.
    Gross pay is calculated as: Hours-worked * Hourly-rate
    Taxes are calculated as: Gross pay * tax_rate
    Net pay is calculated as: Gross pay - Taxes
    """
    payroll = []
    while True:
        name = input("Name (leave blank to finish): ").strip()
        if not name:
            break

        try:
            hours_worked = float(input("Hours-worked: ").strip())
            hourly_rate = float(input("Hourly-rate: ").strip())
        except ValueError:
            print("Invalid number entered — please try this row again.")
            continue

        # compute gross pay, taxes, and net pay
        gross = hours_worked * hourly_rate
        taxes = gross * tax_rate
        net = gross - taxes

        # sanity checks
        if hours_worked < 0 or hourly_rate < 0:
            print("Hours-worked and Hourly-rate must be non-negative — try again.")
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
        def compute_from_inputs(gross, taxes, net, tax_rate, orig_gross=None, orig_taxes=None):
            # compute missing values using rules from interactive_input
            # If gross changed and taxes left blank, prefer proportional update
            if gross is not None and taxes is not None and net is None:
                net = gross - taxes
            elif gross is not None and net is not None and taxes is None:
                taxes = gross - net
            elif taxes is not None and net is not None and gross is None:
                gross = taxes + net
            elif gross is not None and taxes is None and net is None:
                # If original taxes/gross available, preserve the same ratio
                if orig_gross and orig_gross > 0 and orig_taxes is not None:
                    rate = orig_taxes / orig_gross
                    taxes = gross * rate
                else:
                    taxes = gross * tax_rate
                net = gross - taxes
            elif taxes is not None and gross is None and net is None:
                if tax_rate <= 0:
                    return None, None, None
                gross = taxes / tax_rate
                net = gross - taxes
            return gross, taxes, net

        def edit_saved_file(fname, tax_rate):
            if not os.path.exists(fname):
                print(f'File not found: {fname}')
                return
            payroll = process_input_file(fname, tax_rate=tax_rate)
            if not payroll:
                print(f'No valid rows parsed from {fname}')
                return
            while True:
                print('\nLoaded payroll:')
                for i, (name, gross, taxes, net) in enumerate(payroll, start=1):
                    print(f"{i}) {name:<20} {gross:>10.2f} {taxes:>10.2f} {net:>10.2f}")
                sel = input('Enter row number to edit (or blank to return to menu): ').strip()
                if sel == '':
                    break
                try:
                    idx = int(sel) - 1
                    if idx < 0 or idx >= len(payroll):
                        print('Invalid row number')
                        continue
                except ValueError:
                    print('Please enter a number')
                    continue

                name, gross, taxes, net = payroll[idx]
                print(f'Editing row {sel}: {name}, Gross={gross}, Taxes={taxes}, Net={net}')
                new_name = input(f'Name [{name}]: ').strip() or name
                def read_val(prompt, old):
                    s = input(f"{prompt} [{old}]: ").strip()
                    return None if s == '' else s

                h_s = read_val('Hours-worked', f'{gross / 20:.2f}')
                r_s = read_val('Hourly-rate', '20.00')
                try:
                    h_v = float(h_s) if h_s is not None else None
                    r_v = float(r_s) if r_s is not None else None
                except ValueError:
                    print('Invalid number entered; edit cancelled for this row.')
                    continue

                if h_v is None or r_v is None:
                    print('Hours-worked and Hourly-rate are required.')
                    continue

                if h_v < 0 or r_v < 0:
                    print('Hours-worked and Hourly-rate must be non-negative.')
                    continue

                new_gross = h_v * r_v
                new_taxes = new_gross * tax_rate
                new_net = new_gross - new_taxes
                payroll[idx] = (new_name, new_gross, new_taxes, new_net)
                print('Row updated.')

                save = input('Save changes to file now? (y/N): ').strip().lower()
                if save == 'y':
                    write_output(fname, payroll)
                    print(f'Wrote {len(payroll)} rows to {fname}')

        def run_menu(tax_rate=0.2):
            while True:
                print('\nPayroll Menu:')
                print('1) Enter payroll (interactive)')
                print('2) Read payroll from file')
                print('3) Update payroll file')
                print('4) Quit')
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
                elif choice == '3':
                    fname = input('Enter filename to update (default input.data): ').strip()
                    if not fname:
                        fname = 'input.data'
                    edit_saved_file(fname, tax_rate=args.tax_rate)
                elif choice in ('4', 'q', 'quit', 'exit'):
                    print('Exiting.')
                    break
                else:
                    print('Invalid option — choose 1, 2, 3, or 4.')

        run_menu(tax_rate=args.tax_rate)

