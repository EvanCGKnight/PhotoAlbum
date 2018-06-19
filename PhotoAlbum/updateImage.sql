DELIMITER//
DROP PROCEDURE IF EXISTS updateImage //

CREATE PROCEDURE updateImage(IN titleIn varchar(50), descriptionIn varchar(255))
BEGIN
      UPDATE pictures
      SET description= descriptionIn
      WHERE title=titleIn;
END //
DELIMITER;
