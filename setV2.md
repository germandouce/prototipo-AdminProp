## SET PAGO
### POST

Devuelve: 
```json
{
    "nombre_inquilino":"inquilino_que_paga",
    "id_unidad":11111,
    "fecha_de_pago":"2025-08-31",
    "monto":1000
}
```

## SET NUEVO COMPLEJO
### POST

Devuelve:
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

Devuelve:
```json
{
    "id_complejo":1,
    "comision_porcentaje":5
}
```

## SET NUEVA UNIDAD
### POST

Devuelve:
```json
{
    "consorcio":"fiuba",
    "nombre_unidad": "1A"
}
```

## SET NUEVO INQUILINO
### POST

Devuelve:
```json
{
    "nombre":"juan",
    "id_unidad":1
}
```

## SET NUEVO GASTO
### POST

Devuelve:
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

Devuelve:
```json
{
    "id_unidad":1
}
```