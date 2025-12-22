"""
Operation Selector Component

Extracts operation selection logic from original code.
Implements operation description display.
Adds date range inputs for NCM queries.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QComboBox, 
                            QGroupBox, QDateEdit)
from PyQt5.QtCore import pyqtSignal, QDate


class OperationSelector(QWidget):
    """Reusable operation selector component"""
    
    # Signals
    operation_changed = pyqtSignal(str)  # operation_name
    sql_updated = pyqtSignal(str)  # sql_text
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.operations = {}
        self.setup_ui()
        self.setup_styles()
        self.load_operations()
    
    def setup_ui(self):
        """Setup the operation selector UI"""
        layout = QVBoxLayout(self)
        
        # Operation selection group
        operation_group = QGroupBox("Selecione a Operação")
        operation_layout = QVBoxLayout(operation_group)
        
        # Operation combo box
        self.operation_combo = QComboBox()
        self.operation_combo.currentTextChanged.connect(self.on_operation_changed)
        operation_layout.addWidget(self.operation_combo)
        
        # Operation description
        self.operation_description = QLabel()
        self.operation_description.setWordWrap(True)
        self.operation_description.setStyleSheet("color: #7f8c8d; padding: 10px; font-style: italic;")
        operation_layout.addWidget(self.operation_description)
        
        # Date range fields for NCM queries
        self.date_start_label = QLabel("Data Início:")
        self.date_start_edit = QDateEdit()
        self.date_start_edit.setCalendarPopup(True)
        self.date_start_edit.setDate(QDate.currentDate().addDays(-30))
        self.date_start_edit.dateChanged.connect(self.on_date_changed)
        
        self.date_end_label = QLabel("Data Fim:")
        self.date_end_edit = QDateEdit()
        self.date_end_edit.setCalendarPopup(True)
        self.date_end_edit.setDate(QDate.currentDate())
        self.date_end_edit.dateChanged.connect(self.on_date_changed)
        
        operation_layout.addWidget(self.date_start_label)
        operation_layout.addWidget(self.date_start_edit)
        operation_layout.addWidget(self.date_end_label)
        operation_layout.addWidget(self.date_end_edit)
        
        # Initially hide date fields
        self.date_start_label.setVisible(False)
        self.date_start_edit.setVisible(False)
        self.date_end_label.setVisible(False)
        self.date_end_edit.setVisible(False)
        
        layout.addWidget(operation_group)
    
    def setup_styles(self):
        """Setup component styles"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #34495e;
            }
            QComboBox, QDateEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                color: #2c3e50;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #2c3e50;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #41aaf0;
            }
            QComboBox:hover, QDateEdit:hover {
                border: 1px solid #3498db;
            }
        """)
    
    def load_operations(self):
        """Load available operations"""
        self.operations = {
            "Cancelar Cupom": {
                "description": "Cancela todos os cupons (STACUP e STACUPVRF = 'F')",
                "check_sql": "SELECT STACUP, STACUPVRF FROM CAIXA",
                "execute_sql": "UPDATE CAIXA SET STACUP='F', STACUPVRF='F'"
            },
            "Apagar Certificado": {
                "description": "Remove certificado digital do sistema",
                "execute_sql": """UPDATE PROPRIO
SET PRPCERELE = NULL,
    PRPPWDCER = NULL,
    PRPNUMSERA3 = NULL"""
            },
            "Corrigir Erro de Equipamento": {
                "description": "Remove número de série do caixa",
                "execute_sql": "UPDATE CAIXA SET CXASERNUM = NULL"
            },
            "Limpar Tabelas do Fisco": {
                "description": "Remove todos os dados das tabelas fiscais",
                "execute_sql": """EXECUTE BLOCK AS BEGIN
  DELETE FROM FISCO_PRODUTOAUX;
  DELETE FROM FISCO_DOCUMENTOFISCAL;
  DELETE FROM FISCO_CUPOMFISCAL;
  DELETE FROM FISCO_INVENTARIO;
  DELETE FROM FISCO_REDUCAO;
  DELETE FROM FISCO_ITEMDOCUMENTOFISCAL;
  DELETE FROM FISCO_ITEMCUPOMFISCAL;
  DELETE FROM FISCO_PRODUTO;
  DELETE FROM FISCO_ITEMINVENTARIO;
END"""
            },
            "Consultar Transações": {
                "description": "Consulta as transações na tabela TRANSACAO",
                "execute_sql": "SELECT * FROM TRANSACAO"
            },
            "Consultar Proprio": {
                "description": "Consulta os dados da tabela PROPRIO",
                "execute_sql": "SELECT * FROM PROPRIO"
            },
            "Consultar NCM Inexistente": {
                "description": "Consulta transações com NCM inexistente no período",
                "execute_sql": """SELECT 
    TRNNFCENUM AS NOTA,
    T.TRNDAT AS DATA, 
    PROCOD AS PRODUTO,
    T.CXANUM AS CAIXA,
    ITVSEQ AS SEQ_ITEM,
    ITVNCM AS NCM,
    TRNMENSNFE AS ERRO
FROM TRANSACAO_XMLNOTA tx 
INNER JOIN TRANSACAO t  ON TX.TRNSEQ = T.TRNSEQ AND TX.TRNDAT = T.TRNDAT AND TX.CXANUM = T.CXANUM  
INNER JOIN ITEVDA i ON TX.TRNSEQ = I.TRNSEQ AND TX.TRNDAT = I.TRNDAT AND TX.CXANUM = i.CXANUM  
WHERE 
TX.TRNDAT BETWEEN '{data_inicio}' AND '{data_fim}'
AND TRNMENSNFE LIKE '%Rejeicao: Informado NCM inexistente%'
AND CAST(ITVSEQ AS INTEGER) =
CAST( SUBSTRING(TRNMENSNFE FROM POSITION('nItem:' IN TRNMENSNFE) + 6 FOR POSITION(']' IN TRNMENSNFE)- (POSITION('nItem:' IN TRNMENSNFE) + 6))AS INTEGER);"""
            }
        }
        
        # Populate combo box
        self.operation_combo.clear()
        self.operation_combo.addItems(list(self.operations.keys()))
        
        # Initialize with first operation
        if self.operations:
            self.on_operation_changed()
    
    def on_operation_changed(self):
        """Handle operation selection change"""
        operation_name = self.operation_combo.currentText()
        if not operation_name or operation_name not in self.operations:
            return
        
        operation = self.operations[operation_name]
        
        # Update description
        self.operation_description.setText(operation["description"])
        
        # Show/hide date fields for NCM query
        if operation_name == "Consultar NCM Inexistente":
            self.date_start_label.setVisible(True)
            self.date_start_edit.setVisible(True)
            self.date_end_label.setVisible(True)
            self.date_end_edit.setVisible(True)
        else:
            self.date_start_label.setVisible(False)
            self.date_start_edit.setVisible(False)
            self.date_end_label.setVisible(False)
            self.date_end_edit.setVisible(False)
        
        # Update SQL
        self.update_sql()
        
        # Emit signal
        self.operation_changed.emit(operation_name)
    
    def on_date_changed(self):
        """Handle date change for NCM queries"""
        self.update_sql()
    
    def update_sql(self):
        """Update and emit SQL text"""
        operation_name = self.operation_combo.currentText()
        if not operation_name or operation_name not in self.operations:
            return
        
        operation = self.operations[operation_name]
        sql = operation.get("execute_sql", "")
        
        # Add check SQL if available
        if operation.get("check_sql"):
            sql = f"-- Verificação:\n{operation['check_sql']}\n\n-- Execução:\n{sql}"
        
        # Format SQL for NCM query with dates
        if operation_name == "Consultar NCM Inexistente":
            data_inicio = self.date_start_edit.date().toString("yyyy-MM-dd")
            data_fim = self.date_end_edit.date().toString("yyyy-MM-dd")
            sql = operation["execute_sql"].format(data_inicio=data_inicio, data_fim=data_fim)
        
        self.sql_updated.emit(sql)
    
    def get_current_operation(self):
        """Get current operation details"""
        operation_name = self.operation_combo.currentText()
        if not operation_name or operation_name not in self.operations:
            return None
        
        operation = self.operations[operation_name].copy()
        operation['name'] = operation_name
        
        # Add formatted dates for NCM query
        if operation_name == "Consultar NCM Inexistente":
            operation['data_inicio'] = self.date_start_edit.date().toString("yyyy-MM-dd")
            operation['data_fim'] = self.date_end_edit.date().toString("yyyy-MM-dd")
        
        return operation
    
    def get_formatted_sql(self):
        """Get SQL formatted with current parameters"""
        operation = self.get_current_operation()
        if not operation:
            return ""
        
        sql = operation.get("execute_sql", "")
        
        # Format SQL for NCM query with dates
        if operation['name'] == "Consultar NCM Inexistente":
            sql = sql.format(
                data_inicio=operation['data_inicio'],
                data_fim=operation['data_fim']
            )
        
        return sql
    
    def set_operation(self, operation_name):
        """Set current operation by name"""
        if operation_name in self.operations:
            index = list(self.operations.keys()).index(operation_name)
            self.operation_combo.setCurrentIndex(index)