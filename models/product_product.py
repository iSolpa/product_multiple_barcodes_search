from odoo import models, api
import re

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _search(self, domain, *args, **kwargs):
        for sub_domain in list(filter(lambda x: x[0] == "barcode", domain)):
            domain = self._get_barcode_domain(sub_domain, domain)
        return super()._search(domain, *args, **kwargs)

    def _get_barcode_domain(self, sub_domain, domain):
        barcode_operator = sub_domain[1]
        barcode_value = sub_domain[2]
        barcodes = self.env["product.barcode.multi"].search(
            [("name", barcode_operator, barcode_value)]
        )
        return [
            ("barcode_ids", "in", barcodes.ids)
            if x[0] == "barcode" and x[2] == barcode_value
            else x
            for x in domain
        ]
    
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