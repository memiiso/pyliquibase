--liquibase formatted sql

--changeset liqubasetest:1 splitStatements:false stripComments:true runOnChange:true

CREATE TABLE contacts (
    contact_id INTEGER ,
    first_name TEXT NOT NULL
);

--rollback
