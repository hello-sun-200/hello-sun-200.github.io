import sys
import csv
from tabulate import tabulate

if len(sys.argv)!=2:
    sys.exit(1)
else:
    if sys.argv[1].strip().endswith('.csv'):
        try:
            with open(sys.argv[1],"r") as file:
                reader=csv.reader(file)
                data=list(reader)
                print(tabulate(data, headers='firstrow', tablefmt='grid'))
        except FileNotFoundError:
            sys.exit(1)
    else:
        sys.exit(1)
