import tempfile
import unittest
from pathlib import Path
from types import ModuleType
import sys

sqlserver_stub = ModuleType("db.sqlserver")
sqlserver_stub.execute = lambda *args, **kwargs: None
sqlserver_stub.one = lambda *args, **kwargs: None
sqlserver_stub.rows = lambda *args, **kwargs: []
sys.modules.setdefault("db.sqlserver", sqlserver_stub)
from services import mall_service as mall


class CartQuantityTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.original_wallet_file = mall.WALLET_FILE
        mall.WALLET_FILE = Path(self.tmpdir.name) / "wallets.json"

    def tearDown(self):
        mall.WALLET_FILE = self.original_wallet_file
        self.tmpdir.cleanup()

    def test_updates_cash_cart_quantity(self):
        mall.add_cash_cart({"product_id": "cash-01", "qty": "2"}, customer_id=1001)

        mall.update_cash_cart({"product_id": "cash-01", "qty": "5"}, customer_id=1001)

        items = mall.cart_items(customer_id=1001)
        self.assertEqual(1, len(items))
        self.assertEqual(5, items[0]["qty"])
        self.assertEqual(649500, items[0]["line_total_cents"])
        self.assertEqual(49995, items[0]["line_reward_coin"])

    def test_wallet_data_includes_cash_cart_summary(self):
        mall.add_cash_cart({"product_id": "cash-01", "qty": "2"}, customer_id=1001)
        mall.add_cash_cart({"product_id": "cash-03", "qty": "1"}, customer_id=1001)

        wallet = mall.wallet_data(customer_id=1001)

        self.assertEqual(3, wallet["cash_cart_count"])
        self.assertEqual("2697.00", wallet["cash_cart_total"])
        self.assertEqual(20196, wallet["cash_cart_reward_coin"])


if __name__ == "__main__":
    unittest.main()
