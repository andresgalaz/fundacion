drop table if exists tInstitucionUsuario ;
drop table if exists tUsuario ;
CREATE TABLE tUsuario (
  pUsuario      smallint (4)    NOT NULL AUTO_INCREMENT,
  cUsuario      varchar (80)    NOT NULL,
  cNombre       varchar (80)    NOT NULL,
  cEmail        varchar (120)   NOT NULL,
  cEstado       varchar (20)    NOT NULL,
  bEnable       char    (1)     NOT NULL DEFAULT '1',
  tCreacion     timestamp       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (pUsuario),
  UNIQUE KEY iuUsuario_cUsuario (cUsuario)
);
CREATE TABLE tInstitucionUsuario (
  pUsuario      smallint (4)    NOT NULL,
  pInstitucion  smallint (4)    NOT NULL,
  PRIMARY KEY (pUsuario,pInstitucion),
  CONSTRAINT fkInstUsr_institucion   FOREIGN KEY (pInstitucion) REFERENCES tInstitucion  (pInstitucion),
  CONSTRAINT fkInstUsr_usuario       FOREIGN KEY (pUsuario)     REFERENCES tUsuario      (pUsuario)
);

