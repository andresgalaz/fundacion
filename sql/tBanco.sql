drop table if exists tBanco ;
CREATE TABLE tBanco (
  pBanco    smallint (4)    NOT NULL AUTO_INCREMENT,
  cNombre   varchar (40)    NOT NULL,
  tCreacion timestamp       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (pBanco),
  UNIQUE KEY iuBanco_nombre (cNombre)
);

INSERT INTO tBanco ( cNombre ) values ('Banco Estado');
INSERT INTO tBanco ( cNombre ) values ('Santander');
INSERT INTO tBanco ( cNombre ) values ('BBVA');
INSERT INTO tBanco ( cNombre ) values ('Itau');
INSERT INTO tBanco ( cNombre ) values ('BCI');