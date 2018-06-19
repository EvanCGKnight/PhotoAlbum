DROP TABLE IF EXISTS users;
CREATE TABLE users
(
  userID INT NOT NULL auto-increment,
  userName varchar(150) NOT NULL,
  password varchar(255) NOT NULL,
  CONSTRAINT userID_pk PRIMARY KEY (userID)
);
