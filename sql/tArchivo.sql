drop table if exists tArchivo ;
CREATE TABLE tArchivo (
  pArchivo      int     (11)    NOT NULL AUTO_INCREMENT,
  fInstitucion  smallint (4)    NOT NULL,
  fCtaBanco     smallint (4)    NOT NULL,
  cNombre       varchar(120)    NOT NULL,
  cNombreS3     varchar(120)    NOT NULL,
  cUsuario      varchar (80)    NOT NULL,
  dInicio       date                NULL,
  dTermino      date                NULL,
  nSaldoInicio  decimal(18,2)       NULL,
  nSaldoTermino decimal(18,2)       NULL,
  tCreacion     timestamp       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (pArchivo),
  CONSTRAINT fkArchivo_institucion  FOREIGN KEY (fInstitucion)  REFERENCES  tInstitucion  (pInstitucion),
  CONSTRAINT fkArchivo_ctaBanco     FOREIGN KEY (fCtaBanco)     REFERENCES  tCtaBanco     (pCtaBanco)
);
