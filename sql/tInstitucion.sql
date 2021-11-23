drop table if exists tInstitucion ;
CREATE TABLE tInstitucion (
  pInstitucion  smallint (4)    NOT NULL AUTO_INCREMENT,
  cNombre       varchar(120)    NOT NULL,
  tCreacion     timestamp       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (pInstitucion)
);
insert into tInstitucion ( cNombre ) values ('INSTALACIONES DE CLIMAS ARTIFICIALES LIMITAD');
insert into tInstitucion ( cNombre ) values ('FUNDACION CRECER');
