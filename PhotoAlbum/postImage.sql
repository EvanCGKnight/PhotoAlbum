DELIMITER//
DROP PROCEDURE IF EXISTS postImage //

CREATE PROCEDURE postImage(IN titleIn varchar(50), userIDIn INT, descriptionIn varchar(255), imageIn BLOB)
BEGIN
    INSERT INTO pictures(title, userID, description, image)
           VALUES(titleIn, userIDIn, descriptionIn, imageIn);
END //
DELIMITER;
