from lxml import etree
parser = etree.XMLParser(remove_comments=True, remove_blank_text=True)

#----------------------------------------------------------------------------

class Fields:  # template for 'Fields'-type tables
    custom = etree.fromstring(
        '<custom_xml>'
            '<before_save>'
                '<get_display_fields/>'
                '<increment_fields_seq/>'
                '<increment_fields_display_seq/>'
            '</before_save>'
            '<after_save>'
                '<check_display_fields/>'
            '</after_save>'
        '</custom_xml>'
        )

#----------------------------------------------------------------------------
