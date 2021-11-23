drop table if exists tCtaContab ;
CREATE TABLE tCtaContab (
  pCtaContab    smallint (4)    NOT NULL AUTO_INCREMENT,
  fInstitucion  smallint (4)    NOT NULL,
  cCodigo       varchar (80)    NOT NULL,
  cNombre       varchar (80)    NOT NULL,
  tCreacion     timestamp       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (pCtaContab),
  CONSTRAINT fkCtaContab_institucion   FOREIGN KEY (fInstitucion)   REFERENCES tInstitucion  (pInstitucion)
);
