function create_page() {
  var page = document.createElement('div');
  page.style.display = 'inline-block';
  page.style.padding = '0px 10px 10px 10px';
  page.block = null;
  page.sub_pages = [];

  page.kbd_shortcuts = {};
  page.kbd_shortcuts['normal'] = {};
  page.kbd_shortcuts['alt'] = {};
  page.kbd_shortcuts['ctrl'] = {};
  page.kbd_shortcuts['shift'] = {};

  page.onkeydown = function(e) {
//    if (this.frame.ctrl_grid === null)
//      return;
    if (!e) e=window.event;

    if (e.altKey)
      var target = this.kbd_shortcuts['alt'][e.keyCode];
    else if (e.ctrlKey)
      var target = this.kbd_shortcuts['ctrl'][e.keyCode];
    else if (e.shiftKey)
      var target = this.kbd_shortcuts['shift'][e.keyCode];
    else
      var target = this.kbd_shortcuts['normal'][e.keyCode];

    if (target !== undefined) {
      target.onclick.call(target);
      e.cancelBubble = true;
      return false;
      };

/*
    if (!e.ctrlKey)
      return;
    var ctrl_grid = this.frame.ctrl_grid;
    if (e.keyCode === 45 && ctrl_grid.insert_ok) {
      ctrl_grid.req_insert();
      return;
      };
    if (e.keyCode === 46 && ctrl_grid.delete_ok) {
      ctrl_grid.req_delete();
      return;
      };
    if (ctrl_grid.navigate_ok !== true)
      return;
    switch (e.keyCode) {
      case 35:  // end
        if (ctrl_grid.active_row !== (ctrl_grid.total_rows()-1)) {
          var args = [this.frame.ref, 'last'];
          send_request('navigate', args);
          };
        break;
      case 36:  // home
        if (ctrl_grid.active_row !== 0) {
          var args = [this.frame.ref, 'first'];
          send_request('navigate', args);
          };
        break;
      case 38:  // up
        if (ctrl_grid.active_row !== 0) {
          var args = [this.frame.ref, 'prev'];
          send_request('navigate', args);
          };
        break;
      case 40:  // down
        if (ctrl_grid.active_row !== (ctrl_grid.total_rows()-1)) {
          var args = [this.frame.ref, 'next'];
          send_request('navigate', args);
          };
        break;
      };
*/
// if next 2 lines are needed, add them to each 'case' above, remove from here
//      e.cancelBubble = true;
//      return false;
    };
  page.end_page = function() {
    if (this.block != null)
      this.block.end_block()
    for (var j=0; j<page.sub_pages.length; j++)
      page.sub_pages[j].end_page();
    };
  return page;
  };

function create_input(frame, json_elem, label) {
  switch (json_elem.type) {
    case 'text':
      if (json_elem.lkup) {
        var return_elem = setup_lkup(json_elem);
        var input = return_elem.firstChild;
        }
      else if (json_elem.height !== null) {
        var return_elem = setup_textarea(json_elem);
        var input = return_elem;
        }
      else {
        var return_elem = setup_text(json_elem);
        var input = return_elem;
        };
      break;
    case 'num':
      var return_elem = setup_num(json_elem);
      var input = return_elem;
      break;
    case 'date':
      var return_elem = setup_date(json_elem);
      var input = return_elem.firstChild;
      break;
    case 'bool':
      var return_elem = setup_bool(label, json_elem);
      var input = return_elem;
      break;
    case 'choice':
      var return_elem = setup_choice(json_elem);
      var input = return_elem.firstChild;
      break;
    case 'spin':
      var return_elem = setup_spin(json_elem);
      var input = return_elem.firstChild;
      break;
    case 'sxml':
      var return_elem = setup_sxml(json_elem);
      var input = return_elem;
      break;
    case 'dummy':
      var input = document.createElement('span');
      input.aib_obj = new AibDummy();
      input.tabIndex = 0;
      var return_elem = input;
      break;
    };

//  if (json_elem.lng !== null)
//    input.style.width = json_elem.lng + 'px';
//  input.style.font = '10pt Verdana,sans-serif';
//  input.style.color = 'navy';
  input.style.outline = '0px solid transparent';  // disable highlight on focus

  input.pos = frame.obj_list.length;
  frame.obj_list.push(input);
  frame.form.obj_dict[json_elem.ref] = input;

  input.frame = frame;
  input.active_frame = frame;
  input.ref = json_elem.ref;
  input.help_msg = json_elem.help_msg;
  input.title = input.help_msg;
  if (label !== null)
    label.title = input.help_msg;
//  input.readonly = false;
  input.readonly = json_elem.readonly;  // set in form defn
  input.allow_amend = json_elem.allow_amend;  // set in col defn
  input.amend_ok = json_elem.amend_ok;  // db permissions

  // input.form_value is value received from server
  // input.current_value is value entered by user, awaiting validation
  // input.value is value currently being entered by user [DOM element]
  // data_changed - there are 3 scenarios
  // 1 - press Esc while typing
  //   reset value from current_value
  // 2 - tab off field, fails validation, field gets focus again
  //   Esc - reset value and current_value from form_value
  // 3 - on lost focus, detect whether to send value to server
  //   if yes, get value from input.current_value
  // data_changed compares value with form_value
  // on lost focus, set current_value to value
  // in after_lost_focus, reset value to display format (date/num)

  input.get_val = function() {
    return this.firstChild.value;
    };

  input.get_caret = function() {
    return getCaret(this.firstChild);
    };

  input.onkeydown = function(e) {
    if (input.frame.form.disable_count) return false;
    if (!e) e=window.event;
    if (e.ctrlKey && (e.keyCode === 70) && (input.lkup !== undefined)) {  // Ctrl+F
      input.lkup();
      e.cancelBubble = true;
      e.keyCode = 0;
      return false;
      };
    switch(e.keyCode) {
      case 27:  // Esc
        if (input.aib_obj.data_changed(input)) {  //, input.childNodes[0].value)) {
          if (input.key_strokes) {
            input.firstChild.value = input.current_value;
            input.key_strokes = 0;
            }
          else
            // timeout needed for Opera, Firefox
            setTimeout(function() {input.aib_obj.reset_value(input)}, 0);
          e.cancelBubble = true;
          return false;
          };
        // else allow escape to bubble up to form, which sends 'req_cancel'
        break;
      case 32:  // space
        if (!input.key_strokes && input.expander !== undefined) {
          input.expander();
          e.cancelBubble = true;
          return false;
          };
        break;
      case 13:  // enter
        if (e.shiftKey && input.lookdown !== undefined) {
          input.lookdown();
          e.cancelBubble = true;
          return false;
          };
        break;
      };
    return input.aib_obj.ondownkey(input, e);
    };

  input.onkeypress = function(e) {
    if (!e) e=window.event;
    if (!e.which) e.which=e.keyCode;
    if (e.which === 92 && !input.key_strokes) {  // backslash
      var args = [input.ref];
      send_request('get_prev', args);
      return false;
      };
    input.key_strokes += 1;
    return input.aib_obj.onpresskey(input, e);
    };

  if (input.onfocus === null)  // already set on bool, sxml
    input.onfocus = function() {got_focus(input)};
  //input.onfocus = function() {input.aib_obj.onfocus(input)};
  input.got_focus = function() {
    input.aib_obj.got_focus(input);
    if (input.frame.amended() && !input.frame.form.focus_from_server) {
      var args = [input.ref];
      send_request('got_focus', args);
      };
    input.key_strokes = 0;
    input.aib_obj.after_got_focus(input);
    if (input.multi_line === true)
      ignore_enter = true;
    };

  input.lost_focus = function() {
    //debug3(input.help_msg + ' lost focus');
    if (!input.aib_obj.before_lost_focus(input))  // failed validation (date)
      return false;
//    if (input.aib_obj.data_changed(input, input.current_value) && !input.frame.form.internal)
    if ((input.current_value !== input.form_value) && !input.frame.form.internal)
      input.frame.set_amended(true);
    if (input.frame.amended() && !input.frame.form.focus_from_server) {
      var value = input.aib_obj.get_value_for_server(input);
        var args = [input.ref, value];
        send_request('lost_focus', args);
      };
    input.aib_obj.after_lost_focus(input);
    if (input.multi_line === true)
      ignore_enter = false;
    return true;
    };

  if (input.onclick === null) {  // else we over-write bool.onclick
    input.onclick = function() {  // IE8 does not set focus!
      input.focus();  // not sure if this is necessary - leave for now
      };
    };

  input.set_dflt_val = function(value) {
//    this.current_value = value;
//    if (this.frame.form.current_focus === this)
//      this.aib_obj.after_got_focus(this);
//    else
//      this.aib_obj.after_lost_focus(this);
    if (this.amendable())
      this.aib_obj.set_dflt_val(this, value);
    else {
      this.current_value = value;
      if (this.frame.form.current_focus === this)
        this.aib_obj.after_got_focus(this);
      else
        this.aib_obj.after_lost_focus(this);
      };
    };

  input.amendable = function() {
    if (this.readonly) return false;
    if (!this.amend_ok) return false;
    if (!this.allow_amend && this.frame.obj_exists) return false;
    return true;
    };

  input.set_readonly = function(state) {
    this.readonly = state;
    if (input.frame.form.current_focus === input) {
      //debug3(input.ref + ': must set readonly');
      input.aib_obj.after_lost_focus(input);
      input.aib_obj.got_focus(input);
      };
//    this.aib_obj.set_readonly(this, state);
    };

  input.set_value_from_server = function(value) {
    this.aib_obj.set_value_from_server(this, value);
// not sure about this
//    input.frame.set_amended(true);
    };

  input.reset_value = function() {
    this.aib_obj.reset_value(this);
    };

  if (json_elem.readonly) {  // not used at present
    input.set_readonly(true);
    };

  input.set_value_from_server(json_elem.value);

  return return_elem;
  };

function setup_inp(json_elem) {
  var inp = document.createElement('input');
  inp.style.height = '17px';
  inp.style.width = json_elem.lng + 'px';
  inp.style.padding = '1px';
  inp.style.border = '1px solid black';
  inp.className = 'focus_background';
  inp.style.font = '10pt Verdana,sans-serif';
  inp.style.color = 'navy';
  inp.style.outline = '0px solid transparent';  // disable highlight on focus
  inp.style.display = 'none';
  return inp;
  };

function setup_dsp(json_elem) {
  var dsp = document.createElement('div');
  dsp.style.height = '17px';
  dsp.style.width = json_elem.lng + 'px';
  dsp.style.padding = '1px';
  dsp.style.border = '1px solid darkgrey';
  dsp.style.overflow = 'hidden';
  dsp.style.textOverflow = 'ellipsis';
  dsp.style.whiteSpace = 'nowrap';

  var txt = document.createElement('span');
  dsp.appendChild(txt);
  txt.style.whiteSpace = 'pre';
  txt.style.display = 'inline-block';
  txt.style.height = '17px';
  txt.style.background = '#f5f5f5';  // very light grey
  var text_node = document.createTextNode('');
  txt.appendChild(text_node);
  dsp.txt = txt;
  dsp.text = text_node;

  dsp.onclick = function() {
    if (dsp.parentNode.amendable())
      dsp.parentNode.focus();
    };

  return dsp;
  };

function setup_text(json_elem) {
  var text = document.createElement('div');
  text.style[cssFloat] = 'left';
//  text.style.height = '20px';
  text.tabIndex = 0;

  text.aib_obj = new AibText();

  var inp = setup_inp(json_elem);
  if (json_elem.maxlen)  // 0 means unlimited
    inp.maxLength = json_elem.maxlen;
  text.password = json_elem.password;
  if (text.password !== '')
    inp.type = 'password';

  var dsp = setup_dsp(json_elem);

  text.appendChild(inp);
  text.appendChild(dsp);

  return text;
  };

function setup_num(json_elem) {
  var num = document.createElement('div');
  num.style[cssFloat] = 'left';
//  num.style.height = '20px';
  num.tabIndex = 0;

  num.aib_obj = new AibNum();

  num.reverse = json_elem.reverse;
  num.integer = json_elem.integer;
  num.max_decimals = json_elem.max_decimals;
  num.neg_display = json_elem.neg_display;

  var inp = setup_inp(json_elem);
  inp.style.textAlign = 'right';
  var dsp = setup_dsp(json_elem);
  dsp.style.textAlign = 'right';

  num.appendChild(inp);
  num.appendChild(dsp);

  return num;
  };

//function setup_lkup(text, json_elem) {
function setup_lkup(json_elem) {
  var text = document.createElement('div');
  text.style[cssFloat] = 'left';
//  text.style.height = '20px';
  text.tabIndex = 0;
  text.password = json_elem.password;

  text.aib_obj = new AibText();

  var inp = setup_inp(json_elem);
  var dsp = setup_dsp(json_elem);

  text.appendChild(inp);
  text.appendChild(dsp);

  text.lkup = function() {  // press Ctrl+F or click ButtonTop
    // IE8 bug - if value is "", it returns "null" - this is a workaround
    var lkup_val = (text.firstChild.value === '') ? '' : text.firstChild.value;
    var args = [text.ref, lkup_val];
    send_request('req_lookup', args);
    };
  text.expander = function() {  // press Space
    // IE8 bug - if value is "", it returns "null" - this is a workaround
    var lkup_val = text.firstChild.value === "" ? "" : text.firstChild.value;
    var args = [text.ref, lkup_val];
    send_request('req_lookup', args);
    };
  text.lookdown = function() {  // press Shift+Enter or click ButtonBottom
    var args = [text.ref];
    send_request('req_lookdown', args);
    };

  var container = document.createElement('div');
  container.style[cssFloat] = 'left';
  container.appendChild(text);

  // create 2-part button - top: req_lookup  bottom: req_lookdown
  var btn = document.createElement('span');
  container.appendChild(btn);
  btn.style.display = 'inline-block';
  btn.style.backgroundImage = 'url(' + iLkup_src + ')';
  btn.style.width = '16px';
  btn.style.height = '16px';
  btn.style.marginTop = '2px';
  btn.style.marginBottom = '1px';
  btn.style.marginLeft = '1px';
  btn.style.marginRight = '2px';
  btn.style.verticalAlign = 'bottom';
  btn.onmouseover = function() {
    btn.style.cursor = 'pointer';
    };
  btn.onmouseleave = function() {
    btn.style.cursor = 'default';
    };

  var lkup = document.createElement('div');
  btn.appendChild(lkup);
  lkup.style.width = '15px';
  lkup.style.height = '7px';
  lkup.style.background = 'transparent';
  lkup.title = 'Call lookup (Ctrl+F)';
  lkup.onclick = function() {
    if (text.frame.form.disable_count) return;
    if (!text.amendable()) {
      text.focus();
      return;
      };
    if (text.frame.form.current_focus !== text) {
      callbacks.push([lkup, lkup.afterclick]);
      text.focus();  // set focus on text first
      }
    else
      lkup.afterclick();
    };
  lkup.afterclick = function() {
    if ((text.frame.form.current_focus !== text)
        || (text.frame.form.setting_focus !== text))  // focus reset by server
      return;
    text.lkup();
    };

  var blank = document.createElement('div');
  btn.appendChild(blank);
  blank.style.width = '15px';
  blank.style.height = '1px';
  blank.style.background = 'transparent';

  var lkdn = document.createElement('div');
  btn.appendChild(lkdn);
  lkdn.style.width = '15px';
  lkdn.style.height = '7px';
  lkdn.style.background = 'transparent';
  lkdn.title = 'Call lookdown (Shift+Enter)';
  lkdn.onclick = function() {
    if (text.frame.form.disable_count) return;
    if (!text.amendable()) {
      text.focus();
      return;
      };
    if (text.frame.form.current_focus !== text) {
      text.focus();  // set focus on text first
      setTimeout(function() {lkdn.afterclick()}, 0);
      }
    else
      lkdn.afterclick();
    };
  lkdn.afterclick = function() {
    if ((text.frame.form.current_focus !== text)
        || (text.frame.form.setting_focus !== text))  // focus reset by server
      return;
    text.lookdown();
    };

  return container;
    };

function setup_textarea(json_elem) {
  var text = document.createElement('div');
  text.style.width = (+json_elem.lng + 4) + 'px';
  text.style.height = ((json_elem.height * 17) + 4) + 'px';
  text.tabIndex = 0;
  text.password = '';
  text.multi_line = true;
  text.aib_obj = new AibText();

  var inp = document.createElement('textarea');
  text.appendChild(inp);
  inp.cols = 1;  // required, but over-ridden by json_elem.lng
  inp.rows = json_elem.height;
  inp.style.width = json_elem.lng + 'px';
  inp.style.height = (json_elem.height * 17) + 'px';
  inp.style.border = '1px solid black';
  inp.className = 'focus_background';
  inp.style.font = '10pt Verdana,sans-serif';
  inp.style.color = 'navy';
  inp.style.outline = '0px solid transparent';  // disable highlight on focus
  inp.style.whiteSpace = 'pre-wrap';
  inp.style.display = 'none';

  var dsp = document.createElement('div');
  text.appendChild(dsp);
  dsp.style.width = (+json_elem.lng + 4) + 'px';
  dsp.style.height = ((json_elem.height * 17) + 4) + 'px';
  dsp.style.border = '1px solid darkgrey';
  dsp.style.overflow = 'hidden';
  dsp.style.whiteSpace = 'pre-wrap';
  dsp.style.wordWrap = 'break-word';

  dsp.onclick = function() {
    if (dsp.parentNode.amendable())
      dsp.parentNode.focus();
    };

  var text_node = document.createTextNode('');
  dsp.appendChild(text_node);
  dsp.text = text_node;

  return text;
  };

function setup_date(json_elem) {
  var date = document.createElement('div');
  date.style[cssFloat] = 'left';
//  date.style.height = '20px';
  date.tabIndex = 0;

  date.aib_obj = new AibDate();

  var inp = setup_inp(json_elem);
  var dsp = setup_dsp(json_elem);

  date.appendChild(inp);
  date.appendChild(dsp);

  date.valid = true;
  date.selected = false;
  date.blank = '';
  date.yr_pos = [];
  date.mth_pos = [];
  date.day_pos = [];
  date.literal_pos = [];
  date.input_format = json_elem.input_format;
  date.display_format = json_elem.display_format;
  for (var i=0, l=date.input_format.length; i<l; i++) {
    if (date.input_format[i] === '%') {
      var chr = date.input_format[i+1];
      if (chr === 'd') {
        date.day_pos.push(i);
        date.day_pos.push(2);
        date.blank += '  ';
        i += 1;
        }
      else if (chr === 'm') {
        date.mth_pos.push(i);
        date.mth_pos.push(2);
        date.blank += '  ';
        i += 1;
        }
      else if (chr === 'y') {
        date.yr_pos.push(i);
        date.yr_pos.push(2);
        date.blank += '  ';
        i += 1;
        }
      else if (chr === 'Y') {
        date.yr_pos.push(i);
        date.yr_pos.push(4);
        date.blank += '    ';
        i += 1;
        }
      }
    else {
      date.blank += date.input_format[i];
      date.literal_pos.push(i);
      }
    };

  var container = document.createElement('div');
//  container.style[cssFloat] = 'left';
  container.appendChild(date);

//  var cal = document.createElement('span');
  var cal = document.createElement('div');
  container.appendChild(cal);
//  cal.style.display = 'inline-block';
  cal.style[cssFloat] = 'left';
  cal.style.backgroundImage = 'url(' + iCal_src + ')';
  cal.style.width = '16px';
  cal.style.height = '16px';
  cal.style.marginTop = '3px';
  cal.style.marginBottom = '2px';
  cal.style.marginLeft = '1px';
  cal.style.marginRight = '0px';
  cal.style.verticalAlign = 'bottom';
  cal.style.cursor = 'default';
  cal.title = 'Calendar (Space)';

  cal.onclick = function() {
    if (date.frame.form.disable_count) return;
    if (!date.amendable()) {
      date.focus();
      return;
      };
    if (date.frame.form.current_focus !== date) {
      callbacks.push([cal, cal.after_click]);
      date.focus();  // set focus on date first
      }
    else
      cal.after_click();
    };
  cal.after_click = function() {
    if ((date.frame.form.current_focus !== date)
        || (date.frame.form.setting_focus !== date))  // focus reset by server
      return;
    date.aib_obj.show_cal(date);
    };

  date.expander = function() {
    date.aib_obj.show_cal(date);
    };

  return container;
  };

function setup_bool(label, json_elem) {

  var bool = document.createElement('div');
  bool.style[cssFloat] = 'left';

  if (window.SVGSVGElement !== undefined) {
    var NS='http://www.w3.org/2000/svg';
    var svg=document.createElementNS(NS,'svg');
    bool.appendChild(svg);
    };

  bool.aib_obj = new AibBool();
  bool.tabIndex = 0;
  bool.style.width = '16px';
  bool.style.height = '16px';
  bool.style.border = '1px solid darkgrey';
  bool.style.outline = '0px solid transparent';  // disable highlight on focus

  bool.onmousedown = function() {bool.mouse_down = true};
  bool.onmouseup = function() {bool.mouse_down = false};

  bool.onfocus = function() {
    bool.has_focus = true;  // gets reset in aib_obj.after_lost_focus()
    if (bool.mouse_down)
      return;  // will set focus from onclick()
    got_focus(bool);
    };

  bool.onclick = function() {
    if (bool.frame.form.disable_count) return false;
    if (!bool.amendable()) return false;
    bool.frame.set_amended(true);  // to force sending got_focus
    if (bool.frame.form.current_focus !== bool) {
      callbacks.push([bool, bool.after_click]);
      if (bool.has_focus)  // can't call focus() - it will be ignored!
        got_focus(bool);  // call lost_focus(), got_focus()
      else
        bool.focus();
      }
    else
      bool.after_click();
    };
  bool.after_click = function() {
    if ((bool.frame.form.current_focus !== bool)
        || (bool.frame.form.setting_focus !== bool))  // focus reset by server
      return;
    bool.aib_obj.chkbox_change(bool);
    };

  if (label !== null)
    label.onclick = function() {bool.onclick()};

  bool.onkeydown = function(e) {
    if (bool.frame.form.disable_count) return false;
    if (!e) e=window.event;
    if (e.keyCode === 27) {
      if (bool.aib_obj.data_changed(bool, bool.current_value))
        setTimeout(function() {bool.aib_obj.reset_value(bool)}, 0);
      e.cancelBubble = true;
      return false;
      };
    };

  bool.has_focus = false;
  bool.mouse_down = false;

  return bool;
  };

function setup_choice(json_elem) {

  var choice = document.createElement('div');
  choice.style[cssFloat] = 'left';
//  choice.style.height = '20px';
  choice.tabIndex = 0;

  choice.aib_obj = new AibChoice();

  var inp = document.createElement('div');
  inp.style[cssFloat] = 'left';
  inp.style.height = '17px';
  inp.style.width = json_elem.lng + 'px';
  inp.style.padding = '1px';
  inp.style.border = '1px solid black';
  inp.className = 'focus_background';
  inp.style.font = '10pt Verdana,sans-serif';
  inp.style.color = 'navy';
  inp.style.outline = '0px solid transparent';  // disable highlight on focus
  inp.style.display = 'none';

  var dsp = setup_dsp(json_elem);
  choice.appendChild(inp);
  choice.appendChild(dsp);

  choice.data = [];
  choice.values = [];
  var subtype_name = json_elem.choices[0], choices = json_elem.choices[1];
  for (var j=0; j<choices.length; j++) {
    choice.data.push(choices[j][0]);
    choice.values.push(choices[j][1]);
    };

  if (json_elem.callback !== undefined)
    choice.callback = json_elem.callback;
  else if (subtype_name !== null) {
    choice.subtype_name = subtype_name;
    choice.callback = function(subtype_id) {
      var subtype = choice.frame.subtypes[choice.subtype_name];
      if (subtype === undefined) return;
      if (subtype._active_box !== subtype_id) {
        subtype[subtype._active_box].style.display = 'none';
        subtype[subtype_id].style.display = 'block';
        subtype._active_box = subtype_id;
        };
      };
    }
  else
    choice.callback = function(option_selected) {};
  choice.dropdown = null;

  var container = document.createElement('div');
  container.style[cssFloat] = 'left';
  container.appendChild(choice);
  container.choice = choice;

//  var down = document.createElement('span');
  var down = document.createElement('div');
  container.appendChild(down);
//  down.style.display = 'inline-block';
  down.style[cssFloat] = 'left';
  down.style.backgroundImage = 'url(' + iDown_src + ')';
  down.style.width = '16px';
  down.style.height = '16px';
  down.style.marginTop = '2px';
  down.style.marginBottom = '1px';
  down.style.marginLeft = '1px';
  down.style.marginRight = '2px';
  down.style.verticalAlign = 'bottom';
  down.title = 'Choices (Up/Down/Space)';
  down.onmouseover = function() {down.style.cursor = 'pointer'};
  down.onmouseleave = function() {down.style.cursor = 'default'};
  down.onfocus = function() {choice.focus()};
  down.onclick = function() {
    if (choice.frame.form.disable_count) return;
    if (!choice.amendable()) {
      choice.focus();
      return;
      };
    if (choice.frame.form.current_focus !== choice) {
      choice.focus();  // set focus on choice first
      if ((choice.frame.form.current_focus !== choice)
          || (choice.frame.form.setting_focus !== choice))  // focus reset by server
        return;
      };
    if (choice.dropdown !== null)
      choice.aib_obj.onselection(choice, null)
    else {
      choice.on_selection = choice.aib_obj.after_selection;
      setTimeout(function() {choice.aib_obj.create_dropdown(choice)}, 0);
      };
    };

  return container;
  };

function setup_spin(json_elem) {
  var spin = document.createElement('div');
  spin.style[cssFloat] = 'left';
//  spin.style.height = '20px';
  spin.style.border = '1px solid lightgrey';
  spin.tabIndex = 0;

  spin.aib_obj = new AibSpin();

  var inp = document.createElement('div');
  inp.style[cssFloat] = 'left';
  inp.style.height = '17px';
  inp.style.width = json_elem.lng + 'px';
  inp.style.padding = '1px';
  inp.style.border = '1px solid black';
  inp.className = 'focus_background';
  inp.style.font = '10pt Verdana,sans-serif';
  inp.style.color = 'navy';
  inp.style.outline = '0px solid transparent';  // disable highlight on focus
  inp.style.display = 'none';

  var dsp = setup_dsp(json_elem);
  spin.appendChild(inp);
  spin.appendChild(dsp);

  spin.min = json_elem.min;
  spin.max = json_elem.max;
  spin.callback = json_elem.callback;
  if (spin.current_value !== null)
    dsp.text.data = spin.current_value;

  var container = document.createElement('div');
  container.style[cssFloat] = 'left';
  container.appendChild(spin);
  container.spin = spin;

  var btn = document.createElement('span');
  container.appendChild(btn);
  btn.style.display = 'inline-block';
  btn.style.backgroundImage = 'url(' + iSpin_src + ')';
  btn.style.width = '16px';
  btn.style.height = '16px';
  btn.style.marginTop = '2px';
  btn.style.marginBottom = '1px';
  btn.style.marginLeft = '1px';
  btn.style.marginRight = '2px';
  btn.style.verticalAlign = 'bottom';
  btn.onmouseover = function() {
    btn.style.cursor = 'pointer';
    };
  btn.onmouseleave = function() {
    btn.style.cursor = 'default';
    };
  var up = document.createElement('div');
  btn.appendChild(up);
  up.style.width = '15px';
  up.style.height = '7px';
  up.style.background = 'transparent';
  up.onmousedown = function() {
    up.incr = null;
    up.up = false;
    if (spin.frame.form.disable_count) return;
    if (!spin.amendable()) {

      debug3('not: ro=' + spin.readonly + ' ok=' + spin.amend_ok
        + ' allow=' + spin.allow_amend + ' exists=' + spin.frame.obj_exists);
    //if (this.readonly) return false;
    //if (!this.amend_ok) return false;
    //if (!this.allow_amend && this.frame.obj_exists) return false;

      spin.focus();
      return;
      };
    if (spin.frame.form.current_focus !== spin) {
      spin.focus();  // set focus on spin first
      setTimeout(function() {up.aftermousedown()}, 0);
      }
    else
      up.aftermousedown();
    };
  up.aftermousedown = function() {
    if ((spin.frame.form.current_focus !== spin)
        || (spin.frame.form.setting_focus !== spin))  // focus reset by server
      return;
    spin.aib_obj.change(spin, 1);
    if (!up.up)
      up.incr = setInterval(function() {spin.aib_obj.change(1)}, 200);
    };
  up.onmouseup = function() {
    up.up = true;
    if (up.incr !== null)
      clearInterval(up.incr);
    };
  var blank = document.createElement('div');
  btn.appendChild(blank);
  blank.style.width = '15px';
  blank.style.height = '1px';
  blank.style.background = 'transparent';
  var dn = document.createElement('div');
  btn.appendChild(dn);
  dn.style.width = '15px';
  dn.style.height = '7px';
  dn.style.background = 'transparent';
  dn.onmousedown = function() {
    dn.decr = null;
    dn.up = false;
    if (spin.frame.form.disable_count) return;
    if (!spin.amendable()) {
      spin.focus();
      return;
      };
    if (spin.frame.form.current_focus !== spin) {
      spin.focus();  // set focus on spin first
      setTimeout(function() {dn.aftermousedown()}, 0);
      }
    else
      dn.aftermousedown();
    };
  dn.aftermousedown = function() {
    if ((spin.frame.form.current_focus !== spin)
        || (spin.frame.form.setting_focus !== spin))  // focus reset by server
      return;
    spin.aib_obj.change(spin, -1);
    if (!dn.up)
      dn.decr = setInterval(function() {spin.aib_obj.change(-1)}, 200);
    };
  dn.onmouseup = function() {
    dn.up = true;
    if (dn.decr !== null)
      clearInterval(dn.decr);
    };

  return container;
  };

function setup_sxml(json_elem) {

//  var sxml = document.createElement('div');
//  sxml.style[cssFloat] = 'left';

  var sxml = document.createElement('button');
//  if (json_elem.lng)
//    sxml.style.width = json_elem.lng + 'px';
//  else
//    sxml.style.width = '60px';
  sxml.style.width = '60px';
  sxml.appendChild(document.createTextNode('<xml>'));

  sxml.style.background = button_background(sxml);
  sxml.style.border = '1px solid darkgrey';
  sxml.style.color = 'navy';
  sxml.style.outline = '0px solid transparent';
  sxml.style.height = '22px';
  sxml.style.borderRadius = '4px';

  sxml.pos = frame.obj_list.length;
  frame.obj_list.push(sxml);
  frame.form.obj_dict[json_elem.ref] = sxml;
  sxml.frame = frame;
  sxml.active_frame = frame;
  sxml.ref = json_elem.ref;
  sxml.help_msg = json_elem.help_msg;
  sxml.title = sxml.help_msg;

  sxml.aib_obj = new AibSxml();

  sxml.onmousedown = function() {sxml.mouse_down = true};
  sxml.onmouseup = function() {sxml.mouse_down = false};

  sxml.onfocus = function() {
    sxml.has_focus = true;
    if (sxml.mouse_down)
      return;  // will set focus from onclick()
    got_focus(sxml);
    };

  sxml.onclick = function() {
    if (sxml.frame.form.current_focus !== sxml) {
      callbacks.push([sxml, sxml.after_click]);
      if (sxml.has_focus)  // can't call focus() - it will be ignored!
        got_focus(sxml);  // call lost_focus(), got_focus()
      else
        sxml.focus();
      }
    else
      sxml.after_click();
    };
  sxml.after_click = function() {
    if ((sxml.frame.form.current_focus !== sxml)
        || (sxml.frame.form.setting_focus !== sxml))  // focus reset by server
      return;
    sxml.aib_obj.popup(sxml);
    };

  sxml.onkeydown = function(e) {
    if (sxml.frame.form.disable_count) return false;
    if (!e) e=window.event;
    alert(e.keyCode);
    if (e.keyCode === 27) {
      if (sxml.aib_obj.data_changed(sxml, sxml.current_value))
        setTimeout(function() {sxml.aib_obj.reset_value(sxml)}, 0);
      e.cancelBubble = true;
      return false;
      };
    };

  sxml.has_focus = false;
  sxml.mouse_down = false;

  return sxml;
  };

function create_display(frame, json_elem, label) {
  var display = document.createElement('div');
  display.style[cssFloat] = 'left';

//  display.style.paddingLeft = '1px';
//  display.style.border = '1px solid darkgrey';
//  display.style.overflow = 'hidden';
//  display.style.height = '20px';

  display.choices = (json_elem.choices !== null);  // true/false
  if (display.choices) {
    display.choice_data = [];
    display.choice_values = [];
    var choices = json_elem.choices;
    for (var j=0; j<choices.length; j++) {
      display.choice_data.push(choices[j][0]);
      display.choice_values.push(choices[j][1]);
      };
    };

  var text = document.createTextNode('');
  display.appendChild(text);
  //display.style.marginRight = '10px';
  display.style.width = json_elem.lng + 'px';
  display.display = true;  // used in start_form() to prevent setting focus here

  display.pos = frame.obj_list.length;
  frame.obj_list.push(display);
  frame.form.obj_dict[json_elem.ref] = display;
  display.frame = frame;
  display.active_frame = frame;
  display.ref = json_elem.ref;
  display.text = text;
  display.help_msg = json_elem.help_msg;
  display.title = display.help_msg;
  if (label !== null)
    label.title = display.help_msg;

  display.set_value_from_server = function(value) {
    if (display.choices)
      value = display.choice_values[display.choice_data.indexOf(value)];
    this.text.data = value;
    };

  display.set_value_from_server(json_elem.value);

  return display;
  };


function button_background(button) {
  if (button_background.bg_blur === undefined) {
    try {
      button.style.background = 'linear-gradient(white, gainsboro)';
      button_background.bg_blur = button.style.background;
      button_background.bg_focus = 'linear-gradient(lightcyan, paleturquoise)';
      //button_background.bg_disabled = 'linear-gradient(white, lightgrey)';
      button_background.bg_disabled = 'linear-gradient(#CCFFCC, #B4EEB4)';
      button_background.bg_error = 'mistyrose';
      }
    catch(err) {
      button_background.bg_blur = 'transparent';
      button_background.bg_focus = 'lightcyan';
      //button_background.bg_disabled = 'whitesmoke';
      button_background.bg_disabled = '#CCFFCC';
      button_background.bg_error = 'mistyrose';
      };
    };
  button.bg_blur = button_background.bg_blur;
  button.bg_focus = button_background.bg_focus;
  button.bg_disabled = button_background.bg_disabled;
  button.bg_error = button_background.bg_error;
  return button_background.bg_blur;
  };

function create_button(frame, json_elem) {
//  var container = document.createElement('span');
//  container.style.display = 'inline-block';
  var button = document.createElement('button');
//  container.appendChild(button);
  //button.style.marginRight = '10px';
  //button.style.textAlign = 'center';
  if (json_elem.lng)
    button.style.width = json_elem.lng + 'px';
  var label = document.createTextNode(json_elem.label);
  button.appendChild(label);
  button.label = label;

  button.style.background = button_background(button);
  button.style.border = '1px solid darkgrey';
  button.style.color = 'navy';
  button.style.outline = '0px solid transparent';
  button.style.height = '22px';
  button.style.borderRadius = '4px';

  button.pos = frame.obj_list.length;
  frame.obj_list.push(button);
  frame.form.obj_dict[json_elem.ref] = button;
  button.frame = frame;
  button.active_frame = frame;
  button.ref = json_elem.ref;
  button.help_msg = json_elem.help_msg;
  if (button.help_msg === '') button.help_msg = '\xa0';
  button.title = button.help_msg;
  button.mouse_down = false;
  button.has_focus = false;
  button.readonly = false;
  button.after_focus = null;

  button.onmousedown = function() {button.mouse_down = true};
  button.onmouseup = function() {button.mouse_down = false};

  button.onfocus = function() {
    //debug3(button.label.data + ' on focus');
    button.has_focus = true;
    if (button.mouse_down)
      return;  // will set focus from onclick()
    got_focus(button);
    };
  button.got_focus = function() {
    //debug3(button.label.data + ' got focus amd=' + button.frame.amended());
    if (button.readonly)
      button.style.background = button.bg_disabled;
    else
      button.style.background = button.bg_focus;
    if (button !== button.frame.default_button)
      button.style.border = '1px solid black';
    button.frame.active_button = button;
    if (button.frame.amended()) {
      var args = [button.ref];
      send_request('got_focus', args);
      };
    if (button.after_focus !== null) {
      button.after_focus();
      button.after_focus = null;
      };
    //debug3(button.label.data + ' [focus = ' + (button.form.current_focus) + ']');
    };

  button.lost_focus = function() {
    button.style.background = button.bg_blur;
    if (button !== button.frame.default_button)
      button.style.border = '1px solid darkgrey';
    button.has_focus = false;
    button.frame.active_button = button.frame.default_button;
    return true;
    };

  button.onkeydown = function(e) {
    if (button.frame.form.disable_count)
      return;
//    if (button.readonly) {
//      button.frame.form.current_focus.focus();
//      return;
//      };
    if (!e) e=window.event;
    if (e.ctrlKey) return;
    if (e.altKey) return;
    if ((e.keyCode === 37) || (e.keyCode === 38))  // left|up
      var dir = -1
    else if ((e.keyCode === 39) || (e.keyCode === 40))  // right|down
      var dir = 1
    else
      return;
    var pos = this.pos + dir;
    if (pos < 0)
      pos = button.frame.obj_list.length-1
    else if (pos === button.frame.obj_list.length)
      pos = 0;
    button.frame.obj_list[pos].focus();
    };

  button.onclick = function() {
    //debug3(button.label.data + ' on click ' + click_from_kbd);
    // FF sometimes generates click event when Enter pressed
    // this ensures that clicked() only gets called once
//    if (!click_from_kbd)  // if true, button.clicked is called directly
//      button.clicked();
//    };

//  button.clicked = function() {
    //debug3(button.label.data + ' [clicked : before focus] ' +
    //  (button.frame.form.current_focus === button) + ' ' +
    //  button.frame.form.disable_count + ' ' + button.has_focus);
    if (button.frame.form.disable_count) return;
    if (button.readonly) {
      button.frame.form.current_focus.focus();
      return;
      };
    if (button.frame.form.current_focus !== button) {
      button.after_focus = button.after_click;
      if (button.has_focus)  // can't call focus() - it will be ignored!
        got_focus(button);  // call lost_focus(), got_focus()
      else
        button.focus();
      }
    else
      button.after_click();
//    button.focus();  // in case it does not have focus - if it does, nothing will happen
//    if (button.frame.form.current_focus !== button) {
//      button.after_focus = button.after_click;
//      button.focus();
//      }
//    else
//      button.after_click();
    };

  button.after_click = function() {

//  why are next 4 lines necessary? [2014-01-21]
//  if we click a 'form' button, we should validate up to that point first (maybe?)
//  don't think it is necessary [2014-08-12]
//  on the server, if 'clicked' and button.must_validate, we validate up to that point
//  remove for now, see what happens

//    if (!button.frame.amended()) {
//      var args = [button.ref];
//      send_request('got_focus', args);
//      };

    var args = [button.ref];
    send_request('clicked', args);
    };

  button.set_value_from_server = function(value) {
    var attr = value[0];
    var val = value[1];
    switch (attr) {
      case 'enabled':
        button.set_readonly(!val);
        break;
      case 'label':
        button.label.data = val;
        break;
      case 'default':
        if (button.frame === button.frame.form.active_frame) {
          button.frame.default_button.style.border = '1px solid darkgrey';
          button.style.border = '1px solid blue';
          if (!button.frame.active_button.has_focus)
            if (button.frame.active_button === button.frame.default_button)
              button.frame.active_button = button;
          };
        button.frame.default_button = button;
        break;
      case 'show':
// don't know why this is here [2015-06-03]
// removed for now
//        var col = button.parentNode;
////        var col = button.parentNode.parentNode;
//        col.style.height = (col.offsetHeight - 2) + 'px';
        if (val)  // show button
          button.style.display = 'block';
        else {  // hide button
          button.style.display = 'none';
          if (button.has_focus) {
            var pos = button.pos + 1;
            while (button.frame.obj_list[pos].offsetHeight === 0)
              pos += 1;  // look for next available object
            button.frame.obj_list[pos].focus();
            };
          };
        break;
      };
    };

  button.set_readonly = function(state) {
    button.readonly = state;
    if (state) {
      button.style.color = 'darkgrey';  //'#b8b8b8';
      if (button.has_focus) {
        button.style.background = button.bg_disabled;
        var pos = button.pos + 1;
        while (button.frame.obj_list[pos].offsetHeight === 0)
          pos += 1;  // look for next available object
        button.frame.obj_list[pos].focus();
        };
      }
    else {
      button.style.color = 'navy';  //'black';  //'#101010';
      if (button.has_focus)
        button.style.background = button.bg_focus;
      };
    };

  if (json_elem.enabled === false)
    button.set_readonly(true);

  if (json_elem['default'] === true) {
    frame.default_button = button;
    frame.active_button = button;
    if (frame === frame.form.active_frame)
      button.style.border = '1px solid blue';
    };

  return button;
  };
