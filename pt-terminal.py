import csv
import urllib.request
import os
import datetime

def main():

    print('Hollow Log\n')

    slot = 0;
    while not(slot >=1 and slot <= 3):
        slot = int(input('Slot 1\nSlot 2\nSlot 3\n\nWhich slot do you want to load? '))

    loadSlot(slot)

    # Main Menu
    while True:
        print('1. LookUp\n2. Buy\n3. Sell\n4. Add Cash\n5. Remove Cash\n6. History\n7. Exit\n8. Clear Slot')

        a = 0
        while not(a >= 1 and a <=8):
            a = int(input())

        # Each number coresponds to a menu choice
        if a == 1:
            symbol = input('Symbol: ').upper()
            print('{} - ${:.2f}\n'.format(symbol, lookup(symbol)['price']) )
            loadSlot(slot)
        elif a == 2:
            buyStock(slot)
        elif a == 3:
            sellStock(slot)
        elif a == 4:
            addCash(float(input('Cash to Add: ') ), slot)
            loadSlot(slot)
        elif a == 5:
            addCash(-1 * float(input('Cash to Remove: ') ), slot)
            loadSlot(slot)
        elif a == 6:
            showHistory(slot)
            loadSlot(slot)
        elif a == 7:
            return
        elif a == 8:
            confirm = input('Are you sure("y"/"n"): ')
            clear =input('Clear Slot("y"/"n"): ')
            if (confirm == 'y' or confirm == 'Y') and (clear == 'y' or clear == 'Y'):
                clearSlot(slot)
            loadSlot(slot)

# Loads a slot or creates a new on if it does not exist
def loadSlot(choice):
    slot = choice

    # Try to open the accounts csv
    try:
        with open('accounts.csv', 'r+', newline='') as file:
            slotExists = False
            fileReader = csv.DictReader(file)

            # Find the slot in the csv and if so copy down the amount of cash it Shares
            for row in fileReader:
                if int(row['slot']) == choice:
                    cashText = 'Cash: ${:,.2f}'.format(float(row['cash']) )

                    slotExists = True

            # If the slot does not exist then add it to the csv with default values
            if not slotExists:
                fileWriter = csv.DictWriter(file, fieldnames=['slot', 'cash'])
                fileWriter.writerow({'slot' : choice, 'cash' : '100000'})

                cashText = 'Cash: $100,000.00'

            print(cashText)

    # The accounts csv is not created yet so create it
    except FileNotFoundError:
        with open('accounts.csv', 'w', newline='') as file:
            fileWriter = csv.DictWriter(file, fieldnames=['slot', 'cash'])

            fileWriter.writeheader()
            # Add the current slot to the csv with default values
            fileWriter.writerow({'slot' : choice, 'cash' : '100000'})

        print('Cash: $100,000.00')

    # Try to open the slot specific csv which holds the slot's stock data
    try:
        with open(getSlotName(choice), 'r', newline='') as f:
            fReader = csv.DictReader(f)

            # Print out the data in tabel format
            header = 'Stocks:\n'
            print(header)


            header2 = 'Symbol           Buy Price   Quantity'
            print(header2)

            for row in fReader:
                stock = '{}\t         ${:.2f}\t {}'.format(row['Symbol'],
                float(row['Buy_Price']),
                int(row['Quantity']) )

                print(stock)

    except FileNotFoundError:
        noStocks = 'No Stocks in Portfolio',
        print(noStocks)
    print()

# Adds cash to the given slot
def addCash(addedCash, choice):
    with open('accounts.csv', 'r+', newline='') as f:
        fContent =[]
        fReader = csv.DictReader(f)

        # Find the given slot in the accounts csv and update cash
        for row in fReader:
            if int(row['slot']) == choice:
                row['cash'] = float(row['cash']) + addedCash
            # Copies updated content into list
            fContent.append(row)

        # Overwrites the contents of the account csv with the updated contents
        fWriter = csv.DictWriter(f, fieldnames=['slot', 'cash'])
        f.seek(0)
        fWriter.writeheader()

        for row in fContent:
            fWriter.writerow(row)

    # Record the action in the history csv
    if addedCash > 0:
        writeHistory(choice, 'Add Cash', addedCash, None, None)
    elif addedCash < 0:
        writeHistory(choice, 'Remove Cash', addedCash, None, None)

# Buys a stock for a given slot
def buyStock(choice):
    symbol = input('Stock Symbol: ').upper()
    quantity = int(input('Quantity: ') )

    # Make sure the stock symbol is valid
    if lookup(symbol) == None:
        print('Bad Stock Symbol')
        return

    # Open the accounts csv
    with open('accounts.csv', 'r', newline='') as file:
        fileReader = csv.DictReader(file)
        a = []
        # Get the data for the given slot
        for row in fileReader:
            a.append(row)
            if choice == int(row['slot']):
                cash = float(row['cash'])

        price = lookup(symbol)['price']

        # Check if the slot has enough cash to buy "quantity" amount of stock
        if price * quantity > cash:
            print('Not Enough Cash')
            return
        else:
            # Update the cash/ buying the stock
            for row in a:
                if int(row['slot']) == choice:
                    row['cash'] = float(row['cash']) - (price * quantity)

            # Update the accounts csv
            with open('accounts.csv', 'w', newline='') as f:
                fWriter = csv.DictWriter(f, fieldnames=['slot', 'cash'])
                fWriter.writeheader()
                for row in a:
                    fWriter.writerow(row)

    # Updates the csv of the given slot with the newly bought stocks
    try:
        with open(getSlotName(choice), 'r', newline='') as f:
            reader = csv.DictReader(f)
            dict = {}
            for row in reader:
                dict.update(row)
            # Append the data to the end of the file
            with open(getSlotName(choice), 'a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=['Symbol', 'Quantity', 'Buy_Price'])

                stock = lookup(symbol)
                writer.writerow({'Symbol' : symbol, 'Quantity' : quantity,'Buy_Price' : stock['price']})

    # Create a new file and add the bought stock to it
    except FileNotFoundError:
        with open(getSlotName(choice), 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['Symbol', 'Quantity', 'Buy_Price'])
            writer.writeheader()
            stock = lookup(symbol)
            writer.writerow({'Symbol' : symbol, 'Quantity' : quantity,'Buy_Price' : stock['price']})

    # Record the action and load the slot data again
    writeHistory(choice, 'Buy', lookup(symbol)['price'], quantity, symbol)
    loadSlot(choice)

def sellStock(choice):
    cValues = False
    while not cValues:
        try:
            stock = input('Symbol: ').upper()
            amount = int(input('Amount: '))
            price = float(input('Buy Price: '))
            cash = 0.0
        except ValueError:
            cValues = False
        else:
            cValues = True

    try:
        with open(getSlotName(choice), 'r+', newline='') as file:
            fileReader = csv.DictReader(file)
            fileContent = []
            sold =[]

            for row in fileReader:
                fileContent.append(row)

            a = 0
            for s in fileContent:
                if s['Symbol'] == stock and float(s['Buy_Price']) == price:
                    a = a + int(s['Quantity'])

            if a < amount:
                print('Not Enough Shares or No Such Stock in Portfolio.\n')
                return

            for stocks in fileContent:
                 if stocks['Symbol'] == stock and float(stocks['Buy_Price']) == price:
                     if int(stocks['Quantity']) == amount:
                         stocks['Quantity'] = int(stocks['Quantity']) - amount
                         cash = cash + (amount * float(stocks['Buy_Price']))
                         amount = 0
                         continue
                     elif int(stocks['Quantity']) > amount:
                         stocks['Quantity'] = int(stocks['Quantity']) - amount
                         cash = cash + (amount * float(stocks['Buy_Price']))
                         amount = 0
                     elif int(stocks['Quantity']) < amount and amount != 0:
                         amount = amount - int(stocks['Quantity'])
                         cash = cash + (int(stocks['Quantity']) * float(stocks['Buy_Price']))
                         continue
                 sold.append(stocks)

            fileWriter = csv.DictWriter(file, fieldnames=['Symbol', 'Quantity', 'Buy_Price'])
            file.seek(0)
            file.truncate()
            fileWriter.writeheader()
            for row in sold:
                fileWriter.writerow(row)

            addCash(cash, choice)

        writeHistory(choice, 'Sell', price, amount, stock)
        loadSlot(choice)

    except FileNotFoundError:
        print('There are no stocks to sell.\n')
        loadSlot(choice)

def showHistory(choice):
    try:
        with open(getSlotNameH(choice), 'r', newline='') as file:
            fileReader = csv.reader(file)

            print('History: \n')
            for row in fileReader:
                for element in row:
                    print('{} '.format(element), end='')
                print()
        print()
    except FileNotFoundError:
        print('No History\n')

def writeHistory(choice, type, cash, quantity, symbol):
    with open(getSlotNameH(choice), 'a', newline='') as file:
        fileWriter = csv.writer(file)
        if symbol == None:
            fileWriter.writerow([type, cash, datetime.datetime.now()])
        else:
            fileWriter.writerow([type, symbol, cash, quantity, datetime.datetime.now()])

def lookup(symbol):
    """Look up quote for symbol."""

    # reject symbol if it starts with caret
    if symbol.startswith("^"):
        return None

    # Reject symbol if it contains comma
    if "," in symbol:
        return None

    if ' ' in symbol:
        return None

    # Query Yahoo for quote
    # http://stackoverflow.com/a/21351911
    try:

        # GET CSV
        url = f"http://download.finance.yahoo.com/d/quotes.csv?f=snl1&s={symbol}"
        webpage = urllib.request.urlopen(url)

        # Read CSV
        datareader = csv.reader(webpage.read().decode("utf-8").splitlines())

        # Parse first row
        row = next(datareader)

        # Ensure stock exists
        try:
            price = float(row[2])
        except:
            return None

        # Return stock's name (as a str), price (as a float), and (uppercased) symbol (as a str)
        return {
            "price": price,
            }

    except:
        pass

    # Query Alpha Vantage for quote instead
    # https://www.alphavantage.co/documentation/
    try:

        # GET CSV
        url = f"https://www.alphavantage.co/query?apikey=NAJXWIA8D6VN6A3K&datatype=csv&function=TIME_SERIES_INTRADAY&interval=1min&symbol={symbol}"
        webpage = urllib.request.urlopen(url)

        # Parse CSV
        datareader = csv.reader(webpage.read().decode("utf-8").splitlines())

        # Ignore first row
        next(datareader)

        # Parse second row
        row = next(datareader)

        # Ensure stock exists
        try:
            price = float(row[4])
        except:
            return None

        # Return stock's name (as a str), price (as a float), and (uppercased) symbol (as a str)
        return {
            "price": price,
            }

    except:
        return None

def clearSlot(choice):

    try:
        os.unlink( getSlotName(choice) )
    except FileNotFoundError:
        print('', end='')

    with open('accounts.csv', 'r+', newline='') as f:
        fContent =[]
        fReader = csv.DictReader(f)
        for row in fReader:
            if int(row['slot']) == choice:
                row['cash'] = 100000
            fContent.append(row)

        fWriter = csv.DictWriter(f, fieldnames=['slot', 'cash'])
        f.seek(0)
        fWriter.writeheader()
        for row in fContent:
            fWriter.writerow(row)

def getSlotName(choice):
    if choice == 1:
        return('slot1.csv')
    elif choice == 2:
        return('slot2.csv')
    elif choice == 3:
        return('slot3.csv')

def getSlotNameH(choice):
    if choice == 1:
        return('history1.csv')
    elif choice == 2:
        return('history2.csv')
    elif choice == 3:
        return('history3.csv')

if __name__ == "__main__":
    main()