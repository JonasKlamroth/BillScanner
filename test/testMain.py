import unittest
from BillScanner import main as BillScanner
from BillScanner.Receipt import Receipt

class MainTests(unittest.TestCase):

    def test_main(self):
        rec = BillScanner.getReceipt("res/test1.jpg")
        pass


if __name__ == '__main__':
    unittest.main()

