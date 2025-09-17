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
  "consortium_id": 0 // Opcional para filtrar por consorcio, sino trae todas las unidades
}
```
Devuelve:
```json
{
  "functional_units": [
    {
      "id": 0,
      "unit_number": "001",
      "unit_name": "1A",
      "occupation_status": true,
      "tentant": "John Doe",
      "consortium_address": "Av. Paseo Colón 850",
      "rent_value": 1500.00,
      "expenses_value": 300.00,
      "debt": 0.00
    },
    {
      "id": 1,
      "unit_number": "002",
      "unit_name": "1B",
      "occupation_status": true,
      "tentant": "Jane Smith",
      "consortium_address": "Av. Paseo Colón 850",
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
  "tentant_name": "John Doe", 
  "id_unit": 0
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

## Rendición de propietarios
### endpoint: /owners_reports
### GET
Pide:
```json
{
  "consortium_id": 0,
  "month_of_year": "2024-02"
}
```
Devuelve:
```json
{
  "owner_report": {
    "consortium_address": "Av. Paseo Colón 850",
    "month_of_year": "2024-02",
    "total_incomes": 3000.00,
    "total_outcomes": 800.00,
    "administration_percentage": 10.0,
    "administration_fee": 220.00,
    "net_income": 1880.00
  }
}
```
## Comisión de administración
### endpoint: /administration_fee
### GET
Pide:
```json
{
  "month_of_year": "2024-02"
}
```
Devuelve:
```json
{
  "administration_fee": {
    "month_of_year": "2024-02",
    "total_administration_fee": 400.00,
    "details": [
      {
        "consortium_address": "Av. Paseo Colón 850",
        "administration_percentage": 10.0,
        "total_incomes": 3000.00,
        "administration_fee": 300.00
      },
      {
        "consortium_address": "Calle Falsa 123",
        "administration_percentage": 5.0,
        "total_incomes": 2000.00,
        "administration_fee": 100.00
      }
    ]
  }
}
```