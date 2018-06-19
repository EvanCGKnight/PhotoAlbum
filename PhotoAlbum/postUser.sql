DELIMITER//
DROP PROCEDURE IF EXISTS postUser //

CREATE PROCEDURE postUser(IN nameIn varchar(50), passwordIn varchar(255))
BEGIN
    INSERT INTO users(username, password)
           VALUES(nameIn, passwordIn);
END //
DELIMITER;
