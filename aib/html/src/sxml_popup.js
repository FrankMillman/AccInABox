function sxml_popup(sxml) {

  popup.sxml = sxml;

  popup.readonly = !sxml.amendable();
  popup.caption.data = 'Xml';

  popup.text.value = sxml.value;

  if (popup.readonly)
    popup.text.style.background = '#CCFFCC';

  document.body.appendChild(popup);
  popup.style.display = 'block';
  var max_x = (max_w - popup.offsetWidth);
  var max_y = (max_h - popup.offsetHeight);
  popup.style.left = (max_x / 2) + 'px';
  popup.style.top = (max_y / 4) + 'px';

  Drag.init(popup.header, popup, 0, max_x, 0, max_y);

  current_form.disable_controls();
  popup.active_form = current_form;
  popup.current_focus = popup.text;
  popup.text.focus();
  current_form = popup;

  popup.style.zIndex = root_zindex.length * 100

  };

popup = document.createElement('div');
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
var popup_caption = document.createTextNode('');
popup.caption = popup_caption;
header.appendChild(popup_caption);
// to prevent selection of text - IE only
header.onselectstart = function(){return false};
popup.header = header;
popup.appendChild(header);

var popup_text = document.createElement('textarea');
popup_text.rows = 20;
popup_text.cols = 80;
popup_text.style.margin = '10px';
popup.appendChild(popup_text);
popup.text = popup_text;

popup_text.onkeydown = function(e) {
  if (!e) e=window.event;
  if (e.keyCode === 9)
    return;  // always allow 'tab'
  if (e.keyCode >= 33 && e.keyCode <= 40)
    return;  // always allow cursor keys
  var popup = this.parentNode;
  if (popup.readonly) {
    e.cancelBubble = true;
    return false;
    };
  if (e.keyCode === 27)
    this.value = popup.sxml.value;
  };

var popup_button_row = document.createElement('div');
popup_button_row.style.padding = '5px 0px 10px';  // top l/r bot
//popup_button_row.style.margin = '0px 15px';
popup_button_row.style.textAlign = 'right';
popup.appendChild(popup_button_row);

/*
var btn_lft = document.createElement('button');
btn_lft.style.textAlign = 'center';
btn_lft.style.marginRight = '10px';
btn_lft.style.width = '60px';
btn_lft.style.color = 'darkgrey';
btn_lft.label = document.createTextNode('Save')
btn_lft.appendChild(btn_lft.label);
popup.btn_lft = btn_lft;
popup_button_row.appendChild(btn_lft);

var btn_rgt = document.createElement('button');
btn_rgt.style.textAlign = 'center';
btn_rgt.style.marginRight = '10px';
btn_rgt.style.width = '60px';
btn_rgt.style.color = 'navy';
btn_rgt.label = document.createTextNode('Close')
btn_rgt.appendChild(btn_rgt.label);
popup.btn_rgt = btn_rgt;
popup_button_row.appendChild(btn_rgt);

btn_rgt.onclick = function() {popup.close_window()};
*/

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
  document.body.removeChild(popup);
  current_form = popup.active_form;
  current_form.enable_controls();
  // IE8 converts all \n to \r\n
  // this converts it back again!
  popup.sxml.value = popup.text.value.replace(/(\r\n|\n|\r)/gm, '\n');
  if (popup.sxml.callback !== undefined) {
    callback = popup.sxml.callback;
    var ctx = callback.shift();  // shift removes first element
    var func = callback.shift();  // callback now contains arguments
    func.apply(ctx, callback);
    };
  ////setTimeout(popup.sxml.focus(), 0);
  //setTimeout(function() {popup.sxml.focus()}, 0);
  setTimeout(function() {current_form.current_focus.focus()}, 0);
  };

popup.style.display = 'none';  // do not show window

popup.disable_controls = function() {debug3('ERROR - popup has no disable_controls()')};
