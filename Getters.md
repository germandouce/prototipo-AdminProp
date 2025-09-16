# Recursos

## Consortiums
### GET
Devuelve:
```json
{
  "consortiums": [
      {
        "ID": 0,
        "Address": "Av. Paseo Colón 850",
        "UFs Amount": 1000
      },
      {
        "ID": 1,
        "Address": "Calle Falsa 123",
        "UFs Amount": 500
      }
  ]
}
```
POST

## Functional units
### GET
Pide:
```json
{
  "ConsortiumID": 0
}
```
Devuelve:
```json
{
  "functional_units": [
    {
    "id": 0,
    "number": "101",
      
    "owner": "John Doe",
    "area": 75.5
  },
  {
    "ID": 1,
    "ConsortiumID": 0, 
    "Type": "Garage",
    "Number": "G1",
    "Owner": "Jane Smith",
    "Area": 15.0
  }
  ]
}
```