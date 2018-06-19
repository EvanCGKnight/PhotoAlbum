DELIMITER//
DROP PROCEDURE IF EXISTS getYourPictureID//

CREATE PROCEDURE getYourPictureID(IN usernameIn varchar)
BEGIN
   SELECT  MAX(pictureID)
      FROM pictures
      WHERE username = usernameIn;
END  //
DELIMITER;
