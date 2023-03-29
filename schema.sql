CREATE TABLE IF NOT EXISTS messages (
    message_id  BIGINT PRIMARY KEY,
    monday      BIGINT[],
    tuesday     BIGINT[],
    wednesday   BIGINT[],
    thursday    BIGINT[],
    friday      BIGINT[],
    saturday    BIGINT[]
);