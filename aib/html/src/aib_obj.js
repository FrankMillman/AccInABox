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
  if (!ctrl.amendable())
    ctrl.className = 'readonly_background'
  else if (ctrl.frame.err_flag)
    ctrl.className = 'error_background'
  else
    ctrl.className = 'focus_background';

  // next line was removed in 0.1.7, replaced in 0.1.9
  // latest version of Chrome requires it [2015-07-30]
  ctrl.focus();
  //got_focus(ctrl);
  };
AibCtrl.prototype.set_cell_value_from_server = function(grid, row, col, value) {
  // update subset_data if row is in subset
  if (row >= grid.first_subset_row && row < (grid.first_subset_row+grid.subset_data.length)) {
    var subset_row = row - grid.first_subset_row;
    grid.subset_data[subset_row][col] = value;
    };
  // update cell if row is visible
  if (row >= grid.first_grid_row && row < (grid.first_grid_row+grid.num_grid_rows)) {
    var cell = grid.grid_rows[row-grid.first_grid_row].grid_cols[col];
    cell.aib_obj.set_cell_value_lost_focus(cell, value);
    };
  };

////////////////////
//  AibText       //
////////////////////
function AibText() {};
AibText.prototype = new AibCtrl();
AibText.prototype.type = 'text';
AibText.prototype.after_got_focus = function(text) {
  if (!text.amendable()) {
    setInsertionPoint(text, 0);
    return;
    };
  if (text.multi_line === true) {
    text.scrollTop = 0;
    setInsertionPoint(text, 0);
    }
  else
    setInsertionPoint(text, 0, text.value.length);
  };
AibText.prototype.set_dflt_val = function(text, value) {
  text.value = value;
  if (text.multi_line === true) {
    text.scrollTop = 0;
    setInsertionPoint(text, 0);
    }
  else
  setInsertionPoint(text, 0, text.value.length);
};
AibText.prototype.before_lost_focus = function(text) {
  if (text.multi_line === true)
    // IE8 converts all \n to \r\n
    // this converts it back again!
    text.current_value = text.value.replace(/(\r\n|\n|\r)/gm, '\n');
  else
    text.current_value = text.value;
  return true;
  };
AibText.prototype.after_lost_focus = function(text) {
  if (text.multi_line === true)
    text.scrollTop = 0;
  text.scrollLeft = 0;
  text.className = 'blur_background';
  };
AibText.prototype.ondownkey = function(text, e) {
  return true;
  };
AibText.prototype.data_changed = function(text) {
  return (text.value !== text.form_value);
  };
AibText.prototype.reset_value = function(text) {
  text.value = text.form_value;
  text.current_value = text.form_value;
  text.focus();
  };
AibText.prototype.get_value_for_server = function(text) {
  if ((text.current_value === text.form_value) && (text.password === ''))
    return null;  // no change
  var value = text.current_value;
  if (text.password !== '') {
    text.form_value = value;  // save it now - no redisplay
    var pwd = value;
    value = '';
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
    text.value = value;
    };
  text.form_value = value;
  };
AibText.prototype.set_prev_from_server = function(text, value) {
    text.value = value;
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
  cell.current_value = value;
  };
AibText.prototype.set_cell_value_lost_focus = function(cell, value) {
  cell.current_value = value;  // save for 'got_focus' and 'edit_cell'
  if (cell.input.choices)
    value = cell.input.choice_values[cell.input.choice_data.indexOf(value)];
  // added next two lines [2017-11-15]
  // without it, replacing a non-empty string with an empty string leaves
  //   the original value still visible
  if (!(/\S/.test(value)))  // if cannot find a non-whitespace character
    value = '\xa0';  // replace with &nbsp
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
    var pwd = value;
    value = '';
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
AibText.prototype.start_edit = function(input, current_value, key) {  // called from grid
  if (key === null)  // user pressed F2 or double-clicked
    input.value = current_value;
  else {
    input.value = key;
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
AibNum.prototype.type = 'num';
AibNum.prototype.after_got_focus = function(num) {
  if (!num.amendable()) {  // reset in case set_dflt, retain display format
    num.value = this.num_to_string(num, num.current_value);
    return;
    }
  num.value = num.current_value;  // reset from display format to input format
  setInsertionPoint(num, 0, num.value.length);
  };
AibNum.prototype.set_dflt_val = function(num, value) {
  num.value = value;
  setInsertionPoint(num, 0, num.value.length);
  };
AibNum.prototype.before_lost_focus = function(num) {
  if (!num.amendable())
    return true;
  num.current_value = num.value;
  return true;
  };
AibNum.prototype.after_lost_focus = function(num) {
  num.className = 'blur_background';
  var value = num.current_value;
  num.value = this.num_to_string(num, value);
  };
AibNum.prototype.num_to_string = function(num, value) {
  if (value === '')
    ;  // no-op
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
  if (e.key.length > 1)  // control key
    return true;
  return this.validate_chr(num, e.key);
};
AibNum.prototype.validate_chr = function(num, key) {
  if ('0123456789'.includes(key)) {
    var decimal_pos = num.value.indexOf('.');
    if (decimal_pos === -1)  // no decimal point present
      return true;
    if (num.integer)
      return false;  // decimal point not allowed
    if (getCaret(num) <= decimal_pos)
      return true;  // cursor is before decimal point - ok
    var no_decimals = num.value.length - decimal_pos - 1;
    if (no_decimals === num.max_decimals)
      return false;
    return true;
    };
  if (
      key === '-' &&
      num.value.indexOf('-') === -1 &&  // the only one
      getCaret(num) === 0  // at the beginning
      )
    return true;
  if (
      key === '.' &&
      !num.integer &&  // not an 'integer' type
      num.value.indexOf('.') === -1  // the only one
      )
    return true;
  return false;
  };
AibNum.prototype.data_changed = function(num) {
  return (num.value !== num.form_value);
  };
AibNum.prototype.reset_value = function(num) {
  var value = num.form_value;
  num.current_value = value;
  num.value = value;
  num.focus();
  };
AibNum.prototype.get_value_for_server = function(num) {
  if (num.current_value === num.form_value)
    return null;  // no change
  return num.current_value;
  };
AibNum.prototype.set_value_from_server = function(num, value) {
  if (value !== num.current_value) {
    num.current_value = value;
    if (num.frame.form.current_focus === num)
      num.value = value;
    else
      num.value = this.num_to_string(num, value);
    };
  num.form_value = value
  };
AibNum.prototype.set_prev_from_server = function(num, value) {
   num.value = value;
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
  var value = num.value;
  num.current_value = value;
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
  cell.current_value = value;
  };
AibNum.prototype.set_cell_value_lost_focus = function(cell, value) {
  cell.current_value = value;  // save for 'got_focus' and 'edit_cell'
  value = this.num_to_string(cell.input, value);
  if (!(/\S/.test(value)))  // if cannot find a non-whitespace character
    value = '\xa0';  // replace with &nbsp
  cell.text_node.data = value;
  };
AibNum.prototype.get_cell_value_for_server = function(cell) {
  if (!this.cell_data_changed(cell))
    return null;  // no change
  return cell.current_value;
  };
AibNum.prototype.start_edit = function(input, current_value, key) {  // called from grid
  if (key === null)  // user pressed F2 or double-clicked
    input.value = current_value;
  else {
    input.value = '';
    if (this.validate_chr(input, key))
      input.value = key;
    };
  setInsertionPoint(input, input.value.length);
  };
AibNum.prototype.convert_prev_cell_value = function(cell, prev_value) {
//  if (!(/\S/.test(prev_value)))  // if cannot find a non-whitespace character
//    prev_value = '\xa0';  // replace with &nbsp
  return prev_value;
  };

////////////////////
//  AibDate       //
////////////////////
function AibDate() {};
AibDate.prototype = new AibCtrl();
AibDate.prototype.type = 'date';
AibDate.prototype.after_got_focus = function(date) {
  if (!date.amendable()) {
    setInsertionPoint(date, 0, 0);
    return;
    };
  if (date.valid) {
    date.value = this.date_to_string(date, date.current_value, date.input_format);
    date.pos = 0;  //date.blank.length;
    setInsertionPoint(date, 0, date.blank.length);
    date.selected = true;
    }
  else  // returning from failed validation - leave string untouched
    date.pos = 0;
  };
AibDate.prototype.set_dflt_val = function(date, value) {
  date.value = this.date_to_string(date, value, date.input_format);
  setInsertionPoint(date, 0, date.value.length);
  };
AibDate.prototype.before_lost_focus = function(date) {
  if (!date.amendable())
    return true;
  date.valid = true;
  var errmsg = this.validate_string(date);  // sets up current_value if ok
  if (errmsg !== '') {
    date.valid = false;
    date.focus();
    //show_errmsg('Date', errmsg);
    setTimeout(function() {show_errmsg('Date', errmsg)}, 0);
    return false;
    };
  return true;
  };
AibDate.prototype.after_lost_focus = function(date) {
  date.value = this.date_to_string(date, date.current_value, date.display_format);
  date.className = 'blur_background';
  };
AibDate.prototype.validate_string = function(date) {
  if (date.value === date.blank | date.value === '') {
    date.current_value = '';
    return '';  // no error
    };
  var today = new Date();
  var year, month, day;
  if (!date.yr_pos.length)
    year = today.getFullYear()
  else {
    year = date.value.substr(date.yr_pos[0], date.yr_pos[1]);
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
    month = date.value.substr(date.mth_pos[0], date.mth_pos[1]);
    month = month.replace(/ /g, '')  // strip spaces
    if (!month.length)
      month = today.getMonth()+1
    }
  if (!date.day_pos.length)
    day = today.getDate()
  else
    day = date.value.substr(date.day_pos[0], date.day_pos[1]);
  // use string values to construct new date
  var new_date = new Date(year, month-1, day);
  if (new_date.getDate() !== +day) {
    return '"' + day + '" - Invalid day!';
    };
  if (new_date.getMonth()+1 !== +month) {
    return '"' + month + '" - Invalid month!';
    };
  if (new_date.getFullYear() !== +year) {
    return '"' + year + '" - Invalid year!';
    };
  //date.current_value = new_date;
  date.current_value = new_date.getFullYear() + '-' +
    zfill(new_date.getMonth()+1, 2) + '-' + zfill(new_date.getDate(), 2);
  return '';  // no error
  };
AibDate.prototype.string_to_date = function(date) {
  if (date.value === date.blank | date.value === '') {
    return '';
    };
  year = date.value.substr(date.yr_pos[0], date.yr_pos[1]);
  month = date.value.substr(date.mth_pos[0], date.mth_pos[1]);
  day = date.value.substr(date.day_pos[0], date.day_pos[1]);
  return year + '-' + month + '-' + day;
  };
AibDate.prototype.date_to_string = function(date, value, format) {
  var output = '';
  if (value === '' || value === '\xa0')
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
  // use date.value, not date.current_value, to pick up dflt_val if set
  // show_cal(date, date.current_value, this.after_cal);
  show_cal(date, this.string_to_date(date), this.after_cal);
  date.selected = false;
  };
AibDate.prototype.after_cal = function(date, new_date) {
  if (new_date != null) {  // else keep old date
    date.current_value = new_date;
    AibDate.prototype.after_got_focus(date);
    };
  setTimeout(function() {date.focus()}, 0);
  };
AibDate.prototype.handle_bs = function(date) {
  if (date.pos > 0) {

    while (this.test_literal(date, date.pos-1))
      date.pos -= 1;
    date.pos -= 1;
    date.value =
      date.value.substring(0, date.pos) + ' ' +
      date.value.substring(date.pos+1);

    };
  date.selected = false;
  };
AibDate.prototype.handle_del = function(date) {
  if (!this.test_literal(date, date.pos))
    date.value =
      date.value.substring(0, date.pos) + ' ' +
      date.value.substring(date.pos+1);
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
AibDate.prototype.handle_digit = function(date, digit) {
  if (date.selected) {
    date.value = date.blank;
    date.pos = 0;
    date.selected = false;
    };
  date.value = date.value.substring(0, date.pos) + digit + date.value.substring(date.pos+1);
  date.pos += 1;
  while (this.test_literal(date, date.pos))
    date.pos += 1;
  };
AibDate.prototype.ondownkey = function(date, e) {
  if ([' ', 'Tab', 'Escape', 'Enter', '\\'].includes(e.key))
    return true;
  if (e.ctrlKey || e.altKey)
    return true;
  if (!date.amendable())
    return false;
  if (e.key === 'Backspace') this.handle_bs(date)
  else if (e.key === 'Delete') this.handle_del(date)
  else if (e.key === 'ArrowLeft') this.handle_left(date)
  else if (e.key === 'ArrowRight') this.handle_right(date)
  else if (e.key === 'Home') this.handle_home(date)
  else if (e.key === 'End') this.handle_end(date)
  else if ('0123456789'.includes(e.key)) this.handle_digit(date, e.key)
  setInsertionPoint(date, date.pos);
  e.cancelBubble = true;
  return false;
  };
//AibDate.prototype.data_changed = function(date, value) {
//  return (value !== this.date_to_string(date, date.form_value, date.input_format));
//  };
AibDate.prototype.data_changed = function(date) {
  return (date.value !== this.date_to_string(date, date.form_value, date.input_format));
  };
AibDate.prototype.reset_value = function(date) {
  date.value = this.date_to_string(date, date.form_value, date.input_format);
  date.current_value = date.form_value;
  date.pos = 0;
  setInsertionPoint(date, 0);
  date.focus();
  };
AibDate.prototype.get_value_for_server = function(date) {
  if (date.current_value === date.form_value)
    return null;  // no change
  var value = date.current_value;
  return value;
  };
AibDate.prototype.set_value_from_server = function(date, value) {
  if (value === '') {
    date.current_value = '';
    date.value = '';
    }
  else {
    if (value !== date.current_value) {
      date.current_value = value;
      date.value = this.date_to_string(date, value, date.display_format);
      };
    };
  date.form_value = value;
  };
AibDate.prototype.set_prev_from_server = function(date, value) {
  if (value === '') {
    date.value = '';
    }
  else {
    if (value !== date.current_value) {
      date.value = this.date_to_string(date, value, date.input_format);
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

    var cell = date.cell;
    var grid = cell.grid;
    grid.focus_from_server = true;
    grid.err_flag = true;
    grid.cell_set_focus(cell.grid_row, cell.grid_col);

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
  cell.current_value = value;
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
  if (!(/\S/.test(value)))  // if cannot find a non-whitespace character
    value = '\xa0';  // replace with &nbsp
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
AibDate.prototype.start_edit = function(input, current_value, key) {  // called from grid
  var date = input;
  if (key === null) {  // user pressed F2 or double-clicked
    date.value = current_value;
    date.pos = date.blank.length;
    setInsertionPoint(date, date.pos);
    date.selected = true;
    }
  else {
    date.value = date.blank;
    date.selected = true;
    if (key === 'Backspace') this.handle_bs(date)
    else if (key === 'Delete') this.handle_del(date)
    else if (key === 'ArrowLeft') this.handle_left(date)
    else if (key === 'ArrowRight') this.handle_right(date)
    else if (key ==='Home' ) this.handle_home(date)
    else if (key === 'End') this.handle_end(date)
    else if ('0123456789'.includes(key)) this.handle_digit(date, key)
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
AibBool.prototype.type = 'bool';
AibBool.prototype.after_got_focus = function(bool) {
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
  bool.value = value;
  bool.current_value = value;
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
  // bool.style.border = '1px solid black';
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
  if (e.key === ' ')
    this.chkbox_change(bool);
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

  if (!bool.frame.form.internal) {
    var args = [bool.ref, bool.value];
    send_request('cb_checked', args);
    };
  bool.frame.set_amended(true);
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
  if (bool.value === '1')
    this.draw_chk(bool);
  else
    this.draw_unchk(bool);
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
    bool.value = value;
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
    bool.value = value;
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

////////////////////
//  AibChoice     //
////////////////////
function AibChoice() {};
AibChoice.prototype = new AibCtrl();
AibChoice.prototype.type = 'choice';
AibChoice.prototype.after_got_focus = function(choice) {
  if (!choice.amendable())
    return
  if (choice.value === '') {
    choice.value = choice.data[0];
    choice.ndx = 0;
    choice.callback(choice.value);
    };
  choice.innerHTML = html_esc(choice.values[choice.ndx]);
  };
AibChoice.prototype.setup_choices = function(choice, choices) {
  choice.data = [];
  choice.values = [];
  for (var key in choices) {
    var value = choices[key];
    if (typeof(key) === 'number')
      debug3('got number');
    if (typeof(key) === 'number')
      key += '';
    choice.data.push(key);
    choice.values.push(value)
    };
  choice.value = choice.data[0];
  choice.ndx = 0;
  choice.callback(choice.value);
  choice.innerHTML = html_esc(choice.values[choice.ndx]);
  };
AibChoice.prototype.set_dflt_val = function(choice, value) {
  if (typeof(value) === 'number')
    debug3('got number');
  if (typeof(value) === 'number')
    value += '';
  if (value === '')
    value = choice.data[0];
  choice.value = value;
  choice.ndx = choice.data.indexOf(value);
  var dsp_value = choice.values[choice.ndx];
  choice.innerHTML = html_esc(dsp_value);
  choice.callback(choice.value);

  };
AibChoice.prototype.before_lost_focus = function(choice) {
  choice.current_value = choice.value;
  return true;
  };
AibChoice.prototype.after_lost_focus = function(choice) {
  choice.className = 'blur_background';
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
    choice.value = choice.data[option_selected];
    choice.current_value = choice.value
    choice.ndx = option_selected;
    choice.innerHTML = html_esc(choice.values[option_selected]);
    choice.callback(choice.value);

    // do we need this? [2019-08-15]
    // it triggers a validation on the server, which sets the object to 'dirty'
    // if we remove it, validation is triggered when we tab off
    // any implications?
    // if (!choice.frame.form.internal) {
    //   var args = [choice.ref, choice.current_value];
    //   send_request('choice_selected', args);
    //   };

    };
  setTimeout(function() {choice.focus()}, 0);
  };
AibChoice.prototype.create_dropdown = function(choice) {
  var dropdown = document.createElement('div');
  choice.appendChild(dropdown);
  dropdown.choice = choice;
  choice.dropdown = dropdown;
  dropdown.tabIndex = 0;
  dropdown.style.position = 'fixed';
  dropdown.style.background = 'white';
  dropdown.style.border = '1px solid grey';
  dropdown.style.paddingTop = '5px';;
  dropdown.style.paddingBottom = '5px';
  dropdown.clicked = null;
  dropdown.id = '$drop';
  dropdown.top_row = 0;

  dropdown.onclick = function() {
    var parent = document.getElementById('$drop').choice;
    parent.aib_obj.onselection(parent, parent.dropdown.clicked)
    };

  if (document.attachEvent)
    document.attachEvent('onclick', dropdown.onclick);
  else if (document.addEventListener)
    document.addEventListener('click', dropdown.onclick, false);

  if (choice.data.length > 15)
    var max_rows = 15
  else
    var max_rows = choice.data.length;

  for (var i=0; i<max_rows; i++) {
    var row = document.createElement('div');
    row.pos = i;
    row.style.paddingLeft = '10px';;
    row.style.paddingRight = '10px';
    row.style.width = 'auto';
    row.style.cursor = 'default';
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
      dropdown.clicked = this.pos + dropdown.top_row;
      };

    dropdown.appendChild(row);
    };

  dropdown.draw_window = function() {
    for (i=0; i<max_rows; i++) {
      var row = dropdown.childNodes[i];
      row.innerHTML = html_esc(choice.values[i + dropdown.top_row]);
      if (i + dropdown.top_row === dropdown.option_highlighted) {
        row.style.background = 'darkblue';
        row.style.color = 'white';
        };
      };
    };

  dropdown.option_highlighted = choice.ndx;
  if (choice.ndx > 3)
    dropdown.top_row = choice.ndx - 3
  else
    dropdown.top_row = 0;
  if (choice.data.length - dropdown.top_row < max_rows)
    dropdown.top_row = choice.data.length - max_rows;
  dropdown.draw_window();

  var choice_pos = find_pos(choice.parentNode);
  dropdown.style.left = (choice_pos[0]) + 'px';
  dropdown.style.top = (choice_pos[1] + 23) + 'px';
  dropdown.style.width = 'auto';
  dropdown.style.height = 'auto';

  if (dropdown.offsetWidth < (choice.offsetWidth+22))
    dropdown.style.width = (choice.offsetWidth+22) + 'px';

  if ((dropdown.offsetHeight + choice_pos[1] + 23) > max_h)
    dropdown.style.top = (max_h - dropdown.offsetHeight) + 'px';

  dropdown.onkey = function(e) {
    debug4('op');  // workaround for Opera
    if (e.ctrlKey || e.altKey) return;
    if ((e.key === 'Enter') || (e.key === ' '))
      dropdown.choice.aib_obj.onselection(dropdown.choice, this.option_highlighted);
    else if (e.key === 'Escape')
      dropdown.choice.aib_obj.onselection(dropdown.choice, null);
    else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
      var row = this.option_highlighted - this.top_row;
      if (row > 0) {
        this.childNodes[row].style.background = 'white';
        this.childNodes[row].style.color = 'black';
        row -= 1;
        this.option_highlighted -= 1;
        this.childNodes[row].style.background = 'darkblue';
        this.childNodes[row].style.color = 'white';
        }
      else if (this.option_highlighted > 0) {
        this.option_highlighted -= 1;
        this.top_row -= 1;
        this.draw_window();
        };
      }
    else if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
      var row = this.option_highlighted - this.top_row;
      if (row < (max_rows-1)) {
        this.childNodes[row].style.background = 'white';
        this.childNodes[row].style.color = 'black';
        row += 1;
        this.option_highlighted += 1;
        this.childNodes[row].style.background = 'darkblue';
        this.childNodes[row].style.color = 'white';
        }
      else if (this.option_highlighted < (choice.data.length-1)) {
        this.option_highlighted += 1;
        this.top_row += 1;
        this.draw_window();
        };
      };
    e.cancelBubble = true;  // prevent bubbling up to 'choice'
    return false;
    };

  if (navigator.appName === 'Opera')
    dropdown.onkeypress = dropdown.onkey
  else
    dropdown.onkeydown = dropdown.onkey;

  setTimeout(function() {dropdown.focus()}, 0);
  };
AibChoice.prototype.ondownkey = function(choice, e) {
  if (!e) e=window.event;
  if (e.ctrlKey || e.altKey)
    return;
  if (!choice.amendable())
    return;
  if (e.key === ' ') {
    choice.on_selection = this.after_selection;
    this.create_dropdown(choice);
    }
  else if ((e.key === 'ArrowLeft') || (e.key === 'ArrowUp')) {
    if (choice.ndx > 0) {
      this.after_selection(choice, choice.ndx-1)
      };
    }
  else if ((e.key === 'ArrowRight') || (e.key === 'ArrowDown')) {
    if (choice.ndx < (choice.values.length-1)) {
      this.after_selection(choice, choice.ndx+1);
      };
    };
  };
AibChoice.prototype.data_changed = function(choice) {
  value = choice.form_value;
  if (value === '')
    value = choice.data[0];
  return (choice.current_value !== value);
  };
AibChoice.prototype.reset_value = function(choice) {
  value = choice.form_value;
  if (value === '')
    value = choice.data[0];
  pos = choice.data.indexOf(value);
  if (pos !== choice.ndx) {
    choice.ndx = pos;
    var dsp_value = choice.values[choice.ndx];
    choice.innerHTML = html_esc(dsp_value);
    choice.value = value;
    choice.current_value = value;
    choice.callback(choice.current_value);
    };
  };
AibChoice.prototype.get_value_for_server = function(choice) {
  if (choice.current_value === choice.form_value)
    return null;  // no change
  return choice.current_value;
  };
AibChoice.prototype.set_value_from_server = function(choice, value) {
  if (typeof(value) === 'number')
    value += '';
  choice.form_value = value;  // set this before adjusting for ''
  // choice.current_value = value;
  if (value === null)  // added 2022-10-02
    return;  // choice_data will also be null
  if (value === '')
    value = choice.data[0];
  choice.current_value = value;
  choice.value = value;
  choice.ndx = choice.data.indexOf(value);
  choice.innerHTML = html_esc(choice.values[choice.ndx]);
  choice.callback(choice.value);
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
  cell.text_node.data = value;
  };
AibChoice.prototype.set_cell_value_got_focus = function(cell) {
  };
AibChoice.prototype.set_cell_value_lost_focus = function(cell, value) {
  cell.current_value = value;
  if (value === '') {  // bottom 'blank' row
    cell.pos = -1;
    }
  else {
    pos = cell.input.data.indexOf(value);
    cell.pos = pos;
    value = cell.input.values[pos];
    }
  cell.text_node.data = value;
  };
AibChoice.prototype.get_cell_value_for_server = function(cell) {
  if (!this.cell_data_changed(cell))
    return null;  // no change
  var value = cell.current_value;
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
//  AibRadio     //
////////////////////
function AibRadio() {};
AibRadio.prototype = new AibCtrl();
AibRadio.prototype.type = 'radio';
AibRadio.prototype.after_got_focus = function(radio) {
//  if (radio.current_value === '')
//    this.onselection(radio, 0);
  };
AibRadio.prototype.set_dflt_val = function(radio, value) {
  var ndx = radio.data.indexOf(value);
  this.onselection(radio, ndx);
  };
AibRadio.prototype.before_lost_focus = function(radio) {
  radio.current_value = radio.value;
  return true;
  };
AibRadio.prototype.after_lost_focus = function(radio) {
  radio.className = 'blur_background';
  };
AibRadio.prototype.onselection = function(radio, option_selected) {
  radio.buttons[radio.ndx].checked = false;
  radio.ndx = option_selected;
  radio.buttons[radio.ndx].checked = true;
  radio.value = radio.data[option_selected];
  radio.current_value = radio.value;
  radio.callback(radio.value);
  };
AibRadio.prototype.ondownkey = function(radio, e) {
  if (!radio.amendable())
    return;
  if (e.ctrlKey || e.altKey)
    return;
  if (['Tab', 'Enter'].includes(e.key))
    return;
  switch (e.key) {
    case 'ArrowLeft':
      if (radio.ndx > 0)
        this.onselection(radio, radio.ndx-1);
      break;
    case 'ArrowRight':
      if (radio.ndx < (radio.buttons.length-1))
        this.onselection(radio, radio.ndx+1);
      break;
    default:
      return false;
    };
  };
AibRadio.prototype.data_changed = function(radio) {
  value = radio.form_value;
  if (value === '')
    value = radio.data[0];
  return (radio.current_value !== value);
  };
AibRadio.prototype.reset_value = function(radio) {
  value = radio.form_value;
  if (value === '')
    value = radio.data[0];
  pos = radio.data.indexOf(value);
  if (pos !== radio.ndx)
    this.onselection(radio, pos);
  };
AibRadio.prototype.get_value_for_server = function(radio) {
  if (radio.current_value === radio.form_value)
    return null;  // no change
  return radio.current_value;
  };
AibRadio.prototype.set_value_from_server = function(radio, value) {
  radio.form_value = value;  // set this before adjusting for ''
  if (value === '')
    value = radio.data[0];
  if (value !== radio.current_value) {
    // if (value === '')
    //   value = radio.data[0];
    radio.current_value = value;
    radio.value = value;
    var ndx = radio.data.indexOf(value);
    this.onselection(radio, ndx);
    };
  };

////////////////////
//  AibSpin       //
////////////////////
function AibSpin() {};
AibSpin.prototype = new AibCtrl();
AibSpin.prototype.type = 'spin';
AibSpin.prototype.after_got_focus = function(spin) {
  if (spin.amendable())  // why?
    spin.innerHTML = spin.current_value;
  };
AibSpin.prototype.before_lost_focus = function(spin) {
  return true;
  };
AibSpin.prototype.after_lost_focus = function(spin) {
  spin.className = 'blur_background';
  };
AibSpin.prototype.change = function(spin, incr) {
  if (incr === 1) {
    if (spin.current_value < spin.max) {
      spin.current_value += 1;
      spin.innerHTML = spin.current_value;
      if (spin.callback !== null)
        spin.callback(spin.current_value);
      };
    }
  else if (incr === -1) {
    if (spin.current_value > spin.min) {
      spin.current_value -= 1;
      spin.innerHTML = spin.current_value;
      if (spin.callback !== null)
        spin.callback(spin.current_value);
      };
    };
  };
AibSpin.prototype.ondownkey = function(spin, e) {
  if (!e) e=window.event;
  if (e.key === 'ArrowUp') {
    this.change(spin, 1);
    setTimeout(function() {spin.focus()}, 0);
    }
  else if (e.key === 'ArrowDown') {
    this.change(spin, -1);
    setTimeout(function() {spin.focus()}, 0);
    };
  };
AibSpin.prototype.data_changed = function(spin) {
  return (spin.current_value !== spin.form_value);
  };
AibSpin.prototype.reset_value = function(spin) {
  spin.innerHTML = spin.form_value;
  spin.current_value = spin.form_value;
  spin.focus();
  };
AibSpin.prototype.get_value_for_server = function(spin) {
  if (spin.current_value === spin.form_value)
    return null;  // no change
  return spin.current_value;
  };
AibSpin.prototype.set_value_from_server = function(spin, value) {
  if (value !== spin.current_value) {
    if (value >= spin.min && value <= spin.max) {
      spin.current_value = value;
     spin.innerHTML = value;
      };
    };
  spin.form_value = value;
  };

////////////////////
//  AibSxml       //
////////////////////
function AibSxml() {};
AibSxml.prototype = new AibCtrl();
AibSxml.prototype.type = 'sxml';
AibSxml.prototype.after_got_focus = function(sxml) {
  sxml.style.border = '1px solid black';
  if (sxml.frame.err_flag)
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
  if (sxml.value.length === 1)
    sxml.style.fontWeight = 'normal';
  else
    sxml.style.fontWeight = 'bold';
};
AibSxml.prototype.ondownkey = function(sxml, e) {
  if (e.key === 'Enter') {
    sxml.onclick(sxml);
    e.cancelBubble = true;
    return false;
    };
  if ((e.key === 'ArrowLeft') || (e.key === 'ArrowUp'))
    var dir = -1
  else if ((e.key === 'ArrowRight') || (e.key === 'ArrowDown'))
    var dir = 1
  else
    return;
  var pos = sxml.pos + dir;
  if (pos < 0)
    pos = sxml.frame.obj_list.length-1
  else if (pos === sxml.frame.obj_list.length)
    pos = 0;
  sxml.frame.obj_list[pos].focus();
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
    if (sxml.value.length === 1)
    sxml.style.fontWeight = 'normal';
  else
    sxml.style.fontWeight = 'bold';
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
AibSxml.prototype.grid_popup = function(cell, input, row) {
  input.value = cell.current_value;
  input.callback = [this, this.grid_popup_callback, cell, input, row];
  sxml_popup(input);
//  var grid = cell.grid;
//  var args = [cell.input.ref, row];
//  send_request('cell_sxml_checked', args);
//  grid.set_amended(true);
  };
AibSxml.prototype.grid_popup_callback = function(cell, input, row) {
  if (input.value !== cell.current_value) {
    cell.current_value = input.value;
    cell.grid.set_amended(true);
    };
  };

////////////////////
//  AibDummy      //
////////////////////
function AibDummy() {};
AibDummy.prototype = new AibCtrl();
AibDummy.prototype.type = 'dummy';
AibDummy.prototype.after_got_focus = function(dummy) {
  if (!(dummy.frame.form.current_focus === dummy) &&
      !(dummy.frame.form.setting_focus === dummy))
    return;  // focus reset by server
  if (dummy.frame.err_flag)
    dummy.frame.form.tabdir = -1  // set focus on previous control
  var pos = dummy.pos + dummy.frame.form.tabdir;  // tab = 1, shift+tab = -1
  while (true) {
    var obj = dummy.frame.obj_list[pos];
    if ((obj.offsetHeight > 0 && !obj.display && !(obj.tabIndex === -1))
      || // or dummy obj, provided not on hidden notebook page
      (obj.dummy && (
        obj.nb_page === null ||
        obj.nb_page.pos === obj.nb_page.parentNode.current_pos
        )))
      break;
    pos += dummy.frame.form.tabdir;  // look for next available object
    };
  if (obj.dummy)
    got_focus(obj);
  else
    //obj.focus();
    // changed 2016-11-20
    // must allow dummy.focus() to complete before setting next focus
    // else 'current_focus' is not reset - see actions.got_focus()
    setTimeout(function() {obj.focus()}, 0);
  };
AibDummy.prototype.before_lost_focus = function(dummy) {
  return true;
  };
AibDummy.prototype.after_lost_focus = function(dummy) {
  };
AibDummy.prototype.ondownkey = function(dummy, e) {
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
