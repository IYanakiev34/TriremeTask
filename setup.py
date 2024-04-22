from setuptools import setup, find_packages

setup(
    name='KrakenExchangeAPI',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'websocket-client'
    ],
    entry_points={
        'console_scripts': [
            'kraken-api=kraken_api.kraken_exchange:main'
        ],
    },
    description='Custom API interface for the Kraken cryptocurrency exchange.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Ivan Yanakiev',
    author_email='ivan.y.yanakiev@gmail.com',
    url='https://github.com/IYanakiev34/TriremeTask',
    keywords='Kraken API Cryptocurrency Exchange Websocket',
    license='MIT',
)
