DELIMITER//
DROP PROCEDURE IF EXISTS deleteImage //

CREATE PROCEDURE deleteImage(IN titleIn varchar(50))
BEGIN
    DELETE FROM pictures
           WHERE title=titleIn;
END //
DELIMITER;
