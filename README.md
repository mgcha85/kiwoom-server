# FastAPI Application

This project is a FastAPI application designed to manage account, order, market data, and condition search functionalities. It is structured to provide a clear separation of concerns, making it easy to maintain and extend.

## Project Structure

```
my-fastapi-app
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── routes
│   │   ├── __init__.py
│   │   ├── account.py
│   │   ├── order.py
│   │   ├── market.py
│   │   ├── condition.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── kiwoom_service.py
│   │   ├── utils.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── order.py
│   │   ├── market.py
│   │   ├── condition.py
├── tests
│   ├── test_account.py
│   ├── test_order.py
│   ├── test_market.py
│   ├── test_condition.py
├── config
│   ├── config.py
├── logs
│   ├── kiwoom_restful.log
├── requirements.txt
├── README.md
```

## Features

- **Account Management**: API endpoints for managing user accounts.
- **Order Management**: API endpoints for placing and managing orders.
- **Market Data Retrieval**: API endpoints for fetching market data.
- **Condition Search**: API endpoints for searching based on specific conditions.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/my-fastapi-app.git
   cd my-fastapi-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the FastAPI application, execute the following command:
```
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` to access the interactive API documentation.

## Logging

Application logs are stored in the `logs/kiwoom_restful.log` file.

## Testing

To run the tests, use the following command:
```
pytest
```

## License

This project is licensed under the MIT License. See the LICENSE file for more details.