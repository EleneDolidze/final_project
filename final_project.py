import csv
import os
from statistics import stdev   #დავაიმპორტე სტანდარტული გადახრის(standard deviation)ფორმულა volatility index-ის გამოსათვლელად

class CryptoDataLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        data = []
        try:
            with open(self.file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if any(value.strip() == '' for value in row.values()):
                        print(f"Missing values found in row: {row}")
                        continue  #დაskipავს missing value-ების row-ებს
                    data.append(row)
        except (FileNotFoundError, PermissionError) as e: 
            print(f"Error accessing file: {e}")    #ამუშავეს შეცდომას(თუ არაა დამატებული csv file)
        return data

class CryptoDataAnalyzer:
    def calculate_weekly_data(data):   #ფუნქციის იდეაა სრული weekly data პოვნა average/highest/lowest prices/volatility index-ებით 
        weekly_data = []
        current_week = []
        highest_volatility = {'value': None, 'date': None}
        lowest_volatility = {'value': None, 'date': None}

        for row in data:
            current_week.append(row)
            if len(current_week) == 7:
                weekly_prices = [float(row['Close'].replace(',', '')) for row in current_week] 
                weekly_average = CryptoDataAnalyzer.calculate_average_price(current_week)
                highest_price_result = CryptoDataAnalyzer.find_extreme_price(current_week, is_highest=True)
                weekly_highest = highest_price_result['Close'] if highest_price_result else None
                lowest_price_result = CryptoDataAnalyzer.find_extreme_price(current_week, is_highest=False)
                weekly_lowest = lowest_price_result['Close'] if lowest_price_result else None
                weekly_volatility = CryptoDataAnalyzer.calculate_volatility(current_week)
                week_start_date = current_week[0]['Date']

                if highest_volatility['value'] is None or weekly_volatility > highest_volatility['value']:
                    highest_volatility['value'] = weekly_volatility
                    highest_volatility['date'] = week_start_date

                if lowest_volatility['value'] is None or weekly_volatility < lowest_volatility['value']:
                    lowest_volatility['value'] = weekly_volatility
                    lowest_volatility['date'] = week_start_date

                
                weekly_data.append({
                    'Week Start': week_start_date,
                    'Average Price': weekly_average,
                    'Highest Price': weekly_highest,
                    'Lowest Price': weekly_lowest,
                    'Volatility': weekly_volatility
                })
                
                current_week = []

        if current_week:
            weekly_prices = [float(row['Close'].replace(',', '')) for row in current_week]
            weekly_average = CryptoDataAnalyzer.calculate_average_price(current_week)
            highest_price_result = CryptoDataAnalyzer.find_extreme_price(current_week, is_highest=True)
            weekly_highest = highest_price_result['Close'] if highest_price_result else None
            lowest_price_result = CryptoDataAnalyzer.find_extreme_price(current_week, is_highest=False)
            weekly_lowest = lowest_price_result['Close'] if lowest_price_result else None
            weekly_volatility = CryptoDataAnalyzer.calculate_volatility(current_week)
            
            if highest_volatility['value'] is None or weekly_volatility > highest_volatility['value']:
                highest_volatility['value'] = weekly_volatility
                highest_volatility['date'] = week_start_date

            if lowest_volatility['value'] is None or weekly_volatility < lowest_volatility['value']:
                lowest_volatility['value'] = weekly_volatility
                lowest_volatility['date'] = week_start_date

            
            week_start_date = current_week[0]['Date']
            weekly_data.append({
                'Week Start': week_start_date,
                'Average Price': weekly_average,
                'Highest Price': weekly_highest,
                'Lowest Price': weekly_lowest,
                'Volatility': weekly_volatility
            })


        return weekly_data, highest_volatility, lowest_volatility
    

    def calculate_monthly_data(data):   #ფუნქციის იდეაა სრული monthly data პოვნა average/highest/lowest prices/volatility index-ებით 
         monthly_data = {}
         highest_volatility = {'value': None, 'date': None}
         lowest_volatility = {'value': None, 'date': None}

         for row in data:
             try:
                 date_parts = row['Date'].split('-')
                 year = int(date_parts[0])
                 month = int(date_parts[1])
                 month_key = (year, month)
                 if month_key not in monthly_data:
                     monthly_data[month_key] = {
                         'Month': f"{year}-{month:02d}",
                         'Prices': [],
                         'Total Price': 0,
                         'Count': 0,
                         'Volatility': None  #თუ არის საკმარისი მონაცემი historical data-ში, დათვლის volatility index, თუ არა დაწერს 'None'-ს
                     }
                 monthly_data[month_key]['Prices'].append(row)
                 close_price = float(row['Close'].replace(',', ''))
                 monthly_data[month_key]['Total Price'] += close_price
                 monthly_data[month_key]['Count'] += 1
             except ValueError:
                 print("Invalid price format in data.")
                 continue
                 
    
         for month_key, month_data in monthly_data.items():
             if month_data['Count'] == 0:
                 continue
             month_data['Average Price'] = month_data['Total Price'] / month_data['Count']
             highest_price_row = CryptoDataAnalyzer.find_extreme_price(month_data['Prices'], is_highest=True)
             month_data['Highest Price'] = float(highest_price_row['Close'].replace(',', '')) if highest_price_row else None  # Ensure 'Highest Price' is always included
             lowest_price_row = CryptoDataAnalyzer.find_extreme_price(month_data['Prices'], is_highest=False)
             month_data['Lowest Price'] = float(lowest_price_row['Close'].replace(',', '')) if lowest_price_row else None
             month_prices = [float(row['Close'].replace(',', '')) for row in month_data['Prices']]
             if len(month_prices) > 1:
                 month_data['Volatility'] = stdev(month_prices)

                 if highest_volatility['value'] is None or month_data['Volatility'] > highest_volatility['value']:
                     highest_volatility['value'] = month_data['Volatility']
                     highest_volatility['date'] = month_data['Month']
                 if lowest_volatility['value'] is None or month_data['Volatility'] < lowest_volatility['value']:
                     lowest_volatility['value'] = month_data['Volatility']
                     lowest_volatility['date'] = month_data['Month']
         return list(monthly_data.values()), highest_volatility, lowest_volatility
            

    def calculate_yearly_data(data): #ფუნქციის იდეაა სრული yearly data პოვნა average/highest/lowest prices/volatility index-ებით 
        yearly_data = {}
        for row in data:
            try:
                date_parts = row['Date'].split('-')
                year = int(date_parts[0])
                if year not in yearly_data:
                    yearly_data[year] = {
                        'Year': year,
                        'Prices': [],
                        'Total Price': 0,
                        'Count': 0
                    }
                yearly_data[year]['Prices'].append(row)
                close_price = float(row['Close'].replace(',', ''))
                yearly_data[year]['Total Price'] += close_price
                yearly_data[year]['Count'] += 1
            except ValueError:
                print("Invalid price format in data.")
                continue

        for year, year_data in yearly_data.items():
            if year_data['Count'] == 0:
                continue
            year_data['Average Price'] = year_data['Total Price'] / year_data['Count']
            highest_price_row = CryptoDataAnalyzer.find_extreme_price(year_data['Prices'], is_highest=True)
            year_data['Highest Price'] = float(highest_price_row['Close'].replace(',', '')) if highest_price_row else None
            lowest_price_row = CryptoDataAnalyzer.find_extreme_price(year_data['Prices'], is_highest=False)
            year_data['Lowest Price'] = float(lowest_price_row['Close'].replace(',', '')) if lowest_price_row else None
            year_prices = [float(row['Close'].replace(',', '')) for row in year_data['Prices']]
            year_data['Volatility'] = stdev(year_prices)

        return list(yearly_data.values())

    
    def calculate_average_price(data):  #თვლის average price-ებს
        total_price = 0
        total_records = 0
        for row in data:
            try:
                close_price = float(row['Close'].replace(',', ''))
                total_price += close_price
                total_records += 1
            except ValueError:
                print("Invalid price format in data.")
                return None
        if total_records == 0:
            return None
        return total_price / total_records

    
    def find_extreme_price(data, is_highest=True):  #პოულობს extreme(lowest/highest) price-ებს
        extreme_price_row = None
        extreme_price = None
        for row in data:
            close_price = float(row['Close'].replace(',', ''))
            if extreme_price is None or (is_highest and close_price > extreme_price) or (not is_highest and close_price < extreme_price):
                extreme_price = close_price
                extreme_price_row = row
        return extreme_price_row

    
    def calculate_volatility(data): #პოულობს volatility index-არასტაბილურობის ინდექსს
        prices = [float(row['Close'].replace(',', '')) for row in data]
        return stdev(prices) if len(prices) > 1 else None  #stdev ფუნქცია რომელიც დავაიმპორტე კოდის წერის დასაწყისშივე არის იგივე სტანდარტული გადახრა
    


class CryptoReportGenerator:
    
    def save_to_csv(self, crypto_name, report_data, report_type):  #კოდის მნიშვნელოვანი ფუქნცია-ამოღებული ინფორმაციის სხვა csv file-ებში შენახვა
        file_name = f"{crypto_name}_{report_type}.csv"
        with open(file_name, 'w', newline='') as file:
            if report_type == 'average':
                fieldnames = ['Date', 'Average Price']
            elif report_type == 'highest':
                fieldnames = ['Date', 'Highest Price']
            elif report_type == 'lowest':
                fieldnames = ['Date', 'Lowest Price']
            elif report_type == 'volatility':
                fieldnames = ['Date', 'Volatility']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for entry in report_data:
                date = entry.get('Week Start', entry.get('Month', None))
                if report_type == 'average':
                   writer.writerow({'Date': date, 'Average Price': entry.get('Average Price', None)})
                elif report_type == 'highest':
                   writer.writerow({'Date': date, 'Highest Price': entry.get('Highest Price', None)})
                elif report_type == 'lowest':
                    writer.writerow({'Date': date, 'Lowest Price': entry.get('Lowest Price', None)})
                elif report_type == 'volatility':
                    writer.writerow({'Date': date, 'Volatility': entry.get('Volatility', None)})

    
    def save_volatility_indices_to_csv(self,crypto_name, highest_volatility, lowest_volatility, highest_date, lowest_date,  period): #ინახავს სხვა csv ფაილში lowest/highest volatility index-ებს თარიღის მითითებით
        file_name = f"{crypto_name}_{period}_volatility_indices.csv"
        with open(file_name, 'w', newline='') as file:
            fieldnames = ['Volatility Type', 'Value', 'Date']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'Volatility Type': 'Highest Volatility', 'Value': highest_volatility, 'Date': highest_date})
            writer.writerow({'Volatility Type': 'Lowest Volatility', 'Value': lowest_volatility, 'Date': lowest_date})
     
    def save_yearly_report_to_csv(self,crypto_name, yearly_report_data):
         file_name = f"{crypto_name}_yearly_report.csv"
         with open(file_name, 'w', newline='') as file:
             fieldnames = ['Year', 'Average Price', 'Highest Price', 'Lowest Price', 'Volatility']
             writer = csv.DictWriter(file, fieldnames=fieldnames)
             writer.writeheader()
             for entry in yearly_report_data:
                 writer.writerow({
                    'Year': entry['Year'],
                    'Average Price': entry['Average Price'],
                    'Highest Price': entry['Highest Price'],
                    'Lowest Price': entry['Lowest Price'],
                    'Volatility': entry['Volatility']
            })
         print("Yearly report data saved to CSV file.")

     
class CryptoAnalysisApp:
    def __init__(self):
        self.csv_files = [f for f in os.listdir() if f.endswith('.csv')]

    def display_menu(self):
        print("Welcome to Cryptocurrency Market Analysis!")
        print("Menu:")
        print("1. Weekly info")
        print("2. Monthly info")
        print("3. Yearly info")
        print("4. Exit")

    def select_csv_file(self):
        if not self.csv_files:
            print("No CSV files found in the directory.")
            return None, None
        csv_files = [file for file in self.csv_files if not any(x in file for x in ['highest', 'average', 'lowest', 'volatility', 'weakly', 'monthly', 'yearly', 'report'])] #რადგან პროგრამა ქმნის სხვა csvფაილებს სხვადასხვა infoს შესანახად,choice-ებიდან მათი ამოღება აუცილებელია error-ების თავიდან ასაცილებლად.
        print("Available CSV files:")
        for i, file_path in enumerate(csv_files, start=1):
            print(f"{i}. {file_path}")
        file_choice = input("Enter the number corresponding to the CSV file: ")
        if not file_choice.isdigit() or int(file_choice) < 1 or int(file_choice) > len(csv_files):
            print("Invalid file choice. Please enter a valid number.")
            return None, None
        selected_file = csv_files[int(file_choice) - 1]
        crypto_name = os.path.splitext(selected_file)[0]
        return selected_file, crypto_name
    
    def select_crypto_and_info(self, crypto_names):
         print("Available cryptocurrencies:")
         for i, name in enumerate(crypto_names, start=1):
              print(f"{i}. {name}")
         crypto_choice = input("Enter the number corresponding to the cryptocurrency: ")
         if not crypto_choice.isdigit() or int(crypto_choice) < 1 or int(crypto_choice) > len(crypto_names):
              print("Invalid cryptocurrency choice. Please enter a valid number.")
              return None, None
         selected_crypto = crypto_names[int(crypto_choice) - 1]

         print("What information do you want to see?")
         print("1. Average price")
         print("2. Highest price")
         print("3. Lowest price")
         print("4. Volatility")

         info_choice = input("Enter the number corresponding to the desired information: ")
         if not info_choice.isdigit() or int(info_choice) < 1 or int(info_choice) > 4:
             print("Invalid information choice. Please enter a valid number.")
             return None, None
         info_options = ["average", "highest", "lowest", "volatility"]
         return selected_crypto, info_options[int(info_choice) - 1]

    def main(self):
        while True:
            self.display_menu()
            choice = input("Enter your choice: ")

            if not choice.isdigit():
                 print("Incorrect input. Please enter a valid number.")
                 continue

            choice = int(choice)

            if choice in [1, 2, 3]:
                selected_file, crypto_name = self.select_csv_file()
                if selected_file is None:
                    continue

                data_loader = CryptoDataLoader(selected_file)
                data = data_loader.load_data()
                if data is None:
                    print("Error loading data. Please try again.")
                    continue

                if choice == 1: 
                    report_data, highest_volatility, lowest_volatility = CryptoDataAnalyzer.calculate_weekly_data(data)
                elif choice == 2:
                    report_data, highest_volatility, lowest_volatility = CryptoDataAnalyzer.calculate_monthly_data(data)
                elif choice == 3:
                    report_data = CryptoDataAnalyzer.calculate_yearly_data(data)
                    if not report_data:
                        print("No yearly data available.")
                        continue
                    else:
                        report_generator = CryptoReportGenerator()
                        report_generator.save_yearly_report_to_csv(crypto_name, report_data)
                        continue

                selected_crypto, info_choice = self.select_crypto_and_info([crypto_name])
                if not selected_crypto or not info_choice:
                    continue

                report_generator = CryptoReportGenerator()
                report_generator.save_to_csv(crypto_name, report_data, info_choice)
                print(f"Report saved to {crypto_name}_{info_choice}.csv")

                if info_choice == "volatility":
                    period = "weekly" if choice == 1 else "monthly"
                    report_generator.save_volatility_indices_to_csv(crypto_name, highest_volatility['value'], lowest_volatility['value'], highest_volatility['date'], lowest_volatility['date'], period) #ცალკე csv ფაილში ინახავს highest/lowest volatility index-ებს თარიღების მითითებით
                    print(f"Volatility indices saved to {crypto_name}_{period}_volatility_indices.csv")
                    

                if choice == 3:  
                    print(f"{selected_crypto} - Yearly Report")
                    for key, value in report_data.items():
                        print(f"{key}: {value}")
                else:
                    print(f"{selected_crypto} - {'Weekly' if choice == 1 else 'Monthly'} Report")
                    for entry in report_data:
                        date = entry['Week Start'] if 'Week Start' in entry else entry['Month']
                        if info_choice == "average":
                            print(f"{date}: Average Price = {entry['Average Price']}")
                        elif info_choice == "highest":
                            print(f"{date}: Highest Price = {entry['Highest Price']}")
                        elif info_choice == "lowest":
                            print(f"{date}: Lowest Price = {entry['Lowest Price']}")
                        elif info_choice == "volatility":
                            print(f"{date}: Volatility = {entry['Volatility']}")

            elif choice == 4:
                print("Exiting the application.")
                break
            else:
                print("Invalid choice. Please enter a valid number.")

if __name__ == "__main__":
    app = CryptoAnalysisApp()
    app.main()