# Library Application (Assessment)

## Overview
My attempt at this assessment was created with the [FastAPI framework](https://fastapi.tiangolo.com/) and [Rabbitmq](https://www.rabbitmq.com/) for interaction between the Frontend/Client and Backend/Admin.
This repo links both of the separate repos, find their links below

## Service Repos
- Frontend/Client Api - https://github.com/JhimmieC137/library-frontend-api.git 
- Backend/Admin Api - https://github.com/JhimmieC137/library-backend-api.git

## Deployments
- Frontend/Client Api - https://library-frontend-api-fsz4.onrender.com/docs
- Backend/Admin Api - https://library-backend-api-9k0h.onrender.com/docs

## Requirements
- [Docker](https://www.docker.com/products/docker-desktop/)
- A .env file to fill the following: 
POSTGRES_TEST_DATABASE=test_db
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DATABASE=
POSTGRES_SERVER=
POSTGRES_PORT=
RABBITMQ_USER=
RABBITMQ_DEFAULT_PASS=
RABBITMQ_HOSTNAME=
RABBITMQ_PORT=


## Running the applications
Clone the repo's and at the root directry run a `docker-compose up`, visit api documentation at [localhost:8000/docs](localhost:8000/docs)

## Frontend/Client Api breakdown

#### Users
- "api/v1/users" --- POST
Enrolls users into the library using their email, firstname and lastname.

- "api/v1/users/find-me" --- POST
Takes a payoad containing a user's email only, and returns the users details, if user exists 

- "api/v1/users/{id}" --- PATCH
Updates enrolled users data

#### Books
- "api/v1/books"  --- GET
Lists all available books (created by the admin), with filter
    * by publishers e.g Wiley, Apress, Manning 
    * by category e.g fiction, technology, science

- "api/v1/books/{id}"  --- GET
Retieves a specific book using its unique ID

#### Transactions
- "api/v1/trasactions" --- POST
This endpoints facilitates the borrowing or returning of books, depending on the status of the transaction. It requires the book's ID, books name, user's ID, user's email, status, to specify on borrowing or returning), and a specified time of return for "borrowing" transactions. New transaction data will be sent to the Backend API on creation.

- "api/v1/transactions" --- GET
To fetch all transactions from a specific user with filters for
    * status (i.e borrowing or returning transactions)
    * book_id (i.e to retrive that user's transactions on a specific book)

- "api/v1/transactions/{id}" --- GET
To fetch specific transaction with it's unique ID


## Backend/Admin Api breakdown
#### Users
- "api/v1/users" --- POST
Creates users into the library using their email, firstname and lastname. New User data will be sent to the Frontend API on creation.

- "api/v1/users/" --- GET
Fetches paginated list of all users filtering by a search on names and email

- "api/v1/users/{id}" --- GET
Retrieves a particular user using their unique ID

- "api/v1/users/{id}" --- PATCH
Updates users data. Updates to user data is sent to the Frontend Api on updating 

#### Books
- "api/v1/books"  --- POST
Adds new books to the database and updates the Frontend service on each newly created book.

- "api/v1/books"  --- GET
Lists all available books (created by the admin), with filter
    * by publishers e.g Wiley, Apress, Manning 
    * by category e.g fiction, technology, science
    * status (i.e If available or borrowed)
    * current holder's id (i.e the current user with book, for getting books a paticular user has borrowed)

- "api/v1/books/{id}"  --- GET
Retieves a specific book using its unique ID

- "api/v1/books/{id}"  --- DELETE
Removes a specific book using its unique ID. This is communicated to the Frontend service when it happens

- "api/v1/books/{id}"  --- PATCH
Updates a certain books deails and informs the Frontend service of details.

#### Transactions
- "api/v1/trasactions" --- POST
To assist users with trouble creating transactions. Transactions created here a also send to the Frontend service

- "api/v1/transactions" --- GET
To fetch all transactions with filters for
    * user's id (i.e transactions by a specific user)
    * status (i.e borrowing or returning transactions)
    * book_id (i.e to retrive that user's transactions on a specific 

- "api/v1/transactions/{id}" --- GET
To fetch specific transaction with it's unique ID