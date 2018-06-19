DROP TABLE IF EXISTS pictures;
CREATE TABLE pictures
(
  title varchar(50) NOT NULL,
  pictureID INT NOT NULL auto-increment,
  userID INT,
  description varchar(255),
  image BLOB,
  CONSTRAINT pictures_pk PRIMARY KEY (pictureID),
  CONSTRAINT users_fk FOREIGN KEY (userID) REFERENCES users(userID)
);
