DELIMITER//
DROP PROCEDURE IF EXISTS getPicturesByUserID //

CREATE PROCEDURE getPicturesByID(IN userIDIn INT)
BEGIN
   SELECT title, pictureID, userID, description
      FROM pictures
      WHERE userID = userIDIn;
END  //
DELIMITER;
