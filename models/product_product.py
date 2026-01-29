from odoo import models, api
import re

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _search(self, domain, *args, **kwargs):
        domain = self._expand_barcode_domain(list(domain) if domain else [])
        return super()._search(domain, *args, **kwargs)

    def _expand_barcode_domain(self, domain):
        """
        Expand barcode domain items to search in both main barcode AND additional barcodes.
        Replaces ('barcode', op, val) with '|', ('barcode', op, val), ('barcode_ids', op, val)
        """
        new_domain = []
        for item in domain:
            if isinstance(item, (list, tuple)) and len(item) == 3 and item[0] == 'barcode':
                # Add OR condition: main barcode OR additional barcodes
                new_domain.extend(['|', item, ('barcode_ids', item[1], item[2])])
            else:
                new_domain.append(item)
        return new_domain
    
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, order=None):
        """
        Override name search to support barcode searches including bracket format.
        Handles searches like "[1200161307829] ENERGEN LUX (9.5)" by extracting
        the barcode from brackets and searching in both main and additional barcodes.
        Falls back to parent module's search which handles name, default_code, and barcodes.
        """
        args = args or []
        
        # Try to extract barcode from bracket format [barcode]
        barcode_match = re.match(r'^\[([^\]]+)\]', name) if name else None
        
        if barcode_match:
            # Extract the barcode from brackets
            barcode_value = barcode_match.group(1)
            
            # Search for products with this barcode in main barcode field
            products_by_main_barcode = self.search(
                [('barcode', '=', barcode_value)] + args,
                limit=limit,
                order=order
            )
            
            # Search for products with this barcode in additional barcodes
            additional_barcodes = self.env["product.barcode.multi"].search([
                ('name', '=', barcode_value)
            ])
            products_by_additional_barcode = self.search(
                [('barcode_ids', 'in', additional_barcodes.ids)] + args,
                limit=limit,
                order=order
            )
            
            # Combine results (union to avoid duplicates)
            products = products_by_main_barcode | products_by_additional_barcode
            
            if products:
                return products.ids
        
        # If no bracket format or no results, check if it's a plain barcode search
        if name:
            # Try exact barcode match
            products_by_main_barcode = self.search(
                [('barcode', '=', name)] + args,
                limit=limit,
                order=order
            )
            
            # Try additional barcodes
            additional_barcodes = self.env["product.barcode.multi"].search([
                ('name', '=', name)
            ])
            products_by_additional_barcode = self.search(
                [('barcode_ids', 'in', additional_barcodes.ids)] + args,
                limit=limit,
                order=order
            )
            
            products = products_by_main_barcode | products_by_additional_barcode
            
            if products:
                return products.ids
        
        # Fall back to parent module's name search (handles name, default_code, barcodes)
        return super()._name_search(
            name=name,
            args=args,
            operator=operator,
            limit=limit,
            order=order
        ) 