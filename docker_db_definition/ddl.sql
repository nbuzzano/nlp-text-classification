CREATE DATABASE mydatabase;
USE mydatabase;

#init DB
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS models;
DROP TABLE IF EXISTS predictions;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE models (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), version VARCHAR(255), description VARCHAR(255));

CREATE TABLE predictions (id INT AUTO_INCREMENT PRIMARY KEY, document_id VARCHAR(255), predicted_class VARCHAR(255), date_created DATETIME, time_spent INT, model_id INT, FOREIGN KEY(model_id) REFERENCES models(id));

#insert models dummy data
INSERT INTO models (name, version, description) 
VALUES ("LSTM", "2.5.1", "the r2 score was improved");
VALUES ("LSTM", "2.5.0", "the r2 score was improved");

#insert predictions dummy data
INSERT INTO predictions (document_id, predicted_class, date_created, time_spent, model_id)
VALUES ("1231231", "CL", now(), 100, 1);