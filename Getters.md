# Recursos

## Consortiums
### endpoint: /consortiums
### GET
Devuelve:
```json
{
  "consortiums": [
      {
        "id": 0,
        "address": "Av. Paseo Colón 850",
        "ufs_amount": 1000
      },
      {
        "id": 1,
        "address": "Calle Falsa 123",
        "ufs_amount": 500
      }
  ]
}
```
### POST

## Functional units
### endpoint: /functional_units
### GET
Pide:
```json
{
  "consortium_id": 0 // Opcional para filtrar por consorcio
}
```
Devuelve:
```json
{
  "functional_units": [
    {
      "id": 0,
      "unit": "101",
      "occupation_status": true,
      "tentant": "John Doe",
      "consortium_address": "Av. Paseo Colón 850",
      "rent_value": 1500.00,
      "expenses_value": 300.00,
      "debt": 0.00
    },
    {
      "id": 1,
      "unit": "1G",
      "occupation_status": true,
      "tentant": "Jane Smith",
      "consortium_address": "Calle Falsa 123",
      "rent_value": 1200.00,
      "expenses_value": 250.00,
      "debt": 100.00
    }
  ]
}
```
## Payments
### endpoint: /payments
### GET
Pide:
```json
{
  "tentant_id": 0 // Opcional para filtrar por inquilino
}
```
Devuelve:
```json
{
  "payments": [
    {
      "id": 0,
      "amount": 1800.00,
      "date": "2024-02-15"
    },
    {
      "id": 1,
      "amount": 1450.00,
      "date": "2024-01-20"
    }
  ],
  "tentant": "John Doe",
  "last_payment": 1800.00
}
```
## Expenses (gastos comunes)
### endpoint: /expenses
### GET
Pide:
```json
{
  "consortium_id": 0
}
```
Devuelve:
```json
{
  "expenses": [
    {
      "id": 0,
      "description": "Electricidad",
      "amount": 500.00,
      "date": "2024-02-01"
    },
    {
      "id": 1,
      "description": "Agua",
      "amount": 300.00,
      "date": "2024-02-05"
    }
  ]
}
```