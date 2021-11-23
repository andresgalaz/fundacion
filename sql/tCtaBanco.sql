drop table if exists tCtaBanco;
CREATE TABLE tCtaBanco (
  pCtaBanco     smallint (4)    NOT NULL AUTO_INCREMENT,
  fInstitucion  smallint (4)    NOT NULL,
  fBanco        smallint (4)    NOT NULL,
  cNombre       varchar (40)        NULL,
  cCuenta       varchar (20)    NOT NULL,
  tCreacion     timestamp       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (pCtaBanco),
  UNIQUE KEY iuCtaBanco_cuenta (cCuenta),
  CONSTRAINT fkCtaBanco_institucion FOREIGN KEY (fInstitucion)  REFERENCES tInstitucion (pInstitucion),
  CONSTRAINT fkCtaBanco_banco       FOREIGN KEY (fBanco)        REFERENCES tBanco       (pBanco)
);
