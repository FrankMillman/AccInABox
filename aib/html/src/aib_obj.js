/*
this is how to 'subclass' -

function AibCtrl() {};
AibCtrl.prototype.commonfunc = function() {can be called for all subclasses};

function AibText() {};
AibText.prototype = new AibCtrl();
AibText.prototype.textfunc = function() {can only be called for text subclasses};
AibText.prototype.commonfunc = function() {will override AibCtrl commonfunc};
*/

////////////////////
//  AibCtrl       //
////////////////////
function AibCtrl() {};
AibCtrl.prototype.got_focus = function(ctrl) {
  var inp = ctrl.childNodes[0];
  var dsp = ctrl.childNodes[1];
  if (!ctrl.amendable()) {

//    if (ctrl.tabIndex === -1) {
    if (dsp.style.display === 'none') {
      // can happen on navigating a form view -
      //   switching from blank row to existing row - key field becomes not amendable
      inp.style.display = 'none';
      dsp.style.display = 'block';
      ctrl.tabIndex = 0;
      ctrl.focus();
      };
    dsp.style.background = '#CCFFCC';  // light green
    if (dsp.txt !== undefined)
      dsp.txt.style.background = '#B4EEB4';  // slightly darker green

//    if (ctrl.frame.form.current_focus === ctrl)
//      ctrl.aib_obj.after_got_focus(ctrl)
//    else
//      got_focus(ctrl);
    return;
    };

//  if (ctrl.tabIndex === 0) {
  if (inp.style.display === 'none') {
    dsp.style.display = 'none';
    inp.style.display = 'block';
    ctrl.tabIndex = -1;
    };

//  if (ctrl.frame.form.focus_from_server)
  if (ctrl.frame.err_flag)
    inp.className = 'error_background'
  else
    inp.className = 'focus_background';

  //inp.focus();
  //got_focus(ctrl);
  };
AibCtrl.prototype.set_cell_value_from_server = function(grid, row, col, value) {
  var subset_row = row - grid.first_subset_row;
  grid.subset_data[subset_row][col] = value;
  // update cell if row is visible
  if (row >= grid.first_grid_row && row < (grid.first_grid_row+grid.num_grid_rows)) {
    var cell = grid.grid_rows[row-grid.first_grid_row].grid_cols[col];
    cell.aib_obj.set_cell_value_lost_focus(cell, value);
    };
  };
//AibCtrl.prototype.set_readonly = function(ctrl, state) {
//  var dsp = ctrl.childNodes[1];
//  if (state)  // set to readonly
//    dsp.style.color = 'grey';
//  else  // set to enabled
//    dsp.style.color = '';  // reset to CSS value
//  };

////////////////////
//  AibText       //
////////////////////
function AibText() {};
AibText.prototype = new AibCtrl();
AibText.prototype.after_got_focus = function(text) {
  var inp = text.childNodes[0];
  var dsp = text.childNodes[1];
  if (!text.amendable()) {
    if (text.password !== '')
      dsp.text.data = repeat('x', text.current_value.length);
    else
      dsp.text.data = text.current_value;
    dsp.style.border = '1px solid black';
    return;
    };
  inp.value = text.current_value;
  if (text.multi_line === true) {
    inp.scrollTop = 0;
    setInsertionPoint(inp, 0);
    }
  else
    setInsertionPoint(inp, 0);  //inp.value.length);
  };
AibText.prototype.set_dflt_val = function(text, value) {
  var inp = text.childNodes[0];
  inp.value = value;
  if (text.multi_line === true) {
    inp.scrollTop = 0;
    setInsertionPoint(inp, 0);
    }
  else
    setInsertionPoint(inp, 0);  //inp.value.length);
  };
AibText.prototype.before_lost_focus = function(text) {
  if (!text.amendable())
    return true;
  var inp = text.childNodes[0];
  if (text.multi_line === true)
    // IE8 converts all \n to \r\n
    // this converts it back again!
    text.current_value = inp.value.replace(/(\r\n|\n|\r)/gm, '\n');
  else
    text.current_value = inp.value;
  return true;
  };
AibText.prototype.after_lost_focus = function(text) {
  var inp = text.childNodes[0];
  var dsp = text.childNodes[1];
//  if (text.readonly) {
    dsp.style.border = '1px solid darkgrey';
    dsp.style.background = 'transparent';
    if (dsp.txt !== undefined)
      dsp.txt.style.background = '#f5f5f5';  // very light grey
//    return;
//    };
  if (text.password !== '')
    dsp.text.data = repeat('x', text.current_value.length);
  else
    dsp.text.data = text.current_value;
  inp.style.display = 'none';
  dsp.style.display = 'block';
  text.tabIndex = 0;
  };
AibText.prototype.ondownkey = function(text, e) {
  return true;
  };
AibText.prototype.onpresskey = function(text, e) {
  return true;
  };
//AibText.prototype.data_changed = function(text, value) {
//  return (value !== text.form_value);
//  };
AibText.prototype.data_changed = function(text) {
  var inp = text.childNodes[0];
  if (inp.style.display === 'none')
    return false
  else
    return (inp.value !== text.form_value);
  };
AibText.prototype.reset_value = function(text) {
  var inp = text.childNodes[0];
  var dsp = text.childNodes[1];
  inp.value = text.form_value;
  text.current_value = text.form_value;
  inp.focus();
  };
AibText.prototype.get_value_for_server = function(text) {
  if ((text.current_value === text.form_value) && (text.password === ''))
    return null;  // no change
  var value = text.current_value;
  if (text.password !== '') {
    text.form_value = value;  // save it now - no redisplay
    var pwd = value; value = '';
    for (var i=pwd.length; i<8; i++) pwd += '\x7f';  // pad to length of 8
    for (var i=0, l=pwd.length; i<l; i++) {
      value += String.fromCharCode(
        pwd.charCodeAt(i) -  parseInt(text.password[i%8]));
      };
    };
  return value;
  };
AibText.prototype.set_value_from_server = function(text, value) {
  if (value !== text.current_value) {
    text.current_value = value;
    var inp = text.childNodes[0];
    var dsp = text.childNodes[1];
    if (inp.style.display === 'none')
      dsp.text.data = value;
    else
      inp.value = value;
    };
  text.form_value = value;
  };
AibText.prototype.set_prev_from_server = function(text, value) {
  var inp = text.childNodes[0];
  var dsp = text.childNodes[1];
  if (inp.style.display === 'none')
    dsp.text.data = value;
  else
    inp.value = value;
  };
AibText.prototype.cell_data_changed = function(cell) {
  var grid = cell.grid;
  if (!grid.subset_data.length)
    return false;
  var subset_row = grid.first_grid_row - grid.first_subset_row + cell.grid_row;
  return cell.current_value !== grid.subset_data[subset_row][cell.grid_col];
  };
AibText.prototype.reset_cell_value = function(cell) {
  var grid = cell.grid;
  var subset_row = grid.first_grid_row - grid.first_subset_row + cell.grid_row;
  var value = grid.subset_data[subset_row][cell.grid_col];
  cell.current_value = value;
//  if (!(/\S/.test(value)))  // if cannot find a non-whitespace character
//    value = '\xa0';  // replace with &nbsp
  cell.text_node.data = value;
  };
AibText.prototype.before_cell_lost_focus = function(text) {
  text.current_value = text.value;
  return true;
  };
AibText.prototype.set_cell_value_got_focus = function(cell) {
//  var value = cell.current_value;
//  if (!(/\S/.test(value)))  // if cannot find a non-whitespace character
//    value = '\xa0';  // replace with &nbsp
//  cell.text_node.data = value;
  };
AibText.prototype.set_cell_dflt_val = function(cell, value) {
  cell.text_node.data = value;
  };
AibText.prototype.set_cell_value_lost_focus = function(cell, value) {
  cell.current_value = value;  // save for 'got_focus' and 'edit_cell'
  if (cell.input.choices)
    value = cell.input.choice_values[cell.input.choice_data.indexOf(value)];
//  if (!(/\S/.test(value)))  // if cannot find a non-whitespace character
//    value = '\xa0';  // replace with &nbsp
  cell.text_node.data = value;
  };
AibText.prototype.get_cell_value_for_server = function(cell) {
  if (!this.cell_data_changed(cell))
    return null;  // no change
  var value = cell.current_value;
  if (cell.input.password !== '') {
    // save it now - no redisplay
    var grid = cell.grid;
    var subset_row = grid.first_grid_row - grid.first_subset_row + cell.grid_row;
    grid.subset_data[subset_row][cell.grid_col] = value;
    var pwd = value; value = '';
    for (var i=pwd.length; i<8; i++) pwd += '\x7f';  // pad to length of 8
    for (var i=0, l=pwd.length; i<l; i++) {
      value += String.fromCharCode(
        pwd.charCodeAt(i) -  parseInt(cell.input.password[i%8]));
      };
    };
//  if (value === '\xa0')
//    value = '';
  return value;
  };
AibText.prototype.start_edit = function(input, current_value, keyCode) {  // called from grid
  if (keyCode === null)  // user pressed F2 or double-clicked
    input.value = current_value;
  else {
    input.value = String.fromCharCode(keyCode);
    };
  setInsertionPoint(input, input.value.length);
  };
AibText.prototype.convert_prev_cell_value = function(cell, prev_value) {
//  if (!(/\S/.test(prev_value)))  // if cannot find a non-whitespace character
//    prev_value = '\xa0';  // replace with &nbsp
  return prev_value;
  };

////////////////////
//  AibNum        //
////////////////////
function AibNum() {};
AibNum.prototype = new AibCtrl();
AibNum.prototype.after_got_focus = function(num) {
  var inp = num.childNodes[0];
  var dsp = num.childNodes[1];
  if (!num.amendable()) {
    dsp.text.data = this.num_to_string(num, num.current_value);
    dsp.style.border = '1px solid black';
    return;
    };
  inp.value = num.current_value;  // reset from display format to input format
  setInsertionPoint(inp, 0, inp.value.length);
  };
AibNum.prototype.set_dflt_val = function(num, value) {
  var inp = num.childNodes[0];
  inp.value = value;
  setInsertionPoint(inp, 0, inp.value.length);
  };
AibNum.prototype.before_lost_focus = function(num) {
  if (!num.amendable())
    return true;
  var inp = num.childNodes[0];
  num.current_value = inp.value;
  return true;
  };
AibNum.prototype.after_lost_focus = function(num) {
  var inp = num.childNodes[0];
  var dsp = num.childNodes[1];
  if (inp.style.display === 'none') {
    dsp.style.border = '1px solid darkgrey';
    dsp.style.background = 'transparent';
    dsp.txt.style.background = '#f5f5f5';  // very light grey
    return;
    };
  dsp.text.data = this.num_to_string(num, num.current_value);
  inp.style.display = 'none';
  dsp.style.display = 'block';
  num.tabIndex = 0;
  };
AibNum.prototype.num_to_string = function(num, value) {
  if (value === '')
    value  // no-op
  else if (num.neg_display === 'r') {  // minus sign on right
    if (value < 0)
      value = value.substring(1) + '-';
    else
      value += '\xa0';
    }
  else if (num.neg_display === 'b') {  // negative values in angle brackets
    if (value < 0)
      value = '<' + value.substring(1) + '>';
    else
      value += '\xa0';
    };
  return value;
  };
AibNum.prototype.ondownkey = function(num, e) {
  return true;
  };
AibNum.prototype.onpresskey = function(num, e) {
  if (!e.which) e.which=e.keyCode;
  if (e.which < 32)
    return true;
  return this.validate_chr(num, e.which);
  };
AibNum.prototype.validate_chr = function(num, key) {
//  var inp = num.firstChild;
  if (key >= 48 && key <= 57) {
//    var decimal_pos = inp.value.indexOf('.');
    var decimal_pos = num.get_val().indexOf('.');
    if (decimal_pos === -1)  // no decimal point present
      return true;
    if (num.integer)
      return false;  // decimal point not allowed
//    if (getCaret(inp) < decimal_pos)
    if (num.get_caret() < decimal_pos)
      return true;  // cursor is before decimal point - ok
//    var no_decimals = inp.value.length - decimal_pos - 1;
    var no_decimals = num.get_val().length - decimal_pos - 1;
    if (no_decimals === num.max_decimals)
      return false;
    return true;
    };
  if (
      key === 45 &&                          // minus sign
//      inp.value.indexOf('-') === -1 &&     // the only one
      num.get_val().indexOf('-') === -1 &&   // the only one
//      getCaret(inp) === 0                  // at the beginning
      num.get_caret() === 0                  // at the beginning
      )
    return true;
  if (
      key === 46 &&                      // decimal point
      !num.integer &&                    // not an 'integer' type
 //     inp.value.indexOf('.') === -1    // the only one
      num.get_val().indexOf('.') === -1  // the only one
      )
    return true;
  return false;
  };
//AibNum.prototype.data_changed = function(num, value) {
//  return (value !== num.form_value);
//  };
AibNum.prototype.data_changed = function(num) {
  var inp = num.childNodes[0];
  if (inp.style.display === 'none')
    return false
  else
    return (inp.value !== num.form_value);
  };
AibNum.prototype.reset_value = function(num) {
  num.value = num.form_value;
  num.current_value = num.form_value;
  num.focus();
  };
AibNum.prototype.get_value_for_server = function(num) {
  if (num.current_value === num.form_value)
    return null;  // no change
  if (num.reverse)
    return (-num.current_value) + ''
  else
    return num.current_value;
  };
AibNum.prototype.set_value_from_server = function(num, value) {
  if (num.reverse)
    var value = (-value) + '';
  if (value !== num.current_value) {
    num.current_value = value;
    var inp = num.childNodes[0];
    var dsp = num.childNodes[1];
    if (inp.style.display === 'none')
      dsp.text.data = this.num_to_string(num, value);
    else
      inp.value = value;
    };
  num.form_value = value
  };
AibNum.prototype.set_prev_from_server = function(num, value) {
  if (num.reverse)
    var value = (-value) + '';
  var inp = num.childNodes[0];
  var dsp = num.childNodes[1];
  if (inp.style.display === 'none')
    dsp.text.data = this.num_to_string(num, value);
  else
    inp.value = value;
  };
AibNum.prototype.cell_data_changed = function(cell) {
  var grid = cell.grid;
  var subset_row = grid.first_grid_row - grid.first_subset_row + cell.grid_row;
  return cell.current_value !== grid.subset_data[subset_row][cell.grid_col];
  };
AibNum.prototype.reset_cell_value = function(cell) {
  var grid = cell.grid;
  var subset_row = grid.first_grid_row - grid.first_subset_row + cell.grid_row;
  var value = grid.subset_data[subset_row][cell.grid_col];
  cell.current_value = value;
  cell.text_node.data = value;
  };
AibNum.prototype.before_cell_lost_focus = function(num) {
  num.current_value = num.value;
  return true;
  };
AibNum.prototype.set_cell_value_got_focus = function(cell) {
  var value = cell.current_value;
//  if (!(/\S/.test(value)))  // if cannot find a non-whitespace character
//    value = '\xa0';  // replace with &nbsp
  cell.text_node.data = value;
  };
AibNum.prototype.set_cell_dflt_val = function(cell, value) {
  cell.text_node.data = value;
  };
AibNum.prototype.set_cell_value_lost_focus = function(cell, value) {
  cell.current_value = value;  // save for 'got_focus' and 'edit_cell'
  if (cell.input.reverse)
    value = (-value) + '';
  value = this.num_to_string(cell.input, value);
//  if (!(/\S/.test(value)))  // if cannot find a non-whitespace character
//    value = '\xa0';  // replace with &nbsp
  cell.text_node.data = value;
  };
AibNum.prototype.get_cell_value_for_server = function(cell) {
  if (!this.cell_data_changed(cell))
    return null;  // no change
  var value = cell.current_value;
//  if (cell.input.reverse)
//    value = (-value) + '';
//  if (value === '\xa0')
//    value = '';
  return value;
  };
AibNum.prototype.start_edit = function(input, current_value, keyCode) {  // called from grid
  if (keyCode === null)  // user pressed F2 or double-clicked
    input.value = current_value;
  else {
    input.value = '';
    if (this.validate_chr(input, keyCode))
      input.value = String.fromCharCode(keyCode);
    };
  setInsertionPoint(input, input.value.length);
  };
AibNum.prototype.convert_prev_cell_value = function(cell, prev_value) {
  if (cell.input.reverse)
    if (prev_value !== '')
      prev_value = (-prev_value) + '';
//  if (!(/\S/.test(prev_value)))  // if cannot find a non-whitespace character
//    prev_value = '\xa0';  // replace with &nbsp
  return prev_value;
  };

////////////////////
//  AibDate       //
////////////////////
function AibDate() {};
AibDate.prototype = new AibCtrl();
AibDate.prototype.after_got_focus = function(date) {
  var inp = date.childNodes[0];
  var dsp = date.childNodes[1];
  if (!date.amendable()) {
    dsp.text.data = this.date_to_string(date, date.current_value, date.display_format);
    dsp.style.border = '1px solid black';
    return;
    };
  if (date.valid) {
    inp.value = this.date_to_string(date, date.current_value, date.input_format);
    date.pos = 0;  //date.blank.length;
    setInsertionPoint(inp, 0);  //, date.pos);
    date.selected = true;
    }
  else  // returning from failed validation - leave string untouched
    date.pos = 0;
  };
AibDate.prototype.set_dflt_val = function(date, value) {
  var inp = date.childNodes[0];
  inp.value = this.date_to_string(date, value, date.input_format);
  setInsertionPoint(inp, 0, inp.value.length);
  };
AibDate.prototype.before_lost_focus = function(date) {
  if (!date.amendable())
    return true;
  var inp = date.childNodes[0];
  date.valid = true;
  var errmsg = this.validate_string(date);  // sets up current_value if ok
  if (errmsg !== '') {
    date.valid = false;
    date.focus();
    setTimeout(function() {show_errmsg('Date', errmsg)}, 0);
    //show_errmsg('Date', errmsg);
    return false;
    };
  return true;
  };
AibDate.prototype.after_lost_focus = function(date) {
  var inp = date.childNodes[0];
  var dsp = date.childNodes[1];
  if (inp.style.display === 'none') {
    dsp.style.border = '1px solid darkgrey';
    dsp.style.background = 'transparent';
    dsp.txt.style.background = '#f5f5f5';  // very light grey
    return;
    };
  dsp.text.data = this.date_to_string(date, date.current_value, date.display_format);
  inp.style.display = 'none';
  dsp.style.display = 'block';
  date.tabIndex = 0;
  };
AibDate.prototype.validate_string = function(date) {
  if (date.childNodes.length)  // 'date' is a gui_obj
    var inp = date.childNodes[0];
  else  // 'date' is a grid_obj
    var inp = date;
  if (inp.value === date.blank) {
    date.current_value = '';
    return '';  // no error
    };
  var today = new Date();
  var year, month, day;
  if (!date.yr_pos.length)
    year = today.getFullYear()
  else {
    year = inp.value.substr(date.yr_pos[0], date.yr_pos[1]);
    year = year.replace(/ /g, '')  // strip spaces
    if (!year.length)
      year = today.getFullYear()
    else if (year.length === 2) {
      var this_year = today.getFullYear();
      year = +year + (Math.round(this_year/100)*100);
      if (year - this_year > 10)
        year -= 100
      else if (year - this_year < -90)
        year += 100
      };
    };
  if (!date.mth_pos.length)
    month = today.getMonth()
  else {
    month = inp.value.substr(date.mth_pos[0], date.mth_pos[1]);
    month = month.replace(/ /g, '')  // strip spaces
    if (!month.length)
      month = today.getMonth()+1
    }
  if (!date.day_pos.length)
    day = today.getDate()
  else
    day = inp.value.substr(date.day_pos[0], date.day_pos[1]);
  // use string values to construct new date
  var new_date = new Date(year, month-1, day);
  if (new_date.getDate() !== +day) {
    return msg = '"' + day + '" - Invalid day!';
    };
  if (new_date.getMonth()+1 !== +month) {
    return msg = '"' + month + '" - Invalid month!';
    };
  if (new_date.getFullYear() !== +year) {
    return msg = '"' + year + '" - Invalid year!';
    };
  //date.current_value = new_date;
  date.current_value = new_date.getFullYear() + '-' +
    zfill(new_date.getMonth()+1, 2) + '-' + zfill(new_date.getDate(), 2);
  return '';  // no error
  };
AibDate.prototype.date_to_string = function(date, value, format) {
  var output = '';
  if (value === '')
    if (format === date.display_format)
      return '';
    else
      return date.blank;
  var dt = value.split('-');
  var date_obj = new Date(dt[0], dt[1]-1, dt[2]);
  for (var i=0, l=format.length; i<l; i++) {
    if (format[i] === '%') {
      switch(format[i+1]) {
        case 'd': {
          //var dd = date_obj.getDate() + '';
          //if (dd.length === 1) output += '0';
          var dd = zfill(date_obj.getDate(), 2);
          output += dd;
          break;
          }
        case 'm': {
          //var mm = (date_obj.getMonth() + 1) + '';  // + 1 to change 0-11 to 1-12
          //if (mm.length === 1) output += '0';
          var mm = zfill((date_obj.getMonth() + 1), 2);  // + 1 to change 0-11 to 1-12
          output += mm;
          break;
          }
        case 'y': {
          var yyyy = date_obj.getFullYear() + '';
          output += yyyy.substring(2);
          break;
          }
        case 'Y': {
          var yyyy = date_obj.getFullYear() + '';
          output += yyyy;
          break;
          }
        case 'a': {
          output += ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][date_obj.getDay()]
          break;
          }
        case 'b': {
          output += ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][date_obj.getMonth()]
          break;
          }
        }
      i += 1;
      }
    else
      output += format[i];
    };
    return output;
  };
AibDate.prototype.test_literal = function(date, pos) {
  for (var i=0, l=date.literal_pos.length; i<l; i++)
    if (pos === date.literal_pos[i])
      return true;
  return false;
  };
AibDate.prototype.show_cal = function(date) {
  if (!date.amendable())
    return;
  show_cal(date, date.current_value, this.after_cal);
  date.selected = false;
  };
AibDate.prototype.after_cal = function(date, new_date) {
  if (new_date != null)  // else keep old date
    date.current_value = new_date;
  AibDate.prototype.after_got_focus(date);
  setTimeout(function() {date.focus()}, 0);
  };
AibDate.prototype.handle_bs = function(date) {
  if (date.childNodes.length)  // 'date' is a gui_obj
    var inp = date.childNodes[0];
  else  // 'date' is a grid_obj
    var inp = date;
  if (date.pos > 0) {

    while (this.test_literal(date, date.pos-1))
      date.pos -= 1;
    date.pos -= 1;
    inp.value =
      inp.value.substring(0, date.pos) + ' ' +
      inp.value.substring(date.pos+1);

//    date.pos -= 1;
//    while (this.test_literal(date, date.pos))
//      date.pos -= 1;
//    inp.value =
//      inp.value.substring(0, date.pos) + ' ' +
//      inp.value.substring(date.pos+1);
    };
  date.selected = false;
  };
AibDate.prototype.handle_del = function(date) {
  if (date.childNodes.length)  // 'date' is a gui_obj
    var inp = date.childNodes[0];
  else  // 'date' is a grid_obj
    var inp = date;
  if (!this.test_literal(date, date.pos))
    inp.value =
      inp.value.substring(0, date.pos) + ' ' +
      inp.value.substring(date.pos+1);
  date.selected = false;
  };
AibDate.prototype.handle_left = function(date) {
  if (date.pos > 0) {
    date.pos -= 1;
//    while (this.test_literal(date, date.pos-1))
//      date.pos -= 1;
    };
  date.selected = false;
  };
AibDate.prototype.handle_right = function(date) {
  if (date.pos < date.blank.length) {
    date.pos += 1;
//    while (this.test_literal(date, date.pos-1))
//      date.pos += 1;
    };
  date.selected = false;
  };
AibDate.prototype.handle_home = function(date) {
  date.pos = 0;
  date.selected = false;
  };
AibDate.prototype.handle_end = function(date) {
  date.pos = date.blank.length;
  date.selected = false;
  };
//AibDate.prototype.handle_dot = function(date) {
//  if (date.selected) {
//    date.pos = date.blank.length;
//    date.pos = 0;
//    date.selected = false;
//    date.value =
//      date.value.substring(0, date.pos) + '.' +
//      date.value.substring(date.pos+1);
//    date.pos += 1;
//    };
//  };
AibDate.prototype.handle_keyCode = function(date, keyCode) {
  if (date.childNodes.length)  // 'date' is a gui_obj
    var inp = date.childNodes[0];
  else  // 'date' is a grid_obj
    var inp = date;
  if (date.selected) {
    inp.value = date.blank;
    date.pos = 0;
    date.selected = false;
    };
  inp.value =
    inp.value.substring(0, date.pos) +
    String.fromCharCode(keyCode) +
    inp.value.substring(date.pos+1);
  date.pos += 1;
  while (this.test_literal(date, date.pos))
    date.pos += 1;
  };
AibDate.prototype.onkey = function(date, e) {
  if (date.childNodes.length)  // 'date' is a gui_obj
    var inp = date.childNodes[0];
  else  // 'date' is a grid_obj
    var inp = date;
  // allow 'space' (32) for use as 'date expander'
  if (e.keyCode < 33 && e.keyCode !== 8)
    return true;
  if (e.ctrlKey || e.altKey)
    return true;
//  if (e.keyCode === 32) this.show_cal(date)
  if (e.keyCode === 8) this.handle_bs(date)
  else if (e.keyCode === 46) this.handle_del(date)
  else if (e.keyCode === 37) this.handle_left(date)
  else if (e.keyCode === 39) this.handle_right(date)
  else if (e.keyCode === 36) this.handle_home(date)
  else if (e.keyCode === 35) this.handle_end(date)
//  else if (e.keyCode === 190) this.handle_dot(date)
  else if (e.keyCode >= 48 && e.keyCode <= 57) this.handle_keyCode(date, e.keyCode)
  else if ((e.keyCode >= 96 && e.keyCode <= 105) && (navigator.appName !== 'Opera'))
    this.handle_keyCode(date, e.keyCode-48);
//  else {
//    date.pos = 0;
//    return;
//    };
  setInsertionPoint(inp, date.pos);
  e.cancelBubble = true;
  return false;
  };
if (navigator.appName === 'Opera') {
  AibDate.prototype.onpresskey = AibDate.prototype.onkey;
  AibDate.prototype.ondownkey = function(date, e) {return true;};
  }
else {
  AibDate.prototype.ondownkey = AibDate.prototype.onkey;
  AibDate.prototype.onpresskey = function(date, e) {return true;};
  };
//AibDate.prototype.data_changed = function(date, value) {
//  return (value !== this.date_to_string(date, date.form_value, date.input_format));
//  };
AibDate.prototype.data_changed = function(date) {
  var inp = date.childNodes[0];
  if (inp.style.display === 'none')
    return false
  else
    return (inp.value !== this.date_to_string(date, date.form_value, date.input_format));
  };
AibDate.prototype.reset_value = function(date) {
  var inp = date.childNodes[0];
  inp.value = this.date_to_string(date, date.form_value, date.input_format);
  date.current_value = date.form_value;
  date.pos = 0;
  setInsertionPoint(inp, 0);
  inp.focus();
  };
AibDate.prototype.get_value_for_server = function(date) {
  if (date.current_value === date.form_value)
    return null;  // no change
  var value = date.current_value;
//  if (value === null)
//    return ''
//  else
//    return value.getFullYear() + '-' + (zfill(value.getMonth()+1, 2))
//      + '-' + zfill(value.getDate(), 2);
  return value;
  };
AibDate.prototype.set_value_from_server = function(date, value) {
  var inp = date.childNodes[0];
  var dsp = date.childNodes[1];
  if (value === '') {
    date.current_value = '';
    inp.value = '';
    dsp.text.data = '';
    }
  else {
//    var dt = value.split('-');
//    var date_obj = new Date(dt[0], dt[1]-1, dt[2]);
    if (value !== date.current_value) {
      date.current_value = value;
      if (inp.style.display === 'none')
        dsp.text.data = this.date_to_string(date, value, date.display_format);
      else
        inp.value = this.date_to_string(date, value, date.input_format);
      };
    };
  date.form_value = date.current_value;
  };
AibDate.prototype.set_prev_from_server = function(date, value) {
  var inp = date.childNodes[0];
  var dsp = date.childNodes[1];
  if (value === '') {
    inp.value = '';
    dsp.text.data = '';
    }
  else {
//    var dt = value.split('-');
//    var date_obj = new Date(dt[0], dt[1]-1, dt[2]);
    if (value !== date.current_value) {
      if (inp.style.display === 'none')
        dsp.text.data = this.date_to_string(date, value, date.display_format);
      else
        inp.value = this.date_to_string(date, value, date.input_format);
      };
    };
  };
AibDate.prototype.cell_data_changed = function(cell) {
  var grid = cell.grid;
  var subset_row = grid.first_grid_row - grid.first_subset_row + cell.grid_row;
  return cell.current_value !== grid.subset_data[subset_row][cell.grid_col];
  };
AibDate.prototype.reset_cell_value = function(cell) {
  var grid = cell.grid;
  var subset_row = grid.first_grid_row - grid.first_subset_row + cell.grid_row;
  var value = grid.subset_data[subset_row][cell.grid_col];
  cell.current_value = value;
//  if (!(/\S/.test(value)))  // if cannot find a non-whitespace character
//    value = '\xa0';  // replace with &nbsp

//  // *** value format is 'yyyy-mm-dd ***
//  if (value === '') {
//    var date_obj = null;
//    }
//  else {
//    var dt = value.split('-');
//    var date_obj = new Date(dt[0], dt[1]-1, dt[2]);
//    };
//  cell.current_value = date_obj;

  var date = cell.input;
  value = this.date_to_string(date, value, date.display_format);
  cell.text_node.data = value;
  };
AibDate.prototype.before_cell_lost_focus = function(date) {
  date.valid = true;
  var errmsg = this.validate_string(date);  // sets up current_value if ok
  if (errmsg !== '') {
    date.valid = false;
    setTimeout(function() {show_errmsg('Date', errmsg)}, 0);
    return false;
    };
  return true;
  };
AibDate.prototype.set_cell_value_got_focus = function(cell) {
//  var date_obj = cell.current_value;
  // *** value format is 'yyyy-mm-dd ***
//  if (value === '') {
//    var date_obj = null;
//    }
//  else {
//    var dt = value.split('-');
//    var date_obj = new Date(dt[0], dt[1]-1, dt[2]);
//    };

  var date = cell.input;
  value = this.date_to_string(date, cell.current_value, date.input_format);
//  if (!(/\S/.test(value)))  // if cannot find a non-whitespace character
//    value = '\xa0';  // replace with &nbsp
  cell.text_node.data = value;
  };
AibDate.prototype.set_cell_dflt_val = function(cell, value) {
  cell.text_node.data = this.date_to_string(date, value, date.input_format);
  };
AibDate.prototype.set_cell_value_lost_focus = function(cell, value) {
  cell.current_value = value;  // save for 'got_focus' and 'edit_cell'

//  // *** value format is 'yyyy-mm-dd ***
//  if (value === '') {
//    var date_obj = null;
//    }
//  else {
//    var dt = value.split('-');
//    var date_obj = new Date(dt[0], dt[1]-1, dt[2]);
//    };

  var date = cell.input;
  value = this.date_to_string(date, value, date.display_format);
//  if (!(/\S/.test(value)))  // if cannot find a non-whitespace character
//    value = '\xa0';  // replace with &nbsp
  cell.text_node.data = value;
  };
AibDate.prototype.get_cell_value_for_server = function(cell) {
  if (!this.cell_data_changed(cell))
    return null;  // no change
  var value = cell.current_value;
//  if (value === null)
//    return ''
//  else
//    return value.getFullYear() + '-' + (zfill(value.getMonth()+1, 2))
//      + '-' + zfill(value.getDate(), 2);
  return value;
  };
AibDate.prototype.start_edit = function(input, current_value, keyCode) {  // called from grid
  var date = input;
  if (keyCode === null) {  // user pressed F2 or double-clicked
    date.value = current_value;
    date.pos = date.blank.length;
    setInsertionPoint(date, date.pos);
    date.selected = true;
    }
  else {
    date.value = date.blank;
    date.selected = true;
    if (keyCode === 8) this.handle_bs(date)
    else if (keyCode === 46) this.handle_del(date)
    else if (keyCode === 37) this.handle_left(date)
    else if (keyCode === 39) this.handle_right(date)
    else if (keyCode === 36) this.handle_home(date)
    else if (keyCode === 35) this.handle_end(date)
    else if (keyCode >= 48 && keyCode <= 57) this.handle_keyCode(date, keyCode)
    else if ((keyCode >= 96 && keyCode <= 105) && (navigator.appName !== 'Opera'))
      this.handle_keyCode(date, keyCode-48)
    setInsertionPoint(date, date.pos);
    };
  };
AibDate.prototype.convert_prev_cell_value = function(cell, prev_value) {
//  if (prev_value === '') {
//    var date_obj = null;
//    }
//  else {
//    var dt = prev_value.split('-');
//    var date_obj = new Date(dt[0], dt[1]-1, dt[2]);
//    };
  var date = cell.input;
  prev_value = this.date_to_string(date, prev_value, date.input_format);
//  if (!(/\S/.test(prev_value)))  // if cannot find a non-whitespace character
//    prev_value = '\xa0';  // replace with &nbsp
  return prev_value;
  };
AibDate.prototype.grid_show_cal = function(date) {
  var date_obj = date.cell.current_value;
  // *** value format is 'yyyy-mm-dd ***
//  if (value === '') {
//    var date_obj = null;
//    }
//  else {
//    var dt = value.split('-');
//    var date_obj = new Date(dt[0], dt[1]-1, dt[2]);
//    };
  show_cal(date, date_obj, this.grid_after_cal);
  date.selected = false;
  };
AibDate.prototype.grid_after_cal = function(date, new_date) {
  // to investigate -
  // 1. is grid_amended always true? what if no change?
  // 2. alternatively, could call start_edit
  //    slightly more consistent with (e.g.) backslash, and allows esc to reset
  var cell = date.cell;
  if (new_date != null) {  // else keep old date
    cell.current_value = new_date;
//      new_date.getFullYear() + '-' + zfill((new_date.getMonth()+1), 2)
//        + '-' + zfill(new_date.getDate(), 2);
    cell.grid.set_amended(true);
    };
  date.aib_obj.set_cell_value_got_focus(cell);
  setTimeout(function() {cell.grid.focus()}, 0);
  };

////////////////////
//  AibBool       //
////////////////////
function AibBool() {};
AibBool.prototype = new AibCtrl();
AibBool.prototype.got_focus = function(bool) {
//  bool.has_focus = true;
//  if (bool.mouse_down)
//    return;  // will set focus from onclick()
//  got_focus(bool);
  };
AibBool.prototype.after_got_focus = function(bool) {
  bool.style.border = '1px solid black';
//  if (bool.frame.form.focus_from_server)
  if (bool.frame.err_flag)
    bool.className = 'error_background'
  else if (!bool.amendable())
    bool.className = 'readonly_background';
  else
    bool.className = 'focus_background';
  };
AibBool.prototype.set_dflt_val = function(bool, value) {
  // don't think this will work
  // if user tabs off, how do we know value has changed?
  if (value === '1')
    this.draw_chk(bool)
  else
    this.draw_unchk(bool);
  };
AibBool.prototype.before_lost_focus = function(bool) {
  return true;
  };
AibBool.prototype.after_lost_focus = function(bool) {
  bool.className = 'blur_background';
  bool.style.border = '1px solid darkgrey';
  bool.has_focus = false;
  };
//AibBool.prototype.set_readonly = function(bool, state) {
//  if (state) {
//    bool.style.color = 'grey';
////    bool.style.background = '#f0f0f0';
//    }
//  else {
//    bool.style.color = null;  //'navy';
////    bool.style.background = '';
//    // reset so that it gets background from className
//    // works with Chrome, not with IE8
////    bool.className = 'blur_background';
//    };
//  };
/*
AibBool.prototype.onclick = function(bool) {
  if (bool.frame.form.disable_count) return false;
  if (!bool.amendable()) return false;
//  if (bool.frame.form.current_focus !== bool) {
//    if (bool.has_focus)
//      got_focus(bool);  // call lost_focus(), got_focus()
//    else
//      bool.focus();  // set focus on bool first
//    };
//  bool.focus();  // in case it does not have focus - if it does, nothing will happen
//  if (bool.frame.amended() && !bool.frame.form.focus_from_server) {
//    var args = [bool.ref];
//    send_request('got_focus', args);
//    };
  this.chkbox_change(bool);
  if (bool.has_focus)
    got_focus(bool);  // call lost_focus(), got_focus()
  else
    bool.focus();  // set focus on bool first
  };
*/
AibBool.prototype.ondownkey = function(bool, e) {
  if (!bool.amendable())
    return;
  if (e.keyCode === 32)
    this.chkbox_change(bool);
  };
AibBool.prototype.onpresskey = function(bool, e) {
  return true;
  };
AibBool.prototype.chkbox_change = function(bool) {
  //bool.value = !bool.value;
  //if (bool.value)
  //  this.draw_chk(bool)
  //else
  //  this.draw_unchk(bool);

  if (bool.value === '1') {
    bool.value = '0';
    this.draw_unchk(bool);
    }
  else {
    bool.value = '1';
    this.draw_chk(bool);
    };

  var args = [bool.ref];
  send_request('cb_checked', args);
  //bool.frame.set_amended(true);
  bool.current_value = bool.value;
  };
//AibBool.prototype.data_changed = function(bool, value) {
//  return (value !== bool.form_value);
//  };
AibBool.prototype.data_changed = function(bool) {
  return (bool.current_value !== bool.form_value);
  };
AibBool.prototype.reset_value = function(bool) {
  bool.value = bool.form_value;
  bool.current_value = bool.form_value;
  bool.focus();
  };
AibBool.prototype.get_value_for_server = function(bool) {
  /*
  if (bool.current_value)
    return '1'
  else
    return '0';
  */
  if (bool.current_value === bool.form_value)
    return null;  // no change
  return bool.current_value;
  };
AibBool.prototype.set_value_from_server = function(bool, value) {
  /*
  if (value === '1')
    var bool_value = true
  else
    var bool_value = false;
  if (bool_value !== bool.current_value) {
    bool.current_value = bool_value;
    bool.value = bool_value;
    //bool.style.backgroundImage = 'url(' + bool.images[+bool.value] + ')';
    if (bool_value)
      this.draw_chk(bool)
    else
      this.draw_unchk(bool);
    };
  bool.form_value = bool_value;
  */
  if (value !== bool.current_value) {
    bool.current_value = value;
    if (value === '1')
      this.draw_chk(bool)
    else
      this.draw_unchk(bool);
    };
  bool.form_value = value;
  };
AibBool.prototype.set_prev_from_server = function(bool, value) {
  if (value !== bool.current_value) {
    bool.current_value = value;
    if (value === '1')
      this.draw_chk(bool)
    else
      this.draw_unchk(bool);
    };
  };
AibBool.prototype.cell_data_changed = function(cell) {
  var grid = cell.grid;
  var subset_row = grid.first_grid_row - grid.first_subset_row + cell.grid_row;
  return cell.current_value !== grid.subset_data[subset_row][cell.grid_col];
  };
AibBool.prototype.reset_cell_value = function(cell) {
  var grid = cell.grid;
  var subset_row = grid.first_grid_row - grid.first_subset_row + cell.grid_row;
  var value = grid.subset_data[subset_row][cell.grid_col];
  cell.current_value = value;
  if (value === '1') {
    this.draw_chk(cell.firstChild);
    }
  else {
    this.draw_unchk(cell.firstChild);
    };
  };
AibBool.prototype.set_cell_value_got_focus = function(cell) {
  };
AibBool.prototype.set_cell_value_lost_focus = function(cell, value) {
  cell.current_value = value;
  if (value === '1') {
    this.draw_chk(cell.firstChild);
    }
  else {
    this.draw_unchk(cell.firstChild);
    };
  };
AibBool.prototype.get_cell_value_for_server = function(cell) {
  if (!this.cell_data_changed(cell))
    return null;  // no change
  return cell.current_value;
  };
AibBool.prototype.grid_chkbox_change = function(cell, row) {
  if (cell.current_value === '0') {
    cell.current_value = '1';
    this.draw_chk(cell.firstChild);
    }
  else {
    cell.current_value = '0';
    this.draw_unchk(cell.firstChild);
    };
  var grid = cell.grid;
  var args = [cell.input.ref, row];
  send_request('cell_cb_checked', args);
  grid.set_amended(true);
  };

if (window.SVGSVGElement === undefined) {  // no svg - use vml (IE8)
  document.namespaces.add('v','urn:schemas-microsoft-com:vml');
  AibBool.prototype.draw_chk = function(bool) {
    if (bool.firstChild)
      bool.removeChild(bool.firstChild);
    var line = document.createElement('v:polyline');
    bool.appendChild(line);
    line.points =
      '4,8 5,8 5,10 6,10 6,11 6,10 7,10 7,9 8,9 8,8 9,8 9,7 10,7 10,6 11,6 11,5';
    line.style.behavior = 'url(#default#VML)';
    line.style.display = 'inline-block';
    };
  AibBool.prototype.draw_unchk = function(bool) {
    if (bool.firstChild)
      bool.removeChild(bool.firstChild);
    };
  }
else {  // svg available - use it (the rest)
  AibBool.prototype.draw_chk = function(bool) {
    var svg = bool.firstChild;
    if (svg.firstChild)
      svg.removeChild(svg.firstChild);
    var NS='http://www.w3.org/2000/svg';
    var line = document.createElementNS(NS,'polyline')
    svg.appendChild(line);
    line.setAttributeNS(null, 'points',
      '4,8 5,8 5,10 6,10 6,11 6,10 7,10 7,9 8,9 8,8 9,8 9,7 10,7 10,6 11,6 11,5');
    line.setAttributeNS(null, 'fill', 'none');
    line.setAttributeNS(null, 'stroke', 'black');
    };
  AibBool.prototype.draw_unchk = function(bool) {
    var svg = bool.firstChild;
    if (svg.firstChild)
      svg.removeChild(svg.firstChild);
    };
  };

////////////////////
//  AibChoice     //
////////////////////
function AibChoice() {};
AibChoice.prototype = new AibCtrl();
AibChoice.prototype.after_got_focus = function(choice) {
  var inp = choice.childNodes[0];
  var dsp = choice.childNodes[1];
  if (!choice.amendable()) {
    dsp.style.border = '1px solid black';
    return;
    };
//  if (choice.current_value === '') {
//    choice.current_value = choice.data[0];
//    choice.ndx = 0;
//    choice.callback(choice.current_value);
//    };
  inp.innerHTML = html_esc(choice.values[choice.ndx]);
  };
AibChoice.prototype.before_lost_focus = function(choice) {
  return true;
  };
AibChoice.prototype.after_lost_focus = function(choice) {
  var inp = choice.childNodes[0];
  var dsp = choice.childNodes[1];
  if (inp.style.display === 'none') {
    dsp.style.border = '1px solid darkgrey';
    dsp.style.background = 'transparent';
    dsp.txt.style.background = '#f5f5f5';  // very light grey
    return;
    };
  dsp.text.data = choice.values[choice.ndx];
  inp.style.display = 'none';
  dsp.style.display = 'block';
  choice.tabIndex = 0;
  };
AibChoice.prototype.close_dropdown = function(choice) {
  if (choice.dropdown !== null) {
    if (document.detachEvent) {
      document.detachEvent('onclick', choice.dropdown.onclick);
      }
    else if (document.removeEventListener) {
      document.removeEventListener('click', choice.dropdown.onclick, false);
      };
    choice.removeChild(choice.dropdown);
    choice.dropdown = null;
    };
  };
AibChoice.prototype.onselection = function(choice, option_selected) {
  this.close_dropdown(choice);
//  if (option_selected !== null) {
//    choice.current_value = choice.data[option_selected];
//    choice.ndx = option_selected;
//    choice.innerHTML = choice.values[option_selected];
//    if (choice.callback !== undefined)
//      choice.callback(choice.data[option_selected]);
//    };
//  setTimeout(function() {choice.focus()}, 0);

  // on_selection can be after_selection() or grid_after_selection()
  choice.on_selection(choice, option_selected);
  };
AibChoice.prototype.after_selection = function(choice, option_selected) {
  if (option_selected !== null) {
    choice.current_value = choice.data[option_selected];
    choice.ndx = option_selected;
    var inp = choice.childNodes[0];
    inp.innerHTML = html_esc(choice.values[option_selected]);
    choice.callback(choice.current_value);

//    var subtype_name = choice.subtype_name;  //'body.type';
//    if (subtype_name !== null) {
//      var subtype_id = choice.current_value;
//      var subtype = choice.frame.subtypes[subtype_name];
//      subtype[subtype._active_box].style.display = 'none';
//      subtype[subtype_id].style.display = 'block';
//      subtype._active_box = subtype_id;
//      };

//  this.after_got_focus(choice);
    };
  setTimeout(function() {choice.focus()}, 0);
  };
AibChoice.prototype.create_dropdown = function(choice) {
  var dropdown = document.createElement('div');
  choice.appendChild(dropdown);
  dropdown.choice = choice;
  choice.dropdown = dropdown;
  dropdown.tabIndex = 0;

  //dropdown.style.position = 'absolute';
  //dropdown.style.left = choice.parentNode.offsetLeft + 'px';
  //dropdown.style.top = (choice.parentNode.offsetTop + 23) + 'px';

  dropdown.style.position = 'fixed';
  //choice.parentNode.style.parentNode = 'relative';
  //dropdown.style.position = 'absolute';
  var choice_pos = find_pos(choice.parentNode);
  dropdown.style.left = (choice_pos[0]) + 'px';
  dropdown.style.top = (choice_pos[1] + 23) + 'px';

  dropdown.style.background = 'white';
  dropdown.style.border = '1px solid grey';
  dropdown.style.width = 'auto';
  dropdown.style.height = 'auto';
  dropdown.style.paddingTop = '5px';;
  dropdown.style.paddingBottom = '5px';
  dropdown.clicked = null;
  dropdown.id = '$drop';

  dropdown.onclick = function() {
    var parent = document.getElementById('$drop').choice;
    parent.aib_obj.onselection(parent, parent.dropdown.clicked)
    };

  if (document.attachEvent)
    document.attachEvent('onclick', dropdown.onclick);
  else if (document.addEventListener)
    document.addEventListener('click', dropdown.onclick, false);

  for (var i=0, l=choice.values.length; i<l; i++) {
    var row = document.createElement('div');
    row.pos = i;
    row.style.paddingLeft = '10px';;
    row.style.paddingRight = '10px';
    row.style.width = 'auto';
    row.style.cursor = 'default';
    if (i === choice.ndx) {
      row.style.background = 'darkblue';
      row.style.color = 'white';
      dropdown.option_highlighted = i;
//      }
//    else if (i % 2) {
//      row.style.background = 'gainsboro';
      };
    row.innerHTML = html_esc(choice.values[i]);
    row.onmouseover = function(e) {
      debug4('op');  // workaround for Opera
      var dropdown = row.parentNode;
      if (dropdown.option_highlighted !== this.pos) {
        dropdown.childNodes[dropdown.option_highlighted].style.background = 'white';
        dropdown.childNodes[dropdown.option_highlighted].style.color = 'black';
        dropdown.option_highlighted = this.pos;
        dropdown.childNodes[dropdown.option_highlighted].style.background = 'darkblue';
        dropdown.childNodes[dropdown.option_highlighted].style.color = 'white';
        };
      };
    row.onclick = function() {
      // will bubble up to dropdown.onclick()
      dropdown.clicked = this.pos;
      };

    dropdown.appendChild(row);
    };
  if (dropdown.offsetWidth < (choice.offsetWidth+22))
    dropdown.style.width = (choice.offsetWidth+22) + 'px';

  dropdown.onkey = function(e) {
    debug4('op');  // workaround for Opera
    if (!e) e=window.event;
    if (e.ctrlKey || e.altKey) return;
    if ((e.keyCode === 13) || (e.keyCode === 32))  // enter|space
      dropdown.choice.aib_obj.onselection(dropdown.choice, this.option_highlighted);
    else if (e.keyCode === 27)  // escape
      dropdown.choice.aib_obj.onselection(dropdown.choice, null);
    else if (e.keyCode === 37 || e.keyCode === 38) {  // left|up
      if (this.option_highlighted > 0) {
        this.childNodes[this.option_highlighted].style.background = 'white';
        this.childNodes[this.option_highlighted].style.color = 'black';
        this.option_highlighted -= 1;
        this.childNodes[this.option_highlighted].style.background = 'darkblue';
        this.childNodes[this.option_highlighted].style.color = 'white';
        };
      }
    else if (e.keyCode === 39 || e.keyCode === 40) {  // right|down
      if (this.option_highlighted < (this.childNodes.length-1)) {
        this.childNodes[this.option_highlighted].style.background = 'white';
        this.childNodes[this.option_highlighted].style.color = 'black';
        this.option_highlighted += 1;
        this.childNodes[this.option_highlighted].style.background = 'darkblue';
        this.childNodes[this.option_highlighted].style.color = 'white';
        };
      }
    e.cancelBubble = true;  // prevent bubbling up to 'choice'
    return false;
    };

  if (navigator.appName === 'Opera')
    dropdown.onkeypress = dropdown.onkey
  else
    dropdown.onkeydown = dropdown.onkey;

  setTimeout(function() {dropdown.focus()}, 0);
  //return dropdown;
  };
AibChoice.prototype.onkey = function(choice, e) {
  if (!choice.amendable())
    return;
  if (e.keyCode === 32) {  // space
    choice.on_selection = this.after_selection;
    this.create_dropdown(choice);
    }
//  else if (e.keyCode === 13) {  // enter
//    this.onselection(choice, choice.ndx);
//    e.cancelBubble = true;
//    return false;
//    }
  else if ((e.keyCode === 37) || (e.keyCode === 38)) {  // left|up
    if (choice.ndx > 0) {
      this.after_selection(choice, choice.ndx-1)
      setTimeout(function() {choice.focus()}, 0);
      };
    }
  else if ((e.keyCode === 39) || (e.keyCode === 40)) {  // right|down
    if (choice.ndx < (choice.values.length-1)) {
      this.after_selection(choice, choice.ndx+1);
      setTimeout(function() {choice.focus()}, 0);
      };
    };
  };
if (navigator.appName === 'Opera') {
  AibChoice.prototype.onpresskey = AibChoice.prototype.onkey
  AibChoice.prototype.ondownkey = function(e) {return true};
  }
else {
  AibChoice.prototype.ondownkey = AibChoice.prototype.onkey;
  AibChoice.prototype.onpresskey = function(e) {return true};
  };
AibChoice.prototype.data_changed = function(choice) {
  var inp = choice.childNodes[0];
  if (inp.style.display === 'none')
    return false
  else
    return (choice.current_value !== choice.form_value);
  };
AibChoice.prototype.reset_value = function(choice) {
  var inp = choice.childNodes[0];
  var dsp = choice.childNodes[1];
  value = choice.form_value;
  pos = choice.data.indexOf(value);
  if (pos !== choice.ndx) {
    choice.ndx = pos;
    var dsp_value = choice.values[choice.ndx];
    if (inp.style.display === 'none')
      dsp.text.data = dsp_value;
    else
      inp.innerHTML = html_esc(dsp_value);
    choice.current_value = value;
    };
  };
AibChoice.prototype.get_value_for_server = function(choice) {
  //return choice.data[choice.current_value];
  if (choice.current_value === choice.form_value)
    return null;  // no change
  return choice.current_value;
  };
AibChoice.prototype.set_value_from_server = function(choice, value) {
  var inp = choice.childNodes[0];
  var dsp = choice.childNodes[1];

  choice.current_value = value;
  choice.ndx = choice.data.indexOf(value);
  var dsp_value = choice.values[choice.ndx];

  if (inp.style.display === 'none')
    dsp.text.data = dsp_value;
  else
    inp.innerHTML = html_esc(dsp_value);

/*
  // none of this is necessary, provided that we ensure that
  //   the server never sends an invalid value
  // the server inserts <none> at the top to represent
  //   a null value, so it should not happen

  pos = choice.data.indexOf(value);
  if (pos !== choice.ndx) {
    choice.ndx = pos;
    if (pos === -1) {
      choice.current_value = '';
      value = '';
      }
    else {
      choice.current_value = choice.data[pos];
      value = choice.values[pos]
      };
    choice.callback(choice.current_value);

    if (inp.style.display === 'none')
      dsp.text.data = value;
    else
      inp.innerHTML = html_esc(value);
    };
*/

  choice.form_value = value;
  choice.callback(choice.current_value);

  };
AibChoice.prototype.cell_data_changed = function(cell) {
  var grid = cell.grid;
  var subset_row = grid.first_grid_row - grid.first_subset_row + cell.grid_row;
  return cell.current_value !== grid.subset_data[subset_row][cell.grid_col];
  };
AibChoice.prototype.reset_cell_value = function(cell) {
  // this is copied from AibText - will have to be modified for AibChoice
  var grid = cell.grid;
  var subset_row = grid.first_grid_row - grid.first_subset_row + cell.grid_row;
  var value = grid.subset_data[subset_row][cell.grid_col];
  cell.current_value = value;
//  if (!(/\S/.test(value)))  // if cannot find a non-whitespace character
//    value = '\xa0';  // replace with &nbsp
  cell.text_node.data = value;
  };
AibChoice.prototype.set_cell_value_got_focus = function(cell) {
  };
AibChoice.prototype.set_cell_value_lost_focus = function(cell, value) {
  cell.current_value = value;
  pos = cell.input.data.indexOf(value);
  cell.pos = pos;
//  if (pos === -1)
//    value = '';
//  else
//    value = cell.input.values[pos];
  value = cell.input.values[pos];
//  if (!(/\S/.test(value)))  // if cannot find a non-whitespace character
//    value = '\xa0';  // replace with &nbsp
  cell.text_node.data = value;
  };
AibChoice.prototype.get_cell_value_for_server = function(cell) {
  if (!this.cell_data_changed(cell))
    return null;  // no change
  var value = cell.current_value;
//  if (value === '\xa0')
//    value = '';
  return value;
  };
AibChoice.prototype.grid_create_dropdown = function(cell) {
  choice = cell.input;
  if (!choice.amendable())
    return;
  cell.parentNode.appendChild(choice);
  choice.cell = cell;
  choice.ndx = cell.pos;
  if (choice.ndx === -1)
    choice.ndx = 0;
  choice.on_selection = this.grid_after_selection;
  this.create_dropdown(choice);
  };
AibChoice.prototype.grid_after_selection = function(choice, option_selected) {
  // to investigate -
  // 1. is grid_amended always true? what if no change?
  // 2. alternatively, could call start_edit
  //    slightly more consistent with (e.g.) backslash, and allows esc to reset
  var cell = choice.cell;
  if (option_selected !== null) {
    cell.current_value = choice.data[option_selected];
    cell.pos = option_selected;
    cell.text_node.data = choice.values[option_selected];
    cell.grid.set_amended(true);
    };
  setTimeout(function() {cell.grid.focus()}, 0);
  };

////////////////////
//  AibSpin       //
////////////////////
function AibSpin() {};
AibSpin.prototype = new AibCtrl();
AibSpin.prototype.after_got_focus = function(spin) {
  var inp = spin.childNodes[0];
  var dsp = spin.childNodes[1];
  if (!spin.amendable()) {
    dsp.style.border = '1px solid black';
    return;
    };
  inp.innerHTML = spin.current_value;
  };
AibSpin.prototype.before_lost_focus = function(spin) {
  return true;
  };
AibSpin.prototype.after_lost_focus = function(spin) {
  var inp = spin.childNodes[0];
  var dsp = spin.childNodes[1];
  if (!spin.amendable()) {
    dsp.style.border = '1px solid darkgrey';
    dsp.style.background = 'transparent';
    dsp.txt.style.background = '#f5f5f5';  // very light grey
    return;
    };
  dsp.text.data = spin.current_value;
  inp.style.display = 'none';
  dsp.style.display = 'block';
  spin.tabIndex = 0;
  };
AibSpin.prototype.change = function(spin, incr) {
  var inp = spin.childNodes[0];
  if (incr === 1) {
    if (spin.current_value < spin.max) {
      spin.current_value += 1;
      inp.innerHTML = spin.current_value;
      if (spin.callback !== null)
        spin.callback(spin.current_value);
      };
    }
  else if (incr === -1) {
    if (spin.current_value > spin.min) {
      spin.current_value -= 1;
      inp.innerHTML = spin.current_value;
      if (spin.callback !== null)
        spin.callback(spin.current_value);
      };
    };
  };
AibSpin.prototype.onkey = function(spin, e) {
  if (!e) e=window.event;
  if (e.keyCode === 38) {  // up
    this.change(spin, 1);
    setTimeout(function() {spin.focus()}, 0);
    }
  else if (e.keyCode === 40) {  // down
    this.change(spin, -1);
    setTimeout(function() {spin.focus()}, 0);
    };
  };
if (navigator.appName === 'Opera') {
  AibSpin.prototype.onpresskey = AibSpin.prototype.onkey
  AibSpin.prototype.ondownkey = function(e) {return true};
  }
else {
  AibSpin.prototype.ondownkey = AibSpin.prototype.onkey;
  AibSpin.prototype.onpresskey = function(e) {return true};
  };
//AibSpin.prototype.after_got_focus = function(spin) {
//  spin.parentNode.style.outline = '1px solid darkgrey';
//  };
//AibSpin.prototype.before_lost_focus = function(spin) {
//  return true;
//  };
//AibSpin.prototype.after_lost_focus = function(spin) {
//  spin.parentNode.style.outline = 'none';
//  };
AibSpin.prototype.data_changed = function(spin) {
  var inp = spin.childNodes[0];
  if (inp.style.display === 'none')
    return false
  else
    return (spin.current_value !== spin.form_value);
  };
AibSpin.prototype.reset_value = function(spin) {
  var inp = spin.childNodes[0];
  inp.innerHTML = spin.form_value;
  spin.current_value = spin.form_value;
  spin.focus();
  };
AibSpin.prototype.get_value_for_server = function(spin) {
  if (spin.current_value === spin.form_value)
    return null;  // no change
  return spin.current_value;
  };
AibSpin.prototype.set_value_from_server = function(spin, value) {
  var inp = spin.childNodes[0];
  var dsp = spin.childNodes[1];
  if (value !== spin.current_value) {
    if (value >= spin.min && value <= spin.max) {
      spin.current_value = value;
      if (dsp.style.display === 'none')
        inp.innerHTML = value;
      else
        dsp.text.data = value;
      };
    };
  spin.form_value = value;
  };

////////////////////
//  AibSxml       //
////////////////////
function AibSxml() {};
AibSxml.prototype = new AibCtrl();
AibSxml.prototype.got_focus = function(sxml) {
//  sxml.has_focus = true;
//  if (sxml.mouse_down)
//    return;  // will set focus from onclick()
//  got_focus(sxml);
  };
AibSxml.prototype.after_got_focus = function(sxml) {
  sxml.style.border = '1px solid black';
//  if (sxml.frame.form.focus_from_server)
  if (sxml.frame.err_flag)
    //sxml.className = 'error_background'
    sxml.style.background = sxml.bg_error;
  else if (!sxml.amendable())
    sxml.style.background = sxml.bg_disabled;
  else
    sxml.style.background = sxml.bg_focus;
  };
AibSxml.prototype.before_lost_focus = function(sxml) {
  sxml.current_value = sxml.value;
  return true;
  };
AibSxml.prototype.after_lost_focus = function(sxml) {
  sxml.style.background = sxml.bg_blur;
  sxml.style.border = '1px solid darkgrey';
  sxml.has_focus = false;
  };
//AibSxml.prototype.set_readonly = function(sxml, state) {
//  if (state) {
//    sxml.style.color = 'grey';
//    }
//  else {
//    sxml.style.color = null;  //'navy';
//    };
//  };
AibSxml.prototype.ondownkey = function(sxml, e) {
  if (e.keyCode === 13) {
    sxml.onclick(sxml);
    e.cancelBubble = true;
    return false;
    };
  };
AibSxml.prototype.onpresskey = function(sxml, e) {
  return true;
  };
AibSxml.prototype.popup = function(sxml) {
  sxml_popup(sxml);
//  var args = [sxml.ref];
//  send_request('sxml_checked', args);
//  sxml.frame.set_amended(true);
  };
AibSxml.prototype.data_changed = function(sxml) {
  return (sxml.current_value !== sxml.form_value);
  };
AibSxml.prototype.reset_value = function(sxml) {
  sxml.value = sxml.form_value;
  sxml.current_value = sxml.form_value;
  sxml.focus();
  };
AibSxml.prototype.get_value_for_server = function(sxml) {
  if (sxml.current_value === sxml.form_value)
    return null;  // no change
  return sxml.current_value;
  };
AibSxml.prototype.set_value_from_server = function(sxml, value) {
  if (value !== sxml.current_value) {
    sxml.current_value = value;
    sxml.value = value;
    };
  sxml.form_value = value;
  };
AibSxml.prototype.set_prev_from_server = function(sxml, value) {
  sxml.value = value;
  };
AibSxml.prototype.cell_data_changed = function(cell) {
  var grid = cell.grid;
  var subset_row = grid.first_grid_row - grid.first_subset_row + cell.grid_row;
  return cell.current_value !== grid.subset_data[subset_row][cell.grid_col];
  };
AibSxml.prototype.reset_cell_value = function(cell) {
  var grid = cell.grid;
  var subset_row = grid.first_grid_row - grid.first_subset_row + cell.grid_row;
  var value = grid.subset_data[subset_row][cell.grid_col];
  cell.value = cell.current_value = value;
  };
AibSxml.prototype.set_cell_value_got_focus = function(cell) {
  };
AibSxml.prototype.set_cell_value_lost_focus = function(cell, value) {
  cell.value = cell.current_value = value;
  };
AibSxml.prototype.get_cell_value_for_server = function(cell) {
  if (!this.cell_data_changed(cell))
    return null;  // no change
  return cell.current_value;
  };
AibSxml.prototype.grid_popup = function(cell, row) {
  cell.value = cell.current_value;
  cell.callback = [this, this.grid_popup_callback, cell, row];
  sxml_popup(cell);
//  var grid = cell.grid;
//  var args = [cell.input.ref, row];
//  send_request('cell_sxml_checked', args);
//  grid.set_amended(true);
  };
AibSxml.prototype.grid_popup_callback = function(cell, row) {
  cell.current_value = cell.value;
  cell.grid.set_amended(true);
  };

////////////////////
//  AibDummy      //
////////////////////
function AibDummy() {};
AibDummy.prototype = new AibCtrl();
AibDummy.prototype.got_focus = function(dummy) {
  if (dummy.frame.form.err_flag)
    dummy.frame.form.tabdir = -1;  // dummy failed vld, set focus on prev field
  got_focus(dummy);
  };
AibDummy.prototype.after_got_focus = function(dummy) {
//  if (dummy.frame.amended())
//    callbacks.push([this, this.go_to_next, dummy]);
//  else {
//    that = this;
//    setTimeout(function() {that.go_to_next(dummy)}, 0);
//    };
//  };
//AibDummy.prototype.go_to_next = function(dummy) {
  if (dummy.frame.form.current_focus !== dummy ||
      dummy.frame.form.setting_focus !== dummy)
    return;  // focus reset by server
  var pos = dummy.pos + dummy.frame.form.tabdir;  // tab = 1, shift+tab = -1
  var obj = dummy.frame.obj_list[pos]
  while (dummy.frame.obj_list[pos].offsetHeight === 0)
    pos += dummy.frame.form.tabdir;  // look for next available object
  dummy.frame.obj_list[pos].focus();
  };
AibDummy.prototype.before_lost_focus = function(dummy) {
  return true;
  };
AibDummy.prototype.after_lost_focus = function(dummy) {
  };
AibDummy.prototype.ondownkey = function(dummy, e) {
  return true;
  };
AibDummy.prototype.onpresskey = function(dummy, e) {
  return true;
  };
AibDummy.prototype.data_changed = function(dummy) {
  return false;
  };
AibDummy.prototype.reset_value = function(dummy) {
  };
AibDummy.prototype.get_value_for_server = function(dummy) {
  return null;  // no change
  };
AibDummy.prototype.set_value_from_server = function(dummy, value) {
  };
