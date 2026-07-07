import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from urllib.parse import urlparse

sqlserver_stub = ModuleType("db.sqlserver")
sqlserver_stub.execute = lambda *args, **kwargs: None
sqlserver_stub.one = lambda *args, **kwargs: None
sqlserver_stub.rows = lambda *args, **kwargs: []
sys.modules.setdefault("db.sqlserver", sqlserver_stub)

import app as mall_app
from services import mall_service as mall


class CartRouteTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.original_wallet_file = mall.WALLET_FILE
        self.original_gift_by_id = mall.gift_by_id
        mall.WALLET_FILE = Path(self.tmpdir.name) / "wallets.json"
        mall_app.app.config.update(TESTING=True)
        self.client = mall_app.app.test_client()
        with self.client.session_transaction() as session:
            session["role"] = "user"
            session["customer_id"] = 1001
            session["account_id"] = 2001
            session["login_name"] = "tester"

    def tearDown(self):
        mall.gift_by_id = self.original_gift_by_id
        mall.WALLET_FILE = self.original_wallet_file
        self.tmpdir.cleanup()

    def test_shop_add_to_cart_redirects_to_cart_with_item(self):
        response = self.client.post("/shop", data={"product_id": "cash-01", "qty": "2"})

        self.assertEqual(302, response.status_code)
        location = urlparse(response.headers["Location"])
        self.assertEqual("/cart", location.path)
        self.assertEqual("cash-cart", location.fragment)
        items = mall.cart_items(customer_id=1001)
        self.assertEqual(1, len(items))
        self.assertEqual("cash-01", items[0]["id"])
        self.assertEqual(2, items[0]["qty"])

    def test_points_mall_add_to_cart_redirects_to_cart_with_item(self):
        mall.gift_by_id = lambda gift_id: {
            "GiftID": int(gift_id),
            "GiftName": "测试礼品",
            "GfitCoin": 120,
            "GiftNum": 9,
            "GiftCategory": "测试",
            "Image": "1.jpg",
        }

        response = self.client.post("/points-mall", data={"gift_id": "7", "qty": "3"})

        self.assertEqual(302, response.status_code)
        location = urlparse(response.headers["Location"])
        self.assertEqual("/cart", location.path)
        self.assertEqual("points-cart", location.fragment)
        items = mall.points_cart_items(customer_id=1001)
        self.assertEqual(1, len(items))
        self.assertEqual(7, items[0]["GiftID"])
        self.assertEqual(3, items[0]["qty"])

    def test_wallet_data_includes_points_cart_summary(self):
        mall.gift_by_id = lambda gift_id: {
            "GiftID": int(gift_id),
            "GiftName": "测试礼品",
            "GfitCoin": 120,
            "GiftNum": 9,
            "GiftCategory": "测试",
            "Image": "1.jpg",
        }
        mall.add_points_cart({"gift_id": "7", "qty": "3"}, customer_id=1001)

        wallet = mall.wallet_data(customer_id=1001)

        self.assertEqual(3, wallet["points_cart_count"])
        self.assertEqual(360, wallet["points_cart_coin"])


if __name__ == "__main__":
    unittest.main()
