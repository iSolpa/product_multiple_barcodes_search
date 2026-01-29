from odoo import models, api
import re
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, order=None):
        """
        Override name search to support bracket format barcode searches.
        Handles searches like "[1200161307829]" by extracting the barcode from brackets.
        Delegates all other searches to parent module.
        """
        args = args or []
        
        # Try to extract barcode from bracket format [barcode]
        if name:
            barcode_match = re.match(r'^\[([^\]]+)\]', name)
            if barcode_match:
                barcode_value = barcode_match.group(1)
                _logger.info(f"Bracket search: extracted barcode '{barcode_value}' from '{name}'")
                
                # Search main barcode field
                products = self.search([('barcode', '=', barcode_value)] + args, limit=limit, order=order)
                
                # Also search additional barcodes
                if not products:
                    additional = self.env["product.barcode.multi"].search([('name', '=', barcode_value)])
                    if additional:
                        products = self.search([('barcode_ids', 'in', additional.ids)] + args, limit=limit, order=order)
                
                if products:
                    _logger.info(f"Bracket search found: {products.ids}")
                    return products.ids
        
        # Delegate to parent module for all other searches
        return super()._name_search(name=name, args=args, operator=operator, limit=limit, order=order) 