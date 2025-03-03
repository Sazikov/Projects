CREATE TABLE Role (
    Id SERIAL PRIMARY KEY,
    Name VARCHAR(50) NOT NULL
);

CREATE TABLE Users (
    Id_user SERIAL PRIMARY KEY,
    Login VARCHAR(30) UNIQUE NOT NULL,
    Password VARCHAR(20) NOT NULL,
    RoleID INTEGER NOT NULL REFERENCES Role(Id),
    Phone VARCHAR(11) NOT NULL
);

CREATE TABLE Shop (
    Id SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Adress VARCHAR(255) NOT NULL,
    Id_user INTEGER REFERENCES Users(Id_user)

);

CREATE TABLE Category (
    Id SERIAL PRIMARY KEY,
    Name VARCHAR(100)
);

CREATE TABLE Product (
    Id_product SERIAL PRIMARY KEY,
    Id_category INTEGER NOT NULL REFERENCES Category(Id)
);

CREATE TABLE Presence (
    Id_product INTEGER REFERENCES Product(Id_product),
    Id_shop INTEGER REFERENCES Shop(Id),
    Quantity INTEGER DEFAULT 0 CHECK (Quantity >= 0),
    PRIMARY KEY (Id_product, Id_shop)
);

CREATE TABLE Orders (
    Id SERIAL PRIMARY KEY,
    Id_user INTEGER REFERENCES Users(Id_user),
    Date DATE NOT NULL,
    Status VARCHAR(50) DEFAULT '0'
);

CREATE TABLE Order_items (
    Id SERIAL PRIMARY KEY,
    Id_order INTEGER REFERENCES Orders(Id),
    Id_product INTEGER REFERENCES Product(Id_product),
    Quantity INTEGER DEFAULT 1 CHECK (Quantity >= 1),
    FOREIGN KEY (Id_order) REFERENCES Orders(Id),
    FOREIGN KEY (Id_product) REFERENCES Product(Id_product)
);



