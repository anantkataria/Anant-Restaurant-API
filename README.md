### This project is part of a Meta Backend developer Specialization.

## Purpose 

fully functioning API project for any restaurant so that the client application developers can use the APIs to develop web and mobile applications. People with different roles will be able to browse, add and edit menu items, place orders, browse orders, assign delivery crew to orders and finally deliver the orders. 

There are three roles to consider: Manager, Delivery Crew and Customer (Those who are not manager and not delivery crew).

APIs are built using Django Rest Framework(DRF) and utilize class based views from generics library of DRF. It also implements Token Based Authentication with Djoser library. It is easily extensible to JWT token system.
APIs levarage pagination and throttling techniques as well, which help limiting server load and avoid abuse related to overloading. Other functionalities include filtering and searching support.

## API Endpoints:

- User registration and token generation:
  ![image](https://github.com/anantkataria/Little-Lemon-Restaurant-API/assets/51715043/20b4900d-8695-4974-ba7d-6469b81d6ea2)

  
- Menu-items endpoints:
  ![image](https://github.com/anantkataria/Little-Lemon-Restaurant-API/assets/51715043/3670c6fe-f8be-42e2-8747-7d9777cba67d)

  
- User group management endpoints:
  ![image](https://github.com/anantkataria/Little-Lemon-Restaurant-API/assets/51715043/09f48e66-be6e-4eb0-9a7f-9f1b444fb4b3)

  
- Cart management endpoints:
  ![image](https://github.com/anantkataria/Little-Lemon-Restaurant-API/assets/51715043/39264f7e-3c92-48cd-9eb4-29ca1d6569b0)

  
- Order management endpoints
  ![image](https://github.com/anantkataria/Little-Lemon-Restaurant-API/assets/51715043/2b19f127-0715-4770-a6b8-d5bf546cc681)
