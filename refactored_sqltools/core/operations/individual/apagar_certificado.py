"""
Apagar Certificado Operation

Remove certificado digital do sistema.
"""

from ..base import BaseOperation


class ApagarCertificadoOperation(BaseOperation):
    """Remove certificado digital do sistema."""

    def __init__(self):
        super().__init__(
            name="Apagar Certificado",
            description="Remove certificado digital do sistema",
        )

    def get_sql(self, **params) -> str:
        return """UPDATE PROPRIO
SET PRPCERELE = NULL,
    PRPPWDCER = NULL,
    PRPNUMSERA3 = NULL"""
