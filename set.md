## SET PAGO
### POST

Devuelve: 
```json
{
    "inquilino":"inquilino_que_paga",
    "id_cliente":11111,
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
    "direccion":"paseo_colon_850",
    "cantidad_uf":50,
    "comision_porcentaje":5
}
```

## SET EDITAR COMISION
### POST

Devuelve:
```json
{
    "nombre_complejo":"fiuba",
    "comision_porcentaje":5
}
```

## SET NUEVA UNIDAD
### POST

Devuelve:
```json
{
    "consorcio":"fiuba",
    "nro_unidad":25,
    "ocupado":"no",
    "cliente":"-",
    "direc_imagen":"www.com",
    "monto":1111
}
```

## SET NUEVO INQUILINO
### POST

Devuelve:
```json
{
    "nombre":"juan",
    "consorcio":"fiuba",
    "nro_unidad":25
}
```

## SET NUEVO GASTO
### POST

Devuelve:
```json
{
    "fecha":"2025-09-16",
    "detalle":"ABL",
    "monto":555.15
}
```

## SET DESOCUPAR
### POST

Devuelve:
```json
{
    "nro_unidad":1111,
    "consorcio":"fiuba"
}
```