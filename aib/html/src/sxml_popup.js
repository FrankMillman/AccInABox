function sxml_popup(sxml) {

  var popup = get_sxml_popup();

  popup.sxml = sxml;

  popup.readonly = !sxml.amendable();

  var comment_xml = sxml.value.split('\f');  // ASCII ff used to join
  var comment = comment_xml[0], xml_code = comment_xml[1];

  popup.comment = comment;
  popup.xml_code = xml_code;

  if (popup.readonly) {
    popup.comment_area.style.background = '#CCFFCC';
    popup.xml_area.style.background = '#CCFFCC';
    }

  document.body.appendChild(popup);
  var max_x = (max_w - popup.offsetWidth);
  var max_y = (max_h - popup.offsetHeight);
  popup.style.left = (max_x / 2) + 'px';
  popup.style.top = (max_y / 4) + 'px';

  Drag.init(popup.header, popup, 0, max_x, 0, max_y);

  current_form.disable_controls();
  popup.active_form = current_form;
  popup.current_focus = popup.xml_area;

  popup.comment_area.value = comment;
  popup.comment_area.scrollTop = 0;
  popup.comment_area.selectionEnd = 0;

  popup.xml_area.value = xml_code;
  popup.xml_area.scrollTop = 0;
  popup.xml_area.selectionEnd = 0;

  popup.comment_area.focus();
  current_form = popup;

  popup.style.zIndex = root_zindex.length * 100

  };

function get_sxml_popup(sxml) {

  var popup = document.createElement('div');
  popup.style.position = 'absolute';
  popup.style.border = '2px solid grey';
  popup.style.background = 'white';

  var header = document.createElement('div');
  header.form = popup;
  header.style.background = '#C3D9FF';
  header.style.fontWeight = 'bold';
  header.style.paddingLeft = '5px';
  header.style.borderBottom = '1px solid grey';
  header.style.cursor = 'default';
  var popup_caption = document.createTextNode('Xml');
  header.appendChild(popup_caption);
  popup.header = header;
  popup.appendChild(header);

  var comment_div = document.createElement('div');
  popup.appendChild(comment_div);
  var comment_subhead = document.createElement('div');
  comment_subhead.style.marginTop = '10px';
  comment_subhead.appendChild(document.createTextNode('Comment:'));
  comment_div.appendChild(comment_subhead);
  var comment_area = document.createElement('textarea');
  comment_area.rows = 8;
  comment_area.cols = 80;
  comment_area.style.margin = '10px';
  comment_div.appendChild(comment_area);
  popup.comment_area = comment_area;

  comment_area.onkeydown = function(e) {
    if (!e) e=window.event;
    if (['Tab', 'Home', 'End', 'PageUp', 'PageDown', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown']
        .includes(e.key))
      return;  // always allow cursor keys
    var popup = this.parentNode.parentNode;
    if (popup.readonly) {
      e.cancelBubble = true;
      return false;
      };
    if (e.key === 'Escape') {
  	  if (this.value === popup.comment) {
        popup.close_window();
      } else {
        this.value = popup.comment;
        this.scrollTop = 0;
        this.selectionEnd = 0;
        };
  	  };
    };

  var xml_div = document.createElement('div');
  popup.appendChild(xml_div);
  var xml_subhead = document.createElement('div');
  xml_subhead.appendChild(document.createTextNode('Xml code:'));
  xml_div.appendChild(xml_subhead);
  var xml_area = document.createElement('textarea');
  xml_area.rows = 12;
  xml_area.cols = 80;
  xml_area.style.margin = '10px';
  xml_div.appendChild(xml_area);
  popup.xml_area = xml_area;

  xml_area.onkeydown = function(e) {
    if (!e) e=window.event;
    if (['Tab', 'Home', 'End', 'PageUp', 'PageDown', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown']
        .includes(e.key))
      return;  // always allow cursor keys
    var popup = this.parentNode.parentNode;
    if (popup.readonly) {
      e.cancelBubble = true;
      return false;
      };
    if (e.key === 'Escape') {
  	  if (this.value === popup.xml_code) {
        popup.close_window();
      } else {
        this.value = popup.xml_code;
        this.scrollTop = 0;
        this.selectionEnd = 0;
        };
	  };
    };

  var popup_button_row = document.createElement('div');
  popup_button_row.style.padding = '5px 0px 10px';  // top l/r bot
  popup_button_row.style.textAlign = 'right';
  popup.appendChild(popup_button_row);

  var btn_ok = document.createElement('button');
  btn_ok.style.textAlign = 'center';
  btn_ok.style.marginRight = '10px';
  btn_ok.style.width = '60px';
  btn_ok.style.color = 'navy';
  btn_ok.label = document.createTextNode('Ok')
  btn_ok.appendChild(btn_ok.label);
  popup.btn_ok = btn_ok;
  popup_button_row.appendChild(btn_ok);

  btn_ok.onclick = function() {popup.close_window()};

  popup.close_window = function() {
    popup.style.display = 'none';
    current_form = popup.active_form;
    current_form.enable_controls();
    popup.sxml.value = popup.comment_area.value + '\f' + popup.xml_area.value;  // use ASCII ff to join
    setTimeout(function() {current_form.current_focus.focus()}, 0);
    document.body.removeChild(popup);
    };

  return popup;
  };
