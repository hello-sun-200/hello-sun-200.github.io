import sys
import csv

if len(sys.argv) != 3:
    sys.exit(1)
if sys.argv[1].endswith('.csv') and sys.argv[2].endswith('.csv'):
    try:
        with open(sys.argv[1], 'r') as f1, open(sys.argv[2], 'w') as f2:
            reader = csv.DictReader(f1)
            fieldnames = ['first', 'last', 'house']
            writer = csv.DictWriter(f2, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                name = row['name'].split(',')
                writer.writerow(
                    {'first': name[1].strip(), 'last': name[0].strip(),
                     'house': row['house']}
                )
    except FileNotFoundError:
        sys.exit(1)
else:
    sys.exit(1)
