drop table if exists tCtaContab ;
CREATE TABLE tCtaContab (
  pCtaContab    smallint (4)    NOT NULL AUTO_INCREMENT,
  fInstitucion  smallint (4)    NOT NULL,
  cCodigo       varchar (80)    NOT NULL,
  cNombre       varchar (80)    NOT NULL,
  bAbono        char(1)         NOT NULL DEFAULT '0',
  bCargo        char(1)         NOT NULL DEFAULT '0',
  tCreacion     timestamp       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (pCtaContab),
  CONSTRAINT fkCtaContab_institucion   FOREIGN KEY (fInstitucion)   REFERENCES tInstitucion  (pInstitucion)
);

INSERT INTO tCtaContab (fInstitucion,cCodigo,cNombre,bAbono,bCargo,tCreacion) VALUES
	 (1,'01-10-200-2010','PRUEBAS HME','1','0','2021-11-24 21:11:17'),
	 (1,'01-01-020102','PROVEEDORES','0','1','2021-11-29 14:50:03'),
	 (2,'01-02-030101','PRUEBAS TERRAZUL','1','0','2021-12-06 23:38:47'),
	 (1,'0101010101231','Prueba ','0','1','2021-12-08 20:02:32');