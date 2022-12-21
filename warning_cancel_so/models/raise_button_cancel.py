from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import api, fields, models, SUPERUSER_ID, _
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    def action_cancel(self):
        # Raise
        for order in self:
            for inv in order.invoice_ids:
                if inv and inv.state not in ('cancel', 'draft'):
                    raise UserError(_("No se puede cancelar este pedido de venta. Primero debe cancelar las facturas de clientes relacionadas."))
        #Cancelation of orders
        documents = None
        for sale_order in self:
            if sale_order.state == 'sale' and sale_order.order_line:
                sale_order_lines_quantities = {order_line: (order_line.product_uom_qty, 0) for order_line in sale_order.order_line}
                documents = self.env['stock.picking']._log_activity_get_documents(sale_order_lines_quantities, 'move_ids', 'UP')
        self.mapped('picking_ids').action_cancel()
        if documents:
            filtered_documents = {}
            for (parent, responsible), rendering_context in documents.items():
                if parent._name == 'stock.picking':
                    if parent.state == 'cancel':
                        continue
                filtered_documents[(parent, responsible)] = rendering_context
            self._log_decrease_ordered_quantity(filtered_documents, cancel=True)
        return super(SaleOrder, self).action_cancel()