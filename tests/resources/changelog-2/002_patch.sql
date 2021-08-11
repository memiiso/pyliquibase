--liquibase formatted sql
--changeset liqubasetest:1 splitStatements:false stripComments:true runOnChange:true

INSERT INTO contacts VALUES (1, 'test_value');

CREATE TABLE testtable (
    contact_id INTEGER ,
    first_name TEXT NOT NULL
);

--rollback drop testtable
