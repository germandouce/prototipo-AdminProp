## PUT /functional_units 
## Actualizar datos de una unidad funcional
## TAMbien sirve para desocupar. le ponemos "-" en el tentant 
PUT /functional_units
```json
{
    "id": 10,                     // ID de la unidad a modificar
    "unit_number": "003",
    "unit_name": "1B",
    "occupation_status": true,    //ESTEEEEE
    "tentant": "Juan Pérez",      //Y ESTEEEE SONN LOS IMPORTANTES. PERO MANDAMOS TDOOS PARA SEGUIR REST DE MANUAL
    "consortium_address": "paseo_colon_900",
    "rent_value": 1300.00,
    "expenses_value": 350.00,
    "debt": 0.00
}
```

## PUT /administration_fee
## Actualizar comisión de administración:
```json
PUT /administration_fee
{
    "month_of_year": "2024-02",
    "total_administration_fee": 420.00,
    "details": [
        {
            "consortium_address": "Av. Paseo Colón 850",
            "administration_percentage": 10.0,
            "total_incomes": 3200.00,
            "administration_fee": 320.00
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


## creo q este es igual q el de arriba....
## VER
## SET EDITAR COMISION
### POST

Envio:
```json
{
    "id_complejo":1,
    "comision_porcentaje":5
}
```

## los de aca abajo no creo q los usemos...,.................

## PUT /payments
## Actualizar un pago existente:
## comentarios: no creo q lo usemos
PUT /payments
{
    "id": 123,                    // ID del pago a modificar
    "tentant_name": "Guillermo",
    "id_unit": 11111,
    "date": "2025-09-01",
    "amount": 1200
}


## PUT /consortiums
## Actualizar DATOS de un consorcio:
## comentarios: no creo q lo usemos
PUT /consortiums
{
    "id": 1,                     // ID del consorcio a modificar
    "address": "paseo_colon_900",
    "ufs_amount": 1200
}

## PUT /expenses
## Actualizar un gasto existente:
## comentarios: no creo q lo usemos
PUT /expenses
{
    "id": 5,                      // ID del gasto a modificar
    "description": "Luz",
    "amount": 600.00,
    "date": "2025-09-20",
    "consortium_id": 1
}