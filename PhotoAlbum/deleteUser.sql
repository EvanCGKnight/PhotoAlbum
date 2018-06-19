DELIMITER//
DROP PROCEDURE IF EXISTS deleteUser //

CREATE PROCEDURE deleteUser(IN nameIn varchar(50))
BEGIN
    DELETE FROM users
           WHERE username=nameIn;
END //
DELIMITER;
