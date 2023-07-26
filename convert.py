import csv
from datetime import datetime

# Replace these with the actual file paths
input_file_path = 'schedule.csv'
output_file_path = 'schedule_new.csv'

def convert_date_format(date_str):
    # Parse the date from "DD/MM/YYYY HH:MM" to a datetime object
    date_obj = datetime.strptime(date_str, "%d/%m/%Y %H:%M")
    # Convert the datetime object to the desired format "%Y-%m-%d %H:%M:%S"
    formatted_date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_date_str

# Read the CSV file, convert the dates, and write to the output CSV file
with open(input_file_path, 'r', newline='') as infile, open(output_file_path, 'w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # Read and write the header row directly to the output file
    header_row = next(reader, None)
    if header_row:
        writer.writerow(header_row)


    # Assuming the date is in the first column (index 0)
    for row in reader:
        if row:  # Check if the row is not empty
            date_str = row[2]
            formatted_date_str = convert_date_format(date_str)
            # Replace the date in the row with the formatted date
            row[2] = formatted_date_str
            writer.writerow(row)

