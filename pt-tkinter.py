import csv
import urllib.request
import os
import datetime
from tkinter import *


class App:

    def __init__(self, master):

        # List of things currently in the window
        self.inWindow = []
        # List of things to remove from the window
        self.inWindowTD = []

        self.normalFont = ('times', 16)

        master.title('Hollow Log')

        # Initialize the slot choice menu
        self.frame = Frame(master)
        self.frame.pack()

        self.title = Label(self.frame, text='Hollow Log', font = ('times', 20))
        self.title.pack(side=TOP)
        self.inWindow.append(self.title)

        self.slot1Button = Button(self.frame, text="Slot 1", command=lambda : self.loadSlot(1))
        self.slot1Button.pack()
        self.inWindow.append(self.slot1Button)

        self.slot2Button = Button(self.frame, text="Slot 2", command=lambda : self.loadSlot(2))
        self.slot2Button.pack()
        self.inWindow.append(self.slot2Button)

        self.slot3Button = Button(self.frame, text="Slot 3", command=lambda : self.loadSlot(3))
        self.slot3Button.pack()
        self.inWindow.append(self.slot3Button)

        self.button = Button(
            self.frame, text="QUIT", fg="red", command=self.frame.quit
            )
        self.button.pack(side=TOP)
        self.inWindow.append(self.button)

    # Loads a slot or creates a new on if it does not exist
    def loadSlot(self, choice):
        self.slot = choice
        self.closeCurrentWindow()

        # Try to open the accounts csv
        try:
            with open('accounts.csv', 'r+', newline='') as file:
                slotExists = False
                fileReader = csv.DictReader(file)

                # Find the slot in the csv and if so copy down the amount of cash it shares
                for row in fileReader:
                    if int(row['slot']) == choice:
                        cashText = Label(
                        self.frame,
                        text = 'Cash: ${:,.2f}'.format(float(row['cash']) ),
                        font = self.normalFont )

                        cashText.pack()
                        self.inWindowTD.append(cashText)

                        slotExists = True

                # If the slot does not exist then add it to the csv with default values
                if not slotExists:
                    fileWriter = csv.DictWriter(file, fieldnames=['slot', 'cash'])
                    fileWriter.writerow({'slot' : choice, 'cash' : '100000'})

                    cashText = Label(self.frame,
                    text = 'Cash: $100,000.00',
                    font = self.normalFont)
                    cashText.pack()
                    self.inWindowTD.append(cashText)

        # The accounts csv is not created yet so create it
        except FileNotFoundError:
            with open('accounts.csv', 'w', newline='') as file:
                fileWriter = csv.DictWriter(file, fieldnames=['slot', 'cash'])

                fileWriter.writeheader()
                # Add the current slot to the csv with default values
                fileWriter.writerow({'slot' : choice, 'cash' : '100000'})

            cashText = Label(self.frame,
            text = 'Cash: $100,000.00',
            font = self.normalFont)
            cashText.pack()
            self.inWindowTD.append(cashText)

        # Try to open the slot specific csv which holds the slot's stock data
        try:
            with open(self.getSlotName(), 'r', newline='') as f:
                fReader = csv.DictReader(f)

                # Print out the data in tabel format
                header = Label(self.frame,
                text = 'Stocks:\n',
                font = self.normalFont)
                header.pack()
                self.inWindowTD.append(header)

                header2 = Label(self.frame,
                text = 'Symbol               Buy Price   Quantity',
                font = self.normalFont)
                header2.pack()
                self.inWindowTD.append(header2)

                for row in fReader:
                    stock = Label(self.frame,
                    text = '{}\t         ${:.2f}\t {}'.format(row['Symbol'],
                    float(row['Buy_Price']),
                    int(row['Quantity']) ),
                    font = self.normalFont)
                    stock.pack()
                    self.inWindowTD.append(stock)

        except FileNotFoundError:
            noStocks = Label(self.frame,
            text = 'No Stocks in Portfolio',
            font = self.normalFont)
            noStocks.pack()
            self.inWindowTD.append(noStocks)

        self.showMenu()

        backButton = Button(self.frame, text = 'Back', command = self.showSlots)
        backButton.pack()
        self.inWindowTD.append(backButton)

        clearSlotButton = Button(self.frame, text = 'Clear Slot', command = self.clearSlotCheck)
        clearSlotButton.pack()
        self.inWindowTD.append(clearSlotButton)

    # Removes objects from the current window
    def closeCurrentWindow(self):
        for widgets in self.inWindow:
            widgets.pack_forget()

        for widgets in self.inWindowTD:
            widgets.destroy()
        self.inWindowTD = []

    def showSlots(self):
        self.closeCurrentWindow()
        for widget in self.inWindow:
            widget.pack()

    # Displays the main menu
    def showMenu(self):
        lookUpButton = Button(self.frame, text = 'Look Up', command = self.find)
        lookUpButton.pack()
        self.inWindowTD.append(lookUpButton)

        buyStockButton = Button(self.frame, text = 'Buy Stock', command = self.buyMenu)
        buyStockButton.pack()
        self.inWindowTD.append(buyStockButton)

        sellStockButton = Button(self.frame, text = 'Sell Stock', command = self.sellMenu)
        sellStockButton.pack()
        self.inWindowTD.append(sellStockButton)

        addCashButton = Button(self.frame, text = 'Add Cash', command =lambda : self.changeCashMenu(True))
        addCashButton.pack()
        self.inWindowTD.append(addCashButton)

        removeCashButton = Button(self.frame, text = 'Remove Cash', command =lambda : self.changeCashMenu(False))
        removeCashButton.pack()
        self.inWindowTD.append(removeCashButton)

        showHistoryButton = Button(self.frame, text = 'History', command = self.showHistory)
        showHistoryButton.pack()
        self.inWindowTD.append(showHistoryButton)

    # Display the lookup stock menu
    def find(self):
        self.closeCurrentWindow()
        lookUpText = Label(self.frame, text = 'Look Up\n', font = self.normalFont)
        lookUpText.pack()
        self.inWindowTD.append(lookUpText)

        e = Entry(self.frame)
        e.pack()
        e.insert(0, 'Symbol')
        self.inWindowTD.append(e)

        enterButton = Button(self.frame, text = 'Submit', command =lambda : self.findPrice(e.get().upper()))
        enterButton.pack()
        self.inWindowTD.append(enterButton)

        backButton = Button(self.frame, text = 'Back', command = self.backToMenu)
        backButton.pack()
        self.inWindowTD.append(backButton)

        self.priceText = Label(self.frame, text = '', font = self.normalFont)
        self.priceText.pack()
        self.inWindowTD.append(self.priceText)

    # Lookup and return price if it exists
    # Symbol: String
    def findPrice(self, symbol):
        price = self.lookup(symbol)
        if price == None:
            self.priceText['text'] = 'Bad Stock Symbol'
        else:
            self.priceText['text'] = '$'+str(price['price'])

    # Display the buy stock menu
    def buyMenu(self):
        self.closeCurrentWindow()

        buyStockText = Label(self.frame,
        text = 'Buy Stocks\n',
        font = self.normalFont)
        buyStockText.pack()
        self.inWindowTD.append(buyStockText)

        e = Entry(self.frame)
        e.pack()
        e.insert(0, 'Symbol')
        self.inWindowTD.append(e)

        n = Entry(self.frame)
        n.pack()
        n.insert(0, 'Quantity')
        self.inWindowTD.append(n)

        buyButton = Button(self.frame, text = 'Buy', command =lambda : self.buy(e.get().upper(), int(n.get()) ) )
        buyButton.pack()
        self.inWindowTD.append(buyButton)

        backButton = Button(self.frame, text = 'Back', command = self.backToMenu)
        backButton.pack()
        self.inWindowTD.append(backButton)

    # Buys a stock for a given slot
    # symbol: String
    # quantity: int
    def buy(self, symbol, quantity):

        # Make sure the stock symbol is valid
        if self.lookup(symbol) == None:
            badSymbol = Label(self.frame,
            text = 'Bad Stock Symbol.\n',
            font = self.normalFont)
            NotEnoughShares.pack()
            self.inWindowTD.append(badSymbol)
            return

        # Open the accounts csv
        with open('accounts.csv', 'r', newline='') as file:
            fileReader = csv.DictReader(file)

            # Get the data for the given slot
            for row in fileReader:
                if self.slot == int(row['slot']):
                    cash = float(row['cash'])

            price = self.lookup(symbol)['price']

            if price * quantity > cash:
                notEnoughCashText = Label(self.frame,
                text = 'Not Enough Cash',
                font = self.normalFont)
                return

            # Update the slots cash
            self.addCash(-(price * quantity), True)

        try:
            with open(self.getSlotName(), 'r', newline='') as f:
                reader = csv.DictReader(f)
                dict = {}
                for row in reader:
                    dict.update(row)
                # Append the data to the end of the file
                with open(self.getSlotName(), 'a', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=['Symbol', 'Quantity', 'Buy_Price'])

                    stock = self.lookup(symbol)
                    writer.writerow({'Symbol' : symbol, 'Quantity' : quantity,'Buy_Price' : stock['price']})

        # Create a new file and add the bought stock to it
        except FileNotFoundError:
            with open(self.getSlotName(), 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=['Symbol', 'Quantity', 'Buy_Price'])
                writer.writeheader()
                stock = self.lookup(symbol)
                writer.writerow({'Symbol' : symbol, 'Quantity' : quantity,'Buy_Price' : stock['price']})

        # Record the action and load the slot data again
        self.writeHistory('Buy', self.lookup(symbol)['price'], quantity, symbol)
        self.backToMenu()

    # Displays the sell stock menu
    def sellMenu(self):
        self.closeCurrentWindow()

        sellStockText = Label(self.frame,
        text = 'Sell Stocks\n',
        font = self.normalFont)
        sellStockText.pack()
        self.inWindowTD.append(sellStockText)

        s = Entry(self.frame)
        s.pack()
        self.inWindowTD.append(s)
        s.insert(0, 'Symbol')

        q = Entry(self.frame)
        q.pack()
        self.inWindowTD.append(q)
        q.insert(0, 'Quantity')

        p = Entry(self.frame)
        p.pack()
        self.inWindowTD.append(p)
        p.insert(0, 'Price')

        sellButton = Button(self.frame, text = 'Sell',
        command =lambda : self.sell(s.get().upper(), int(q.get()), float(p.get())))
        sellButton.pack()
        self.inWindowTD.append(sellButton)

        backButton = Button(self.frame, text = 'Back', command = self.backToMenu)
        backButton.pack()
        self.inWindowTD.append(backButton)

    # Sells stock from a given slot
    def sell(self, symbol, quantity, price):

        # Do nothing if the values are invalid
        try:
            symbol = symbol.upper()
            amount = int(quantity)
            price = float(price)
            cash = 0.0
        except:
            return


        try:
            with open(self.getSlotName(), 'r+', newline='') as file:
                fileReader = csv.DictReader(file)
                fileContent = []
                notSold = []

                # Copy the contents of the csv into the list
                for row in fileReader:
                    fileContent.append(row)

                # Find the correct stock in the file and count up how many shares of it
                # is owned
                a = 0
                for s in fileContent:
                    if s['Symbol'] == symbol and float(s['Buy_Price']) == price:
                        a = a + int(s['Quantity'])

                # If the amount of stock in the file is less than the amout the user
                # wants to sell abort action
                print(a)
                if a < amount:

                    NotEnoughShares = Label(self.frame,
                    text = 'Not Enough Shares or No Such Stock in Portfolio.\n',
                    font = self.normalFont)
                    NotEnoughShares.pack()
                    self.inWindowTD.append(NotEnoughShares)
                    return

                # Remove the desired amount of stock from the file and add the stock's
                # value to the slot's cash
                remaining = amount
                for stocks in fileContent:
                    # Finding the correct stock and price
                     if stocks['Symbol'] == symbol and float(stocks['Buy_Price']) == price:
                          # If there is not enough stock in one entry then subtract from
                          # the amount to remove and then also remove the entry
                         if int(stocks['Quantity']) == remaining:
                             stocks['Quantity'] = int(stocks['Quantity']) - remaining
                             cash = cash + (remaining * float(stocks['Buy_Price']))
                             remaining = 0
                             continue
                         # If there is not enough stock in one entry then subtract from
                         # the amount to remove and then also remove the entry
                         if int(stocks['Quantity']) >= remaining:
                             stocks['Quantity'] = int(stocks['Quantity']) - remaining
                             cash = cash + (remaining * float(stocks['Buy_Price']))
                             remaining = 0
                        # If there is enough stock in on entry then remove from that entry's
                        # quantity
                         elif int(stocks['Quantity']) < remaining and remaining != 0:
                             remaining = remaining - int(stocks['Quantity'])
                             cash = cash + (int(stocks['Quantity']) * float(stocks['Buy_Price']))
                             continue
                    # Keep track of the entries that were not removed
                     notSold.append(stocks)

                fileWriter = csv.DictWriter(file, fieldnames=['Symbol', 'Quantity', 'Buy_Price'])
                file.seek(0)
                file.truncate()
                fileWriter.writeheader()
                for row in notSold:
                    fileWriter.writerow(row)

                # Add the cash obtained from selling to the slot
                self.addCash(cash, True)


            self.writeHistory('Sell', price, amount, symbol)
            self.backToMenu()

        except FileNotFoundError:
            NoStocks = Label(self.frame,
            text = 'There are no stocks to sell.\n',
            font = self.normalFont)

    # Display menu for adding/removing cash
    # opp: True=add, False=remove
    def changeCashMenu(self, opp):
        self.closeCurrentWindow()

        changeCashText = Label(self.frame,
        font = self.normalFont)
        changeCashText.pack()

        self.inWindowTD.append(changeCashText)

        if opp:
            changeCashText['text'] = 'Add Cash'
        elif not opp:
            changeCashText['text'] = 'Remove Cash'

        c = Entry(self.frame)
        c.pack()
        self.inWindowTD.append(c)

        if opp:
            c.insert(0, 'Enter Cash to Add')
        elif not opp:
            c.insert(0, 'Enter Cash to Remove')

        if opp:
            changeCashButton = Button(self.frame, text = 'Submit',
            command = lambda : self.addCash(int(c.get()), False))
        elif not opp:
            changeCashButton = Button(self.frame, text = 'Submit',
            command = lambda : self.addCash(-int(c.get()), False))
        changeCashButton.pack()
        self.inWindowTD.append(changeCashButton)

        backButton = Button(self.frame, text = "Back", command = self.backToMenu)
        backButton.pack()
        self.inWindowTD.append(backButton)

    # Adds cash to the given slot
    # addedCash: flaot
    # choice: int, 1|2|3
    # buyOrSell: Bool
    def addCash(self, addedCash, buyOrSell = False):
        with open('accounts.csv', 'r+', newline='') as f:
            fContent =[]
            fReader = csv.DictReader(f)

            # Find the given slot in the accounts csv and update cash
            for row in fReader:
                if int(row['slot']) == self.slot:
                    row['cash'] = float(row['cash']) + addedCash
                # Copies updated content into list
                fContent.append(row)

            # Overwrites the contents of the account csv with the updated contents
            fWriter = csv.DictWriter(f, fieldnames=['slot', 'cash'])
            f.seek(0)
            fWriter.writeheader()

            for row in fContent:
                fWriter.writerow(row)

        if not buyOrSell:
            if addedCash > 0:
                self.writeHistory('Add Cash', addedCash, None, None)
            elif addedCash < 0:
                self.writeHistory('Remove Cash', addedCash, None, None)

        self.backToMenu()

    # Displays the given slots action history
    def showHistory(self):
        self.closeCurrentWindow()

        try:
            with open(self.getSlotNameH(), 'r', newline='') as file:
                fileReader = csv.reader(file)

                title = Label(self.frame,
                text = 'History\n',
                font = self.normalFont)
                title.pack()
                self.inWindowTD.append(title)

                for row in fileReader:
                    text = ''
                    for element in row:
                        text = text + element + ' '
                    historyElement = Label(
                    self.frame,
                    text = text,
                    font = self.normalFont
                    )
                    historyElement.pack()
                    self.inWindowTD.append(historyElement)

        except FileNotFoundError:
            noHistory = Label(self.frame,
            text = 'No History\n',
            font = self.normalFont)
            noHistory.pack()
            self.inWindowTD.append(noHistory)

        backButton = Button(self.frame, text = 'Back', command = self.backToMenu)
        backButton.pack()
        self.inWindowTD.append(backButton)

    # Closes current window and displays the main menu
    def backToMenu(self):
        self.closeCurrentWindow()
        self.loadSlot(self.slot)

    # Displays a window to confirm clearing of slot
    def clearSlotCheck(self):
        check = Button(self.frame, text = 'Are You Sure?', command = self.clearSlot)
        check.pack()
        self.inWindowTD.append(check)

    # Resets a slot's data to intial default values
    def clearSlot(self):
            try:
                os.unlink(self.getSlotName() )
            except FileNotFoundError:
                pass
            else:
                os.unlink(self.getSlotNameH())

            # Resets the slot's cash to the intial value in the accounts file
            with open('accounts.csv', 'r+', newline='') as f:
                fContent =[]
                fReader = csv.DictReader(f)

                # Copy data in file and update the row of corresponding slot
                for row in fReader:
                    if int(row['slot']) == self.slot:
                        row['cash'] = 100000
                    fContent.append(row)

                # Overwrite file with updated data
                fWriter = csv.DictWriter(f, fieldnames=['slot', 'cash'])
                f.seek(0)
                fWriter.writeheader()
                for row in fContent:
                    fWriter.writerow(row)
            self.backToMenu()

    # Gives the name of the slot based on the chioce
    def getSlotName(self):
        if self.slot == 1:
            return('slot1.csv')
        elif self.slot == 2:
            return('slot2.csv')
        elif self.slot == 3:
            return('slot3.csv')

    # Gives the name of the slot history file based on the chioce
    def getSlotNameH(self):
        if self.slot == 1:
            return('history1.csv')
        elif self.slot == 2:
            return('history2.csv')
        elif self.slot == 3:
            return('history3.csv')

    def lookup(self, symbol):
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

    # Adds a row to the give slot's history file
    # type: string, add/remove cash, buy/sell stock
    # quantity: int, amount of stock bought or sold
    # symbol: sting|None, Symbol of the stock bought or sold
    def writeHistory(self, type, cash, quantity, symbol):
        with open(self.getSlotNameH(), 'a', newline='') as file:
            fileWriter = csv.writer(file)
            if symbol == None:
                fileWriter.writerow([type, cash, datetime.datetime.now()])
            else:
                fileWriter.writerow([type, symbol, cash, quantity, datetime.datetime.now()])

root = Tk()

app = App(root)

root.mainloop()
