# Recursos

## Consortiums
### GET
Devuelve:
```json
{
  "Consortium1": {
    "ID": 0,
    "Address": "Av. Paseo Colón 850",
    "UFs Amount": 1000
  },
  "Consortium2": {
    "ID": 1,
    "Address": "Calle Falsa 123",
    "UFs Amount": 500
  }
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
  "FunctionalUnit1": {
    "ID": 0,
    "ConsortiumID": 0,
    "Type": "Apartment",
    "Number": "101",
    "Owner": "John Doe",
    "Area": 75.5
  },
  "FunctionalUnit2": {
    "ID": 1,
    "ConsortiumID": 0, 
    "Type": "Garage",
    "Number": "G1",
    "Owner": "Jane Smith",
    "Area": 15.0
  }
}
```