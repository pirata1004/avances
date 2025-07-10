
CREATE TABLE Pruebas (
  ID int NOT NULL AUTO_INCREMENT,
  nom varchar(255),
  tipo varchar(255),
  PRIMARY KEY (ID)
);

INSERT INTO Pruebas(nom, tipo)
VALUES ('PRUEBA', 'PRUEBA');

SELECT * FROM pruebas
WHERE nom LIKE 'D%';
