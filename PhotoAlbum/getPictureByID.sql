DELIMITER//
DROP PROCEDURE IF EXISTS getPicturesByID //

CREATE PROCEDURE getPicturesByID(IN ID INT)
BEGIN
   SELECT title, pictureID, userID, description
      FROM pictures
      WHERE pictureID = ID;
END  //
DELIMITER;
