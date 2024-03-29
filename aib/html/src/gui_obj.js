function create_page() {
  //var page = document.createElement('div');
  var page = document.createElement('span');
  page.style.display = 'inline-block';
  page.style.padding = '0px 10px 10px 10px';
  page.block = null;
  page.nb_page = null;  // will be overridden if it is a notebook page
  page.nb_pages = [];

  page.kbd_shortcuts = {};
  page.kbd_shortcuts['normal'] = {};
  page.kbd_shortcuts['alt'] = {};
  page.kbd_shortcuts['ctrl'] = {};
  page.kbd_shortcuts['shift'] = {};

  page.onkeydown = function(e) {

    if (e.altKey)
      var target = this.kbd_shortcuts['alt'][e.code];
    else if (e.ctrlKey)
      var target = this.kbd_shortcuts['ctrl'][e.code];
    else if (e.shiftKey)
      var target = this.kbd_shortcuts['shift'][e.code];
    else
      var target = this.kbd_shortcuts['normal'][e.code];

    if (target !== undefined) {
      target.onclick.call(target);
      e.cancelBubble = true;
      return false;
      };

/*
    if (!e.ctrlKey)
      return;
    var ctrl_grid = this.frame.ctrl_grid;
    if (e.key === 'Insert' && ctrl_grid.insert_ok) {
      ctrl_grid.req_insert();
      return;
      };
    if (e.key === 'Delete' && ctrl_grid.delete_ok) {
      ctrl_grid.req_delete();
      return;
      };
    if (ctrl_grid.navigate_ok !== true)
      return;
    switch (e.key) {
      case 'End':
//        if (ctrl_grid.active_row !== (ctrl_grid.total_rows()-1)) {
        if (ctrl_grid.active_row !== (ctrl_grid.num_data_rows)) {
          var args = [this.frame.ref, 'last'];
          send_request('navigate', args);
          };
        break;
      case 'Home':
        if (ctrl_grid.active_row !== 0) {
          var args = [this.frame.ref, 'first'];
          send_request('navigate', args);
          };
        break;
      case 'ArrowUp':
        if (ctrl_grid.active_row !== 0) {
          var args = [this.frame.ref, 'prev'];
          send_request('navigate', args);
          };
        break;
      case 'ArrowDown':
//        if (ctrl_grid.active_row !== (ctrl_grid.total_rows()-1)) {
        if (ctrl_grid.active_row !== (ctrl_grid.num_data_rows)) {
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
    for (var j=0; j<page.nb_pages.length; j++)
      page.nb_pages[j].end_page();
    };

  return page;
  };

function create_input(frame, page, json_elem, label) {
  switch (json_elem.type) {

//    case 'textarea':
//      var input = document.createElement('textarea');
//      input.cols = 1;  // adjusted by json_elem.len - see below
//      input.rows = json_elem.height;
//      input.form_value = '';
//      input.current_value = '';
//      input.allow_enter = true;
//      var return_elem = setup_text(input, json_elem);
//      break;
    case 'text':
      if (json_elem.height !== null) {
        var input = document.createElement('textarea');
        var return_elem = setup_textarea(input, json_elem);
        }
      else {

        var input = document.createElement('input');
        input.type = 'text';

        input.style.height = '17px';
        input.style.width = json_elem.lng + 'px';
        input.style.padding = '1px';
//        input.style.border = '1px solid black';
//        input.style.font = '10pt Verdana,sans-serif';
//        input.style.color = 'navy';
//        input.style.outline = 'none';  // disable highlight on focus
        input.style[cssFloat] = 'left';

//        input.form_value = '';
//        input.current_value = '';
        if (json_elem.lkup)
          var return_elem = setup_lkup(input, json_elem);
        else
          var return_elem = setup_text(input, json_elem);
      };

      input.style.border = '1px solid black';
      input.style.font = '10pt Verdana,sans-serif';
      input.style.color = 'navy';
      input.style.outline = 'none';  // disable highlight on focus

      input.form_value = '';
      input.current_value = '';

      break;
    case 'num':
      var input = document.createElement('input');
      input.type = 'text';

      input.style.height = '17px';
      input.style.width = json_elem.lng + 'px';
      input.style.padding = '1px';
      input.style.border = '1px solid black';
      input.style.font = '10pt Verdana,sans-serif';
      input.style.color = 'navy';
      input.style.outline = 'none';  // disable highlight on focus
      input.style.textAlign = 'right';
      input.style[cssFloat] = 'left';

      input.form_value = '';
      input.current_value = '';
      var return_elem = setup_num(input, json_elem);
      break;
    case 'date':
      var input = document.createElement('input');
      input.type = 'text';

      input.style.height = '17px';
      input.style.width = json_elem.lng + 'px';
      input.style.padding = '1px';
      input.style.border = '1px solid black';
      input.style.font = '10pt Verdana,sans-serif';
      input.style.color = 'navy';
      input.style.outline = 'none';  // disable highlight on focus
      input.style[cssFloat] = 'left';

      input.form_value = null;
      input.current_value = null;
      var return_elem = setup_date(input, json_elem);
      break;

    case 'bool':
      var input = document.createElement('span');
      input.form_value = '0';
      input.current_value = '0';
      input.value = '0';
      var return_elem = setup_bool(input, label, json_elem);
      break;

    case 'choice':
      var input = document.createElement('div');
      input.style[cssFloat] = 'left';
      input.tabIndex = 0
      input.form_value = '';
      input.current_value = '';
      var return_elem = setup_choice(input, json_elem);
      input.value = input.data[0];
      break;

    case 'radio':
      var input = document.createElement('div');
      input.style[cssFloat] = 'left';
      input.tabIndex = 0;
      input.form_value = '';
      input.current_value = '';
      var return_elem = setup_radio(input, json_elem);
      input.value = input.data[0];
      break;

    case 'spin':
      var input = document.createElement('div');
      input.style[cssFloat] = 'left';
      var return_elem = setup_spin(input, json_elem);
      break;

    case 'sxml':
      var input = document.createElement('button');
      var return_elem = setup_sxml(input, json_elem);
      break;
    case 'dummy':
      var input = document.createElement('span');
      input.aib_obj = new AibDummy();
      input.tabIndex = 0;
      input.dummy = true;  // ok to set focus here
      var return_elem = input;
      break;
    };

  if (json_elem.lng !== null)
    input.style.width = json_elem.lng + 'px';
  // input.style.font = '10pt Verdana,sans-serif';
  // input.style.color = 'navy';
  // input.style.outline = 'none';  // disable highlight on focus

  if (json_elem.skip)
    input.tabIndex = -1;  // remove from tab order

  if (json_elem.clickable) {  // e.g. footer_row in grid
    input.style.textDecoration = 'underline';
    input.style.cursor = 'default';
    input.onclick = function(e) {
      if (input.frame.form.disable_count) return false;
      var args = [input.ref];
      send_request('clicked', args);
      setTimeout(input.frame.form.current_focus.focus(), 0);
      };
    };

  input.pos = frame.obj_list.length;
  frame.obj_list.push(input);
  frame.form.obj_dict[json_elem.ref] = input;

  input.label = label;
  input.frame = frame;
  input.nb_page = page.nb_page;
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
  input.has_focus = false;

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

//  input.get_val = function() {
//    return this.value;
//    };

//  input.get_caret = function() {
//    return getCaret(this.firstChild);
//    };

  input.onkeydown = function(e) {
    if (input.frame.form.disable_count) return false;
    if (input.frame.form.readonly && !(e.key === 'Tab' || e.ctrlKey)) return false;
    // if (!e) e=window.event;
    if (e.ctrlKey && (e.key === 'F' || e.key === 'f') && (input.lkup !== undefined)) {
      input.lkup();
      e.cancelBubble = true;
      return false;
      };

    // [TODO] On Ctrl+Enter, open edit box full screen width, load input.value, dump input.value on 'Ok'
    //if (e.ctrlKey && e.key === 'Enter') {
    //  if (this.aib_obj.type === 'text')
    //    debug3('HERE ' + this.aib_obj.type + ' ' + this.label.firstChild.data);
    //  e.cancelBubble = true;
    //  return false;
    //  };

    switch(e.key) {
      case 'Escape':
        if (input.aib_obj.data_changed(input)) {
          if (input.key_pressed) {
            input.value = input.current_value;
            input.key_pressed = false;
            }
          else
            // // timeout needed for Opera, Firefox
            // setTimeout(function() {input.aib_obj.reset_value(input)}, 0);
            input.aib_obj.reset_value(input);
          e.cancelBubble = true;
          return false;
          };
        // else allow escape to bubble up to form, which sends 'req_cancel'
        break;
      case ' ':
        if (!input.key_pressed && input.expander !== undefined && input.amendable()) {
          input.expander();
          e.cancelBubble = true;
          return false;
          };
        break;
      case '\\':  // Backslash
        if (!input.key_pressed) {
          var args = [input.ref];
          send_request('get_prev', args);
          return false;
          };
        break;
      case 'Enter':
        if (e.shiftKey && input.lookdown !== undefined) {
          input.lookdown();
          e.cancelBubble = true;
          return false;
          };
        break;
      };
      if (!e.altKey)  // could be start of Alt+Tab
        input.key_pressed = true;
      return input.aib_obj.ondownkey(input, e);
    };

  if (input.onfocus === null)  // already set on bool, sxml
    input.onfocus = function() {
      if (input.multi_line === true && !input.frame.err_flag)
        ignore_enter = true;
      got_focus(input)
      };
  //input.onfocus = function() {input.aib_obj.onfocus(input)};
  input.got_focus = function() {
    input.aib_obj.got_focus(input);
    if ((input.frame.amended() || !input.frame.obj_exists) &&
        !input.frame.form.focus_from_server && !input.frame.form.internal) {
      var args = [input.ref];
      send_request('got_focus', args);
      }
    else {
      if (callbacks.length)
        setTimeout(function() {exec_callbacks()}, 0);
      };
    input.has_focus = true;
    input.key_pressed = false;  // set to true after first key pressed
    input.aib_obj.after_got_focus(input);
    };

  input.lost_focus = function() {
    //debug3(input.ref + ' ' + input.help_msg + ' lost focus');
    if (!input.aib_obj.before_lost_focus(input))  // failed validation (date)
      return false;
//    if (input.aib_obj.data_changed(input, input.current_value) && !input.frame.form.internal)
    if ((input.current_value !== input.form_value) && !input.frame.form.internal)
      input.frame.set_amended(true);
    if ((input.frame.amended() || !input.frame.obj_exists) &&
        !input.frame.form.focus_from_server && !input.frame.form.internal) {
      var value = input.aib_obj.get_value_for_server(input);
      var args = [input.ref, value];
      send_request('lost_focus', args);
      };
    input.aib_obj.after_lost_focus(input);
    if (input.multi_line === true)
      ignore_enter = false;
    input.has_focus = false;
    return true;
    };

  input.set_dflt_val = function(value) {
    this.aib_obj.set_dflt_val(this, value);
    };

  input.amendable = function() {
    if (this.readonly) return false;
    // changed 2019-03-16 - ar_inv_view.line_type needs dflt_val - ok?
    // if (this.readonly && this.frame.obj_exists) return false;
    // NOT OK 2019-09-21 - see login.form after password accepted
    if (!this.amend_ok) return false;
    if (!this.allow_amend && this.frame.obj_exists) return false;
    return true;
    };

  input.set_readonly = function(state) {
    // debug3(input.ref + ' readonly');
    if (input.frame.form.readonly)
      return;
    this.readonly = state;
    if (this.label)
      if (state)
        this.label.style.color = 'grey'
      else
        this.label.style.color = '';
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

function setup_text(text, json_elem) {
  text.aib_obj = new AibText();

  if (json_elem.maxlen)  // 0 means unlimited
    text.maxLength = json_elem.maxlen;
  text.password = json_elem.password;
  if (text.password !== '')
    text.type = 'password';

  return text;
  };

function setup_num(num, json_elem) {
  num.aib_obj = new AibNum();

  num.integer = json_elem.integer;
  num.max_decimals = json_elem.max_decimals;
  num.neg_display = json_elem.neg_display;

  return num;
  };

//function setup_lkup(text, json_elem) {
function setup_lkup(text, json_elem) {
  text.password = json_elem.password;

  text.aib_obj = new AibText();

  text.lkup = function() {  // press Ctrl+F or click ButtonTop
    if (text.amendable())
      // IE8 bug - if value is "", it returns "null" - this is a workaround
      var lkup_val = (text.value === '') ? '' : text.value;
    else
      var lkup_val = text.current_value;
    var args = [text.ref, lkup_val];
    send_request('req_lookup', args);
    };
  text.expander = function() {  // press Space
    // IE8 bug - if value is "", it returns "null" - this is a workaround
    var lkup_val = text.value === "" ? "" : text.value;
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
  lkup.title = 'Lookup (Ctrl+F)';
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
  lkdn.title = 'Lookdown (Shift+Enter)';
  lkdn.onclick = function() {
    if (text.frame.form.disable_count) return;
//    if (!text.amendable()) {
//      text.focus();
//      return;
//      };
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

function setup_textarea(text, json_elem) {
//  var text = document.createElement('div');
  text.style.width = (+json_elem.lng + 4) + 'px';
  text.style.height = ((json_elem.height * 17) + 4) + 'px';

  text.style.whiteSpace = 'pre-wrap';
  text.style.overflow = 'hidden';

  text.tabIndex = 0;
  text.password = '';
  text.multi_line = true;
  text.aib_obj = new AibText();

  return text;
  };

function setup_date(date, json_elem) {
  date.style[cssFloat] = 'left';

  date.aib_obj = new AibDate();

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
  container.appendChild(date);

  if (json_elem.readonly)
    return container;

  var cal = document.createElement('div');
  container.appendChild(cal);
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

function setup_bool(bool, label, json_elem) {
  bool.style[cssFloat] = 'left';

  if (window.SVGSVGElement !== undefined) {
    var NS='http://www.w3.org/2000/svg';
    var svg=document.createElementNS(NS,'svg');
    svg.setAttribute('focusable', false);  // IE11 workaround
    svg.style.width = '16px';
    svg.style.height = '16px';
    bool.appendChild(svg);
    };

  bool.aib_obj = new AibBool();
  bool.tabIndex = 0;
  bool.style.width = '16px';
  bool.style.height = '16px';
  bool.style.border = '1px solid black';
  bool.style.outline = 'none';  // disable highlight on focus

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

  bool.has_focus = false;
  bool.mouse_down = false;

  return bool;
  };

function setup_choice(choice, json_elem) {
  choice.aib_obj = new AibChoice();

  choice.style.height = '17px';
  choice.style.width = json_elem.lng + 'px';
  choice.style.padding = '1px';
  choice.style.border = '1px solid black';
  choice.style.font = '10pt Verdana,sans-serif';
  choice.style.color = 'navy';
  choice.style.outline = 'none';  // disable highlight on focus

  choice.data = [];
  choice.values = [];
  var subtype_name = json_elem.choices[0], choices = json_elem.choices[1];
  for (var key in choices) {
    var value = choices[key];
    if (typeof(key) === 'number')
      debug3('got number');
    if (typeof(key) === 'number')
      key += '';
    choice.data.push(key);
    choice.values.push(value)
    };

  if (json_elem.callback !== undefined)
    choice.callback = json_elem.callback;
  else if (subtype_name === null)
    choice.callback = function(option_selected) {};
  else {
    choice.subtype_name = subtype_name;
    choice.callback = function(subtype_id) {
      var subtype = choice.frame.subtypes[choice.subtype_name];
      if (subtype === undefined) return;
      if (subtype._active_subtype !== subtype_id) {
        subtype[subtype._active_subtype].style.display = 'none';
        subtype[subtype_id].style.display = 'block';
        subtype._active_subtype = subtype_id;
        };
      };
    };
  choice.dropdown = null;

  var container = document.createElement('div');
  container.style[cssFloat] = 'left';
  container.appendChild(choice);
  container.choice = choice;

  var down = document.createElement('div');
  container.appendChild(down);
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

function setup_radio(radio, json_elem) {
  radio.aib_obj = new AibRadio();

  radio.style.height = '17px';
  radio.style.padding = '1px 5px 1px 5px';
  radio.style.border = '1px solid grey';
  radio.style.font = '10pt Verdana,sans-serif';
  radio.style.color = 'navy';
  radio.style.outline = 'none';  // disable highlight on focus
  radio.tabIndex = 0;

  radio.data = [];
  radio.values = [];
  radio.buttons = [];
  var subtype_name = json_elem.choices[0], choices = json_elem.choices[1];

  for (var key in choices) {
    var value = choices[key];
    if (typeof(key) === 'number')
      debug3('got number');
    if (typeof(key) === 'number')
      key += '';
    radio.data.push(key);
    radio.values.push(value);

    var text = document.createElement('span');
    text.appendChild(document.createTextNode(value));
    text.style[cssFloat] = 'left';
    text.style.cursor = 'default';
    if (radio.childNodes.length)
      text.style.marginLeft = '10px';
    radio.appendChild(text);

    //var button = document.createElement('span');
    //button.appendChild(document.createTextNode('\u20DD'));
    var button = document.createElement('input');
    button.type = 'radio';
    button.style[cssFloat] = 'left';
    button.style.cursor = 'default';
    button.style.marginLeft = '5px';
    button.tabIndex = -1;
    button.pos = radio.buttons.length;
    button.radio = radio;

    button.onclick = function(e) {
      if (this.radio.frame.form.disable_count) return false;
      if (this.pos !== this.radio.ndx)
        this.radio.aib_obj.onselection(this.radio, this.pos);
      };

    radio.appendChild(button);
    radio.buttons.push(button);

    };

  radio.ndx = 0;
  radio.buttons[0].checked = true;

  if (json_elem.callback !== undefined)
    radio.callback = json_elem.callback;
  else if (subtype_name === null)
    radio.callback = function(option_selected) {};
  else {
    radio.subtype_name = subtype_name;
    radio.callback = function(subtype_id) {
      var subtype = radio.frame.subtypes[radio.subtype_name];
      if (subtype === undefined) return;
      if (subtype._active_subtype !== subtype_id) {
        subtype[subtype._active_subtype].style.display = 'none';
        subtype[subtype_id].style.display = 'block';
        subtype._active_subtype = subtype_id;
        };
      };
    };

  return radio;
  };

function setup_spin(spin, json_elem) {
  spin.style.border = '1px solid lightgrey';
  spin.tabIndex = 0;

  spin.style[cssFloat] = 'left';
  spin.style.height = '17px';
  spin.style.width = json_elem.lng + 'px';
  spin.style.padding = '1px';
  spin.style.border = '1px solid black';
  spin.style.font = '10pt Verdana,sans-serif';
  spin.style.color = 'navy';
  spin.style.outline = 'none';  // disable highlight on focus

  spin.aib_obj = new AibSpin();

  spin.min = json_elem.min;
  spin.max = json_elem.max;
  spin.callback = json_elem.callback;

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

function setup_sxml(sxml, json_elem) {
  if (json_elem.lng === null)
    sxml.style.width = '60px';
  else
    sxml.style.width = json_elem.lng + 'px';
  if (json_elem.label === null)
    sxml.appendChild(document.createTextNode('<xml>'));
  else
    sxml.appendChild(document.createTextNode(json_elem.label));

  sxml.style.background = button_background(sxml);
  sxml.style.border = '1px solid darkgrey';
  sxml.style.color = 'navy';
  sxml.style.outline = 'none';
  sxml.style.height = '22px';
  sxml.style.borderRadius = '4px';

  sxml.pos = frame.obj_list.length;
  frame.obj_list.push(sxml);
  frame.form.obj_dict[json_elem.ref] = sxml;
  sxml.frame = frame;
  sxml.nb_page = frame.page.nb_page;
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
    for (var key in choices) {
      var value = choices[key];
      if (typeof(key) === 'number')
        debug3('got number');
      if (typeof(key) === 'number')
        key += '';
      display.choice_data.push(key);
      display.choice_values.push(value)
      };
    };

  var text = document.createTextNode('');
  display.appendChild(text);
  //display.style.marginRight = '10px';
  display.style.textAlign = json_elem.align;
  display.style.width = json_elem.lng + 'px';
  display.display = true;  // used in start_frame() to prevent setting focus here

  display.pos = frame.obj_list.length;
  frame.obj_list.push(display);
  frame.form.obj_dict[json_elem.ref] = display;
  display.frame = frame;
  display.nb_page = frame.page.nb_page;
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
  button.style.outline = 'none';
  button.style.height = '22px';
  button.style.borderRadius = '4px';

  button.pos = frame.obj_list.length;
  frame.obj_list.push(button);
  frame.form.obj_dict[json_elem.ref] = button;
  button.frame = frame;
  button.nb_page = frame.page.nb_page;
  button.active_frame = frame;
  button.ref = json_elem.ref;
  button.help_msg = json_elem.help_msg;
  if (button.help_msg === '') button.help_msg = '\xa0';
  button.title = button.help_msg;
  button.mouse_down = false;
  button.has_focus = false;
  // button.readonly = false;
  button.readonly = json_elem.readonly;  // set in form defn
  button.after_focus = null;

  button.onmousedown = function() {button.mouse_down = true};
  button.onmouseup = function() {button.mouse_down = false};

  button.onfocus = function() {
    if (button.frame.form.disable_count) return false;
    //debug3(button.label.data + ' on focus');
    if (button.readonly || button.frame.form.readonly)
      button.style.background = button.bg_disabled;
    else
      button.style.background = button.bg_focus;
    if (button !== button.frame.default_button)
      button.style.border = '1px solid black';
    button.has_focus = true;
    if (button.mouse_down)
      return;  // will set focus from onclick()
    got_focus(button);
    };
  button.got_focus = function() {
    //debug3(button.label.data + ' got focus amd=' + button.frame.amended());
    button.frame.active_button = button;
    // if (button.frame.amended()) {  // changed [2019-11-28]
    if ((button.frame.amended() || !button.frame.obj_exists)) {
      var args = [button.ref];
      send_request('got_focus', args);
      }
    else {
      if (callbacks.length)
        setTimeout(function() {exec_callbacks()}, 0);
      };
    if (button.after_focus !== null) {
      button.after_focus();
      button.after_focus = null;
      };
    //debug3(button.label.data + ' [focus = ' + (button.form.current_focus) + ']');
    };

  button.onblur = function() {
    // not thought through! used when 'posting' a transaction, which clears the
    //   screen and re-opens the transaction header - need to reset button background
    button.style.background = button.bg_blur;
    if (button !== button.frame.default_button)
      button.style.border = '1px solid darkgrey';
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
    if (!e) e=window.event;
    if (e.ctrlKey) return;
    if (e.altKey) return;
    if ((e.key === 'ArrowLeft') || (e.key === 'ArrowUp'))
      var dir = -1
    else if ((e.key === 'ArrowRight') || (e.key === 'ArrowDown'))
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
    if (button.frame.form.disable_count) return;
    if (button.frame.form.readonly) return;
    // removed - 2020-11-24 - there may be a pending event to enable the button
    // replaced - 2022-04-19 - must not send 'click' event to server if button disabled
    // implications?
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
    };

  button.after_click = function() {
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
      case 'weight':
        button.style.fontWeight = val;  // 'bold' or 'normal'
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
    if (button.frame.form.readonly)
      return;
    button.readonly = state;
    if (state) {
      button.style.color = 'darkgrey';  //'#b8b8b8';
      if ((button.frame.form.current_focus === button) ||
          (button.frame.form.setting_focus === button)) {
        button.style.background = button.bg_disabled;
        var pos = button.pos + 1;
        if (pos === button.frame.obj_list.length)
          pos = 0;  // wrap around
        while (button.frame.obj_list[pos].offsetHeight === 0) {
          pos += 1;  // look for next available object
          if (pos === button.frame.obj_list.length)
            pos = 0;  // wrap around
          };
        var obj = button.frame.obj_list[pos];
        obj.focus();
        button.frame.form.setting_focus = obj;
        button.has_focus = false;
        };
      if (frame.default_button === button)
        button.style.border = '1px solid darkgrey';
      }
    else {
      button.style.color = 'navy';  //'black';  //'#101010';
      if (button.has_focus)
        button.style.background = button.bg_focus;
      if (frame.default_button === button)
        button.style.border = '1px solid blue';
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
