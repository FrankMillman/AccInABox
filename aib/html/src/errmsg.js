function show_errmsg(caption, message) {
  errmsg.caption.data = caption;
  errmsg.text.innerHTML = message;

  document.body.appendChild(errmsg);
  errmsg.style.display = 'block';
  if (errmsg.offsetWidth < 200)
    errmsg.style.width = '200px';
  var max_x = (max_w - errmsg.offsetWidth);
  var max_y = (max_h - errmsg.offsetHeight);
  errmsg.style.left = (max_x / 2) + 'px';
  errmsg.style.top = (max_y / 4) + 'px';

  Drag.init(errmsg.header, errmsg, 0, max_x, 0, max_y);

  current_form.disable_controls();
  errmsg.active_form = current_form;
  errmsg.current_focus = errmsg.button;
//  errmsg.button.focus();  // IE 11 does not like this!
  setTimeout(function() {errmsg.button.focus()}, 0);
  current_form = errmsg;

  errmsg.style.zIndex = root_zindex.length * 100

  //var sound = document.getElementById('beep');

  //var sound = {};  //new Object;
  //sound.type = 'audio/wav';
  //sound.data = 'c:\windows\media\chord.wav';

  //var sound = document.createElement("sound");
  //sound.src = 'c:\windows\media\chord.wav';
  //sound.hidden = true;
  //sound.setAttribute("autostart", false);
  //sound.setAttribute("width", 0);
  //sound.setAttribute("height", 0);
  //sound.setAttribute("enablejavascript", true);

  //sound.Play();
  };

errmsg = document.createElement('div');
errmsg.style.position = 'absolute';
errmsg.style.border = '2px solid red';
errmsg.style.background = 'white';

var header = document.createElement('div');
header.form = errmsg;
header.style.background = 'violet';
header.style.fontWeight = 'bold';
header.style.paddingLeft = '5px';
header.style.borderBottom = '1px solid red';
header.style.cursor = 'default';
var errmsg_caption = document.createTextNode('');
errmsg.caption = errmsg_caption;
header.appendChild(errmsg_caption);
// to prevent selection of text - IE only
header.onselectstart = function(){return false};
errmsg.header = header;
errmsg.appendChild(header);

var errmsg_text = document.createElement('div');
errmsg.text = errmsg_text;
//errmsg_text.style.fontSize = '80%';
errmsg_text.style.padding = '25px';
errmsg_text.style.textAlign = 'center';
errmsg.appendChild(errmsg_text);

var errmsg_button_row = document.createElement('div');
errmsg_button_row.style.padding = '5px 0px 10px';  // top l/r bot
//errmsg_button_row.style.margin = '0px 15px';
errmsg_button_row.style.textAlign = 'center';
errmsg.appendChild(errmsg_button_row);

var errmsg_button = document.createElement('button');
errmsg_button.style.textAlign = 'center';
errmsg_button.style.marginLeft = 'auto';
errmsg_button.style.marginRight = 'auto';
errmsg_button.style.width = '60px';
errmsg_button.appendChild(document.createTextNode('OK'));
errmsg.button = errmsg_button;
errmsg_button_row.appendChild(errmsg_button);
errmsg_button.onclick = function() {errmsg.close_window()};

errmsg.close_window = function() {
  errmsg.style.display = 'none';
  document.body.removeChild(errmsg);
  current_form = errmsg.active_form;
  current_form.enable_controls();
  setTimeout(function() {current_form.current_focus.focus()}, 0);
  };

errmsg.onkeydown = function(e) {
  if (click_from_kbd)  // Enter pressed while on a form, still active
    return false;  // wait for user to release Enter, else we close too soon
  if ((e.key === 'Enter') || (e.key === 'Escape') || (e.key === ' ')) {
    errmsg.close_window();
    e.cancelBubble = true;
    return false;
    };
  if (e.key === 'Tab') {
    e.cancelBubble = true;
    return false;
    };
  };

errmsg.onkeyup = function(e) {
  // FF workaround - if press space to trigger checkbox, and validation fails,
  //    errmsg is shown, keyup is caught here and generates a click event!
  // [2020-12-09] confirmed that this workaround is still necessary
  if (e.key === ' ')
      return false;
  };

errmsg.style.display = 'none';  // do not show window

errmsg.disable_controls = function() {debug3('ERROR - errmsg has no disable_controls()')};
