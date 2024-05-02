import os
import re
import csv
from institution.interface import InstitutionInterface
from institution.models import Transaction

class InstitutionRBC(InstitutionInterface):
    _pdf_cnt = ""
    _re_openingbal = r'(PREVIOUS|Previous) (STATEMENT|ACCOUNT|Account) (BALANCE|Balance) (?P<balance>-?\$[\d,]+\.\d{2})(?P<cr>(\-|\s?CR))?'
    _re_closingbal = r'(?:NEW|CREDIT) BALANCE (?P<balance>-?\$[\d,]+\.\d{2})(?P<cr>(\-|\s?CR))?'
    _re_trx = (r"^(?P<dates>(?:\w{3} \d{2} ){2})"
            r"(?P<description>.+)\s"    
            r"(?P<amount>-?\$[\d,]+\.\d{2}-?)(?P<cr>(\-|\s?CR))?")

    _openingbal = 0
    _closingbal = 0
    _trxs = []

    def __init__(self):
        pass

    def load_stmt_pdf(self, cnt) -> None:
        self._pdf_cnt = cnt
        self._openingbal = self._parse_opening_balance()
        self._closingbal = self._parse_closing_balance()
        self._trxs = self._parse_transactions()
        self._validate_balance()
        self._write_csv()


    def _parse_opening_balance(self) -> int:
        print("Parsing opening balance", end="...")
        match = re.search(self._re_openingbal, self._pdf_cnt)
        if (match.groupdict()['cr'] and '-' not in match.groupdict()['balance']):
            balance = float("-" + match.groupdict()['balance'].replace('$', ''))
            print("patched credit balance found for opening balance: %f" % balance)
            return balance

        balance = float(match.groupdict()['balance'].replace(',', '').replace('$', ''))
        print("%f" % balance)
        return balance

    def _parse_closing_balance(self) -> int:
        print("Parsing closing balance", end="...")
        match = re.search(self._re_closingbal, self._pdf_cnt)
        if (match.groupdict()['cr'] and '-' not in match.groupdict()['balance']):
            balance = float("-" + match.groupdict()['balance'].replace('$', ''))
            print("patched credit balance found for closing balance: %f" % balance)
            return balance
        
        balance = float(match.groupdict()['balance'].replace(',', '').replace('$', '').replace(' ', ''))
        print("%f" % balance)
        return balance

    def _parse_transactions(self) -> list:
        result = []
        for match in re.finditer(self._re_trx, self._pdf_cnt, re.MULTILINE):
            match_dict = match.groupdict()
            date = match_dict['dates'].replace('/', ' ') # change format to standard: 1/2 -> 1 2
            date = date.split(' ')[0:2]  # Jan. 2 Jan. 3 -> ['Jan.', '2']
            date[0] = date[0].strip('.') # Jan. -> Jan
            date = ' '.join(date)
             
            # checks credit balance regex
            if (match_dict['cr']):
                # credit balance found
                amount = -float("-" + match_dict['amount'].replace('$', '').replace(',', ''))
            else:
                amount = -float(match_dict['amount'].replace('$', '').replace(',', ''))

            # checks description regex
            if ('$' in match_dict['description']):
                newAmount = re.search(r'(?P<amount>-?\$[\d,]+\.\d{2}-?)(?P<cr>(\-|\s?CR))?', match_dict['description'])
                amount = -float(newAmount['amount'].replace('$', '').replace(',', ''))
                match_dict['description'] = match_dict['description'].split('$', 1)[0]

            transaction = Transaction(date,
                                      match_dict['description'],
                                      amount)
            # NOTE: We're not accounting for the possibility of duplicate transactions
            result.append(transaction)
        return result


    def _validate_balance(self) -> bool:
        print("Validating balance", end="...")
        net = round(sum([t.amount for t in self._trxs]), 2)
        outflow = round(sum([t.amount for t in self._trxs if t.amount < 0]), 2)
        inflow = round(sum([t.amount for t in self._trxs if t.amount > 0]), 2)
        if round(self._openingbal - self._closingbal, 2) != net:
            print("discrepancy found!")
            print("Diff is: %f vs. %f" % (self._openingbal - self._closingbal, net))
            print(f"Net/Inflow/Outflow: {net} / {inflow} / {outflow}")
            return False
        print("success!")
        return True

    def _write_csv(self, filepath="./output.csv") -> None:
        print("Writing CSV", end="...")
        has_header = False
        exists = os.path.isfile(filepath)
        if exists:
            with open(filepath, 'r', newline='') as f:
                r = csv.reader(f)
                # Check if the file has a header by peeking at the first line
                has_header = next(r, None) is not None  # Read first line (if exists)
        with open(filepath, "a" if has_header else "w", newline="") as f:
            writer = csv.writer(f, quotechar='"', quoting=csv.QUOTE_ALL)
            if not has_header:
                writer.writerow(["Date", "Description", "Amount"])
            for t in self._trxs:
                row = [t.date, t.description, t.amount]
                writer.writerow(row)
        print("done!")
