from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in stock_reconcialiation_per_item_group/__init__.py
from stock_reconcialiation_per_item_group import __version__ as version

setup(
	name="stock_reconcialiation_per_item_group",
	version=version,
	description="Add button to Stock Reconciliation to add product by Item Group",
	author="scopen.fr",
	author_email="technique@scopen.fr",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
