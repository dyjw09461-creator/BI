import os


class Config:
    SECRET_KEY = os.environ.get("BI_TRAINING_SECRET", "bi-training-dev")
    SQLSERVER_DRIVER = os.environ.get("SQLSERVER_DRIVER", "ODBC Driver 18 for SQL Server")
    SQLSERVER_SERVER = os.environ.get("SQLSERVER_SERVER", ".")
    SQLSERVER_DATABASE = os.environ.get("SQLSERVER_DATABASE", "BIDemo_AccumulateCoin")
    DW_DATABASE = os.environ.get("DW_DATABASE", "BI_GoldCoin_DW")
    SQLSERVER_TRUSTED = os.environ.get("SQLSERVER_TRUSTED", "yes")
    SQLSERVER_TRUST_CERT = os.environ.get("SQLSERVER_TRUST_CERT", "yes")

    @classmethod
    def connection_string(cls, database=None):
        db = database or cls.SQLSERVER_DATABASE
        return (
            f"DRIVER={{{cls.SQLSERVER_DRIVER}}};"
            f"SERVER={cls.SQLSERVER_SERVER};"
            f"DATABASE={db};"
            f"Trusted_Connection={cls.SQLSERVER_TRUSTED};"
            f"TrustServerCertificate={cls.SQLSERVER_TRUST_CERT};"
        )
