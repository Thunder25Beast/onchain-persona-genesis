##API Endpoints

Health Check

URL: /api/health
Method: GET
Returns server and model status
Analyze Wallet

URL: /api/wallet/analyze
Method: POST
Request Body:
    {
    "wallet_address": "0x742d35cc6634c0532925a3b844bc454e4438f44e",
    "detailed": true,
    "hf_token": "optional_huggingface_token"
    }
Returns wallet persona and basic stats

Get Wallet Stats

URL: /api/wallet/stats
Method: GET
Query Parameters:
wallet_address
Returns detailed wallet statistics
Generate HTML Report

URL: /api/wallet/report
Method: POST
Request Body:
    {
    "wallet_address": "0x742d35cc6634c0532925a3b844bc454e4438f44e",
    "detailed": true
    }
Returns an HTML report for the wallet

Fetch Wallet from API

URL: /api/wallet/fetch
Method: POST
Request Body:
    {
    "wallet_address": "0x742d35cc6634c0532925a3b844bc454e4438f44e"
    }
Returns wallet data fetched directly from Moralis API



