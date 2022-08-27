from prometheus_client.core import Summary, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server, Gauge
from prometheus_api_client import PrometheusConnect

from dotenv import load_dotenv
import asyncio
import logging
from marginpy.logger import setup_logging
from marginpy import MarginfiClient
import os
from os.path import join, dirname

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
setup_logging(logging.INFO)

rpc_endpoint = os.getenv("RPC_ENDPOINT")
environment = os.getenv("ENV")
marginfi_account = os.getenv("MARGINFI_ACCOUNT")
prometheus_endpoint = 9000

logging.basicConfig(
    level=logging.INFO,
)

async def main():
    start_http_server(prometheus_endpoint)
    p = PrometheusClient()
    while True:
        await p.marginfi()

class PrometheusClient:
    def __init__(self):
        self.metrics = "http://localhost:" + str(prometheus_endpoint)
        # self.g = Gauge("marginfi_account", 'Marginfi Account Information', ['marginfi_address', 'borrows', 'balances', 'margin_requirement', 'deposits', 'active_utps'])
        # self.g = Gauge("mango_utp_account", 'Mango UTP Account Information', ['marginfi_address', 'mango_address', 'equity', 'free_collateral', 'liquidation_value'])
        # self.g = Gauge("zo_utp_account", 'Zo UTP Account Information', ['marginfi_address', 'zo_address', 'equity', 'free_collateral', 'liquidation_value'])

        # marginfi gauges
        self.marginfi_total_accounts = Gauge("marginfi_total_accounts", "Marginfi Total Accounts Created", ["marginfi"])
        self.marginfi_borrows = Gauge("marginfi_account_borrows", 'Marginfi Account Borrows', ['marginfi_address'])
        self.marginfi_deposits = Gauge("marginfi_account_deposits", 'Marginfi Account Deposits', ['marginfi_address'])
        # self.marginfi_margin_requirement = Gauge("marginfi_account_margin_requirement", 'Marginfi Account Margin Requirement', ['marginfi_address'])
        self.marginfi_equity = Gauge("marginfi_account_equity", 'Marginfi Account Equity', ['marginfi_address'])
        self.marginfi_assets = Gauge("marginfi_account_assets", 'Marginfi Account Assets', ['marginfi_address'])
        self.marginfi_liabilities = Gauge("marginfi_account_liabilities", 'Marginfi Account Liabilities', ['marginfi_address'])

        # mango gauges
        self.mango_equity = Gauge("mango_account_equity", 'Mango Account Equity', ['mango_address'])
        self.mango_free_collateral = Gauge("mango_account_free_collateral", 'Mango Account Free Collateral', ['mango_address'])
        self.mango_liquidation_value = Gauge("mango_account_liquidation_value", 'Mango Account Liquidation Value', ['mango_address'])

        # zo gauges
        self.zo_equity = Gauge("zo_account_equity", 'Zo Account Equity', ['zo_address'])
        self.zo_free_collateral = Gauge("zo_account_free_collateral", 'Zo Account Free Collateral', ['zo_address'])
        self.zo_liquidation_value = Gauge("zo_account_liquidation_value", 'Zo Account Liquidation Value', ['zo_address'])
        
    async def marginfi(self):
        client = await MarginfiClient.from_env()

        # TODO: Load _all_ accounts here
        all_accounts = await client.load_all_marginfi_account_addresses()

        # setting total accounts gauge
        self.marginfi_total_accounts.labels(marginfi="marginfi").set(len(all_accounts))

        # iterating over all accounts
        for account in all_accounts:
            account = await client.load_marginfi_account(account)

            # await account.observe_utps()
            # marginfi
            active_utps = account.active_utps # can grab all active accounts here?

            authority = account.authority
            borrow = account.borrows
            balances = account.compute_balances()
            equity = balances.equity
            assets = balances.assets
            liabilities = balances.liabilities
            # TODO: compute margins across the board
            # margin_requirement = account.compute_margin_requirement(MarginRequir) # for types of margin to check for see here https://mrgnlabs.github.io/marginfi-sdk/marginpy/html/marginpy.types.html#marginpy.types.MarginRequirement
            deposits = account.deposits

            # mango
            mango_address = account.mango.address
            mango_equity = account.mango.equity
            mango_free_collateral =account.mango.free_collateral
            mango_liquidation_value = account.mango.liquidation_value
            
            # zo
            zo_address = account.zo.address
            zo_equity = account.zo.equity
            zo_free_collateral = account.zo.free_collateral
            zo_liquidation_value = account.zo.liquidation_value

            # Setting marginfi gauges
            self.marginfi_borrows.labels(marginfi_address=authority).set(borrow)
            self.marginfi_deposits.labels(marginfi_address=authority).set(deposits)
            # self.marginfi_margin_requirement.labels(marginfi_address=authority).set(margin_requirement)
            self.marginfi_equity.labels(marginfi_address=authority).set(equity)
            self.marginfi_assets.labels(marginfi_address=authority).set(assets)
            self.marginfi_liabilities.labels(marginfi_address=authority).set(liabilities)

            # Settings mango gauges
            self.mango_equity.labels(mango_address=mango_address).set(mango_equity)
            self.mango_free_collateral.labels(mango_address=mango_address).set(mango_free_collateral)
            self.mango_liquidation_value.labels(mango_address=mango_address).set(mango_liquidation_value)

            # Settings mango gauges
            self.zo_equity.labels(zo_address=zo_address).set(zo_equity)
            self.zo_free_collateral.labels(zo_address=zo_address).set(zo_free_collateral)
            self.zo_liquidation_value.labels(zo_address=zo_address).set(zo_liquidation_value)
    
    # TODO: View funding, open orders, etc

if __name__ == '__main__':
    asyncio.run(main())