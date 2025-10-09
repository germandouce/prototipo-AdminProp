## POST /payments
## Crea un nuevo pago en la tabla 
Envio: 
```json
POST /payments
{
  "tenant_name": "John Doe",
  "id_unit": 0,
  "date": "2025-08-31",
  "amount": 1000
}
```

## POST /consortiums
### Crear un nuevo consorcio
POST /consortiums
```json
{
  "address": "Av. Paseo Colón 850",
  "ufs_amount": 1000
}
```

## POST /functional_units
## Crea una unidad funcional nuevo en el 
POST /functional_units
```json
{
  "unit_number": "001",
  "unit_name": "1A",
  "occupation_status": true,
  "tenant": "John Doe",
  "consortium_id": 0,              // ID del consorcio al que pertenece la unidad
  //no hace falta el nombre del consorcio lo obtenemos dde el endpoint con otra consulta
  // o lo dejamos para no equivocarenos ni en pedo en nignun lado?
  //esrta ultima no me parce mal. a la mirda con "lo correcto?"
  "consortium_address": "Av. Paseo Colón 850",
  "rent_value": 1500.00,
  "expenses_value": 300.00,
  "surface":10,
  "debt": 0.00
}
```

## POST /expenses
## Crear un nuevo gasto/expesna
POST /expenses
```json
{
  "description": "ABL",
  "amount": 555.15,
  "date": "2025-09-16",
  "consortium_id": 1
}
```

## POST /owners_reports
## Crear Crea una rendición de propietario
POST /owners_reports
```json
{
  "consortium_id": 0,
  "month_of_year": "2024-02",
  "total_incomes": 3000.00,
  "total_outcomes": 800.00,
  "administration_percentage": 10.0,
  "administration_fee": 220.00,
  "net_income": 1880.00
}
```

## POST /administration_fee
## Crea una comisión de administración
POST /administration_fee
```json
{
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
```



## estos no harian falta xq el nombre del inqulino esta directamente metido en la unidad funcional
## cuando cambia el inqulino lo modificamos sobre la unidad funcional...
## no me gusta pero es mas simples, es cierto....


## SET NUEVO INQUILINO
### POST

Envio:
```json
{
    "nombre":"juan",
    "id_unidad":1
}
```

## SET DESOCUPAR
### POST

Envio:
```json
{
    "id_unidad":1
}
```