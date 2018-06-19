DELIMITER//
DROP PROCEDURE IF EXISTS getUserByID //

CREATE PROCEDURE getUserByID(IN ID INT)
BEGIN
   SELECT username
      FROM picture
      WHERE pictureID = ID;
END  //
DELIMITER;