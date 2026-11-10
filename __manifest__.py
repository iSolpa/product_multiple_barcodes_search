{
    'name': 'Product Multiple Barcodes Search Enhancement',
    'version': '17.0.1.5.0',
    'category': 'Inventory',
    'summary': 'Enhances barcode search capabilities for multiple barcodes',
    'description': """
        Extends the Product Multiple Barcodes module to enhance search capabilities
        across all Odoo applications including Point of Sale.
    """,
    'depends': [
        'product_multiple_barcodes',
    ],
    'data': [
        'views/product_search_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
} 