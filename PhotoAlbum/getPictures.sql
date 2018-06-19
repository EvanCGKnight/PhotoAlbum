DELIMITER //
DROP PROCEDURE IF EXISTS getPictures //

CREATE PROCEDURE getPictures()
BEGIN
  SELECT title, pictureID, userID, description
  		FROM pictures
END //
DELIMITER ;
