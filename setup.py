from setuptools import setup, find_packages

setup(
    name="crypto_project",
    version="0.1.0",
    description="A multi-agent system for cryptocurrency trading and analysis",
    author="Crypto Project Team",
    packages=find_packages(where="files"),
    package_dir={"": "files"},
    python_requires=">=3.8",
    install_requires=[
        "uagents>=0.6.0",
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
        "cosmpy>=0.9.0",
        "newsapi-python>=0.2.6",
        "web3>=6.4.0",
        "uniswap-universal-router-decoder>=0.8.0",
        "flask>=2.0.0",
        "flask-cors>=3.0.10",
        "fetchai>=0.1.0",
        "uagents-core>=0.1.0",
    ],
    entry_points={
        "console_scripts": [
            "crypto-coin-info=crypto_project.agents.coin_info:main",
            "crypto-fgi=crypto_project.agents.fear_greed_index:main",
            "crypto-news=crypto_project.agents.crypto_news:main",
            "crypto-reward=crypto_project.agents.reward:main",
            "crypto-topup=crypto_project.agents.topup:main",
            "crypto-eth-usdc=crypto_project.agents.swap.eth_usdc:main",
            "crypto-usdc-eth=crypto_project.agents.swap.usdc_eth:main",
            "crypto-swapfinder=crypto_project.agents.swap.swapfinder:main",
        ],
    },
) 