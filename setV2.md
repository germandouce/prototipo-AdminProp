## SET PAGO
### POST

Envio: 
```json
{
    "nombre_inquilino":"Guillermo",
    "id_unidad":11111,
    "fecha_de_pago":"2025-08-31",
    "monto":1000
}
```

## SET NUEVO COMPLEJO
### POST

Envio:
```json
{
    "nombre_complejo":"fiuba",
    "nombre_propietario":"propietario_1",
    "direccion":"paseo_colon_850",
    "comision_porcentaje":5
}
```

## SET EDITAR COMISION
### POST

Envio:
```json
{
    "id_complejo":1,
    "comision_porcentaje":5
}
```

## SET NUEVA UNIDAD
### POST

Envio:
```json
{
    "id_consorcio": 2,
    "nombre_unidad": "1A",
    "metros_cuadrados": 50
}
```

## SET NUEVO INQUILINO
### POST

Envio:
```json
{
    "nombre":"juan",
    "id_unidad":1
}
```

## SET NUEVO GASTO
### POST

Envio:
```json
{
    "fecha":"2025-09-16",
    "detalle":"ABL",
    "monto":555.15,
    "id_complejo":1    
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