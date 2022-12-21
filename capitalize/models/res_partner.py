from odoo import api, models, fields

class Partner_Fields(models.Model):
    _inherit = 'res.partner'


    capitalize_name_contact = fields.Char(
        compute='capitalize_name', 
        readonly= True
    )

    capitalize_street_contact = fields.Char(
        compute = 'capitalize_street',
        readonly = True,
    )
    
    @api.depends('name')
    def capitalize_name(self):
        if self.name is not False:
            name_new = self.name.upper() # Nombre de contacto en mayuscula
            ''' name_split = self.name.split()
            new_name_concat = []
            for i in name_split:
                if i.isupper():
                    new_name_concat.append(i)
                else:
                    new_name_concat.append(i.title())
            # capitalize_comprehesions = [i.capitalize() for i in name_split]
            name_new = " ".join(new_name_concat)
            '''
            self.update({'capitalize_name_contact': name_new})
            self.update({'name': name_new})
        else:
            self.update({'capitalize_name_contact': ''})


    @api.depends('street')
    def capitalize_street(self):
        if self.street is not False:
            street_split = self.street.split()
            capitalize_comprehesions = [i.capitalize() for i in street_split]
            street_new = " ".join(capitalize_comprehesions)
            self.update({'capitalize_street_contact': street_new})
            self.update({'street': street_new})
        else:
            self.update({'capitalize_street_contact': ''})

    
    
        

