import os


class Config:
    SECRET_KEY = os.environ.get("MALL_SECRET", "gold-coin-mall-dev")
    SQLSERVER_DRIVER = os.environ.get("SQLSERVER_DRIVER", "ODBC Driver 18 for SQL Server")
    SQLSERVER_SERVER = os.environ.get("SQLSERVER_SERVER", ".")
    SQLSERVER_DATABASE = os.environ.get("SQLSERVER_DATABASE", "BIDemo_AccumulateCoin")

    @classmethod
    def connection_string(cls):
        return (
            f"DRIVER={{{cls.SQLSERVER_DRIVER}}};SERVER={cls.SQLSERVER_SERVER};"
            f"DATABASE={cls.SQLSERVER_DATABASE};Trusted_Connection=yes;TrustServerCertificate=yes;"
        )
