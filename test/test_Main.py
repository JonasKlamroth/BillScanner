import unittest
from BillScanner.main import getReceipt
from BillScanner.Receipt import Receipt

class MainTests(unittest.TestCase):

    def test_main(self):
        rec = getReceipt("test/res/test1.jpg")
        self.assertTrue(rec.isSound())
        rec = getReceipt("test/res/test2.jpg")
        self.assertTrue(rec.isSound())
        rec = getReceipt("test/res/test3.jpg")
        self.assertTrue(rec.isSound())
        rec = getReceipt("test/res/test5.jpg")
        self.assertTrue(rec.isSound())
        rec = getReceipt("test/res/test6.jpg")
        self.assertTrue(rec.isSound())
        rec = getReceipt("test/res/test4.gif")
        self.assertTrue(not rec.isSound())


if __name__ == '__main__':
    unittest.main()

