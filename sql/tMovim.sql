drop table if exists tMovim ;
CREATE TABLE tMovim (
   pMovim       integer (11)  NOT NULL AUTO_INCREMENT,
   fArchivo     integer (11)  NOT NULL,
   fInstitucion smallint (4)  NOT NULL,
   fCtaBanco    smallint (4)  NOT NULL,
   fCtaContab   smallint (4)  NULL,
   dMovim       date          NOT NULL,
   cSucursal    varchar (40)  NOT NULL,
   cOperacion   varchar (20)  NOT NULL,
   cDescripcion varchar(120)  NOT NULL,
   nAbono       decimal(18,2) NOT NULL,
   nCargo       decimal(18,2) NOT NULL,
   nSaldo       decimal(18,2) NOT NULL,
   tCreacion    timestamp     NOT NULL DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (pMovim),
   CONSTRAINT fkMovim_archivo     FOREIGN KEY (fArchivo)      REFERENCES tArchivo     (pArchivo),
   CONSTRAINT fkMovim_institucion FOREIGN KEY (fInstitucion)  REFERENCES tInstitucion (pInstitucion),
   CONSTRAINT fkMovim_ctaBanco    FOREIGN KEY (fCtaBanco)     REFERENCES tCtaBanco    (pCtaBanco),
   CONSTRAINT fkMovim_ctaContab   FOREIGN KEY (fCtaContab)    REFERENCES tCtaContab   (pCtaContab)
);
